from dataclasses import dataclass
from typing import List

@dataclass
class HuiGroup:
    id: str
    name: str
    type: str # HuiType value
    amountPerShare: float
    commissionRate: float # Value of commission (could be % or absolute)
    totalMembers: int
    startDate: str
    status: str # HuiStatus value
    members: List[str] # Member IDs (can have duplicates for multi-slots)
    currentPeriod: int
    commissionType: str = 'PERCENT' # 'PERCENT' or 'FIXED'
    biddingRule: str = 'OPEN_BID' # BiddingRule value
    minBidStep: float = 10000 # Minimum bid increment
    maxBidLimit: float = 0 # Maximum bid allowed (0 = no limit)
    totalPeriods: int = 0 # Total expected periods (0 = auto from members)

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

    def to_dict(self):
        return self.__dict__
