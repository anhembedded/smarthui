from dataclasses import dataclass
from typing import Optional

@dataclass
class AuditLog:
    id: str
    timestamp: str
    action: str
    userId: str
    scenario: str
    stateBefore: dict
    inputParameters: dict
    resultCalculated: dict
    ai_context: Optional[dict] = None
    aiAnalysis: Optional[str] = None

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

    def to_dict(self):
        return self.__dict__
