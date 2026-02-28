import json
import asyncio

from groq import AsyncGroq

from app.core.config import settings
from app.agents.exceptions import AgentException
from app.models.bom import BomItem, AgentResponse
from app.services.external_apis import search_digikey

EXTRACTION_PROMPT = """\
You are an expert embedded-systems architect.
Your job is to clarify the user's constraints or extract search queries for component sourcing.
If the user's constraints are vague (missing info about power supply, size, or connectivity requirements), set "isReadyForBom" to false and ask clarifying questions in the "reply" field. Do not generate search queries.
If you have enough constraints, set "isReadyForBom" to true, provide a brief architectural recommendation in "reply", and generate a list of "search_queries" to find the required components on DigiKey (e.g. "STM32WLE5 MCU", "10k 0402 resistor").

Given a design description, return a JSON object with this exact schema:
{
  "isReadyForBom": boolean,
  "reply": "string (conversational response to the user)",
  "search_queries": ["string"]
}
Return ONLY valid JSON.
"""

SYNTHESIS_PROMPT = """\
You are an expert embedded-systems BOM generator.
I will provide the user's request and the raw JSON results from a component database search.
Select the best components to form a complete Bill of Materials matching the constraints.

Return a JSON object with this exact schema:
{
  "items": [
    {
      "partNumber": "string",
      "manufacturer": "string",
      "description": "string",
      "quantity": integer (>= 1),
      "estimatedCost": number (>= 0, USD)
    }
  ]
}
Return ONLY valid JSON. Do not include markdown.
"""

_client = AsyncGroq(api_key=settings.groq_api_key)


async def run_bom_agent(user_prompt: str, history: list[dict] = [], context: dict | None = None) -> AgentResponse:
    """3-Step Agentic orchestration for sourcing a BOM."""
    
    # Step 1: Extraction
    messages = [{"role": "system", "content": EXTRACTION_PROMPT}]
    for msg in history:
        messages.append({"role": msg.get("role", "user"), "content": msg.get("content", "")})
    
    if context:
        messages.append({"role": "user", "content": json.dumps(context)})
        
    messages.append({"role": "user", "content": user_prompt})

    try:
        ext_response = await _client.chat.completions.create(
            model=settings.groq_default_model,
            messages=messages,
            response_format={"type": "json_object"},
            temperature=0.2,
        )
    except Exception as exc:
        raise AgentException("bom_agent", f"Groq Extraction failed: {exc}") from exc

    try:
        ext_data = json.loads(ext_response.choices[0].message.content)
    except Exception as exc:
        raise AgentException("bom_agent", f"Invalid extraction JSON: {exc}") from exc

    is_ready = ext_data.get("isReadyForBom", False)
    reply_msg = ext_data.get("reply", "")
    search_queries = ext_data.get("search_queries", [])

    if not is_ready or not search_queries:
        return AgentResponse(
            isReadyForBom=False,
            reply=reply_msg,
            items=None,
            totalCost=0.0
        )

    # Step 2: API Execution
    api_results = {}
    for query in search_queries:
        try:
            results = await search_digikey(query)
            api_results[query] = results
        except Exception as e:
            api_results[query] = {"error": str(e)}

    # Step 3: Synthesis
    synth_messages = [
        {"role": "system", "content": SYNTHESIS_PROMPT},
        {"role": "user", "content": f"User Request: {user_prompt}\n\nSearch Results:\n{json.dumps(api_results)}"}
    ]

    try:
        synth_response = await _client.chat.completions.create(
            model=settings.groq_default_model,
            messages=synth_messages,
            response_format={"type": "json_object"},
            temperature=0.2,
        )
    except Exception as exc:
        raise AgentException("bom_agent", f"Groq Synthesis failed: {exc}") from exc

    try:
        synth_data = json.loads(synth_response.choices[0].message.content)
    except Exception as exc:
        raise AgentException("bom_agent", f"Invalid synthesis JSON: {exc}") from exc

    items = synth_data.get("items", [])
    
    try:
        final_response = AgentResponse(
            isReadyForBom=True,
            reply=reply_msg,
            items=items,
            totalCost=0.0
        )
    except Exception as exc:
        raise AgentException("bom_agent", f"Response validation failed: {exc}") from exc

    if final_response.items:
        computed_total = sum(item.quantity * item.estimated_cost for item in final_response.items)
        final_response.total_cost = round(computed_total, 2)

    return final_response
