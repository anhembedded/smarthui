from dataclasses import dataclass, field
from typing import List
from app.models.member import Member
from app.models.hui_group import HuiGroup
from app.models.transaction import Transaction
from app.models.audit_log import AuditLog

@dataclass
class AppState:
    members: List[Member] = field(default_factory=list)
    groups: List[HuiGroup] = field(default_factory=list)
    transactions: List[Transaction] = field(default_factory=list)
    auditLogs: List[AuditLog] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data):
        return cls(
            members=[Member.from_dict(m) for m in data.get('members', [])],
            groups=[HuiGroup.from_dict(g) for g in data.get('groups', [])],
            transactions=[Transaction.from_dict(t) for t in data.get('transactions', [])],
            auditLogs=[AuditLog.from_dict(l) for l in data.get('auditLogs', [])]
        )

    def to_dict(self):
        return {
            'members': [m.to_dict() for m in self.members],
            'groups': [g.to_dict() for g in self.groups],
            'transactions': [t.to_dict() for t in self.transactions],
            'auditLogs': [l.to_dict() for l in self.auditLogs]
        }
