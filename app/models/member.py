from dataclasses import dataclass
from typing import Optional
from app.models.enums import MemberStatus

@dataclass
class Member:
    id: str
    name: str
    phone: str
    address: str
    joinDate: str
    zalo: Optional[str] = None
    reputationScore: int = 100
    status: str = MemberStatus.NORMAL.value
    note: Optional[str] = None

    @classmethod
    def from_dict(cls, data):
        return cls(**data)
    
    def to_dict(self):
        return self.__dict__

    def is_high_risk(self) -> bool:
        """Business rule: Check if member is high risk."""
        return self.status in [MemberStatus.WATCHLIST.value, MemberStatus.BLACKLIST.value]
    
    def is_trusted(self) -> bool:
        """Business rule: Check if member is trusted."""
        return self.reputationScore >= 90 and self.status == MemberStatus.TRUSTED.value
