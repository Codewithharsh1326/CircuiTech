from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict, Field


class BomItem(BaseModel):
    """A single line-item in a Bill of Materials."""

    model_config = ConfigDict(populate_by_name=True)

    part_number: str = Field(..., alias="partNumber", description="Manufacturer part number")
    manufacturer: str | None = Field(None, description="The manufacturer of the component")
    description: str = Field(..., description="Brief component description")
    quantity: int = Field(..., ge=1, description="Number of units required")
    estimated_cost: float = Field(
        ..., alias="estimatedCost", ge=0, description="Estimated unit cost in USD"
    )


class AgentResponse(BaseModel):
    """Conversational response and optional BOM returned by the bom_agent."""

    model_config = ConfigDict(populate_by_name=True)

    is_ready_for_bom: bool = Field(..., alias="isReadyForBom", description="True if the agent has enough technical constraints (power, size, connectivity) to build a precise BOM. False if it needs to ask the user clarifying questions.")
    reply: str = Field(..., description="The conversational message text sent to the user.")
    items: list[BomItem] | None = Field(None, description="List of BOM line-items, populated only if isReadyForBom is true")
    total_cost: float = Field(0.0, alias="totalCost", ge=0)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
