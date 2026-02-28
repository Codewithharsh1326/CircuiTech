from pydantic import BaseModel
from typing import List

class Connection(BaseModel):
    source_part: str
    source_pin: str
    target_part: str
    target_pin: str
    signal_type: str  # e.g., "I2C", "UART", "Power", "Ground"
    description: str  # e.g., "Main 3.3V supply to MCU"

class PinMap(BaseModel):
    connections: List[Connection]
