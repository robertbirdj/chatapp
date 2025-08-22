import dataclasses
from datetime import datetime

@dataclasses.dataclass
class Message:
    """Represents a single chat message."""
    id: int
    name: str
    timestamp: datetime
    content: str
