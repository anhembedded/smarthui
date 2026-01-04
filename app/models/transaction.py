from dataclasses import dataclass
from typing import Optional

@dataclass
class Transaction:
    id: str
    huiGroupId: str
    memberId: str
    type: str  # 'CONTRIBUTE', 'COLLECT', 'PENALTY'
    amount: float
    date: str
    period: int
    bidAmount: Optional[float] = 0
    netAmount: Optional[float] = 0
    note: Optional[str] = None

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

    def to_dict(self):
        return self.__dict__
