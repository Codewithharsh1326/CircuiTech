import json

from groq import AsyncGroq

from app.core.config import settings
from app.agents.exceptions import AgentException
from app.models.bom import BomItem
from app.models.pinmap import PinMap

SYSTEM_PROMPT = """\
You are an expert Embedded Systems Hardware Integrator. 
I will provide you with a Bill of Materials (BOM) in JSON format. 
Your job is to generate a strict JSON netlist mapping the logical connections between these components. 
Ensure voltage levels match, required pull-up resistors for I2C are noted, and standard communication protocols (UART, SPI, I2C) are mapped to the correct pins based on standard datasheets.

Given the BOM, return a JSON object with this exact schema:
{
  "connections": [
    {
      "source_part": "string",
      "source_pin": "string",
      "target_part": "string",
      "target_pin": "string",
      "signal_type": "string",
      "description": "string"
    }
  ]
}
Return ONLY valid JSON. Do not include markdown fences or commentary.\
"""

_client = AsyncGroq(api_key=settings.groq_api_key)


async def run_pinmap_agent(bom_items: list[dict]) -> PinMap:
    """Send a BOM array to Groq and return a validated PinMap."""
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Generate a pin map for these components: {json.dumps(bom_items)}"}
    ]

    try:
        response = await _client.chat.completions.create(
            model=settings.groq_default_model, # llama-3.3-70b-versatile
            messages=messages,
            response_format={"type": "json_object"},
            temperature=0.2,
        )
    except Exception as exc:
        raise AgentException("pinmap_agent", f"Groq API call failed: {exc}") from exc

    raw = response.choices[0].message.content
    if not raw:
        raise AgentException("pinmap_agent", "Empty response from LLM.")

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise AgentException("pinmap_agent", f"LLM returned invalid JSON: {exc}") from exc

    # Validate against Pydantic models
    try:
        pinmap = PinMap.model_validate(data)
    except Exception as exc:
        raise AgentException("pinmap_agent", f"Response validation failed: {exc}") from exc

    return pinmap
