"""
Members Service - Producer
Emits events when data changes.
"""
from typing import List
from app.core.event_bus import get_event_bus, Event, EventType
from app.models.member import Member
from app.models.enums import MemberStatus
from services.finance_service import FinanceService
import time

class MembersService:
    """
    Service layer for Members (Producer).
    Emits events for all data changes.
    """
    
    def __init__(self, members: List[Member], groups, transactions):
        self.members = members
        self.groups = groups
        self.transactions = transactions
    
    def get_all(self) -> List[Member]:
        """Get all members."""
        return self.members
    
    def search(self, query: str) -> List[Member]:
        """Search members by name or phone."""
        query_lower = query.lower()
        results = [
            m for m in self.members
            if query_lower in m.name.lower() or query_lower in m.phone
        ]
        
        # Emit search event
        get_event_bus().publish(Event(
            type=EventType.MEMBER_SEARCH,
            data={'query': query, 'results_count': len(results)},
            source='MembersService'
        ))
        
        return results
    
    def create(self, name: str, phone: str, address: str, zalo: str, note: str, status: str) -> Member:
        """
        Create a new member.
        Emits MEMBER_CREATED event.
        """
        # Validation
        if not name or not phone:
            raise ValueError("Tên và số điện thoại là bắt buộc")
        
        if any(m.phone == phone for m in self.members):
            raise ValueError(f"Số điện thoại {phone} đã tồn tại")
        
        # Create
        new_member = Member(
            id=str(int(time.time())),
            name=name,
            phone=phone,
            address=address,
            joinDate=str(time.time()),
            zalo=zalo,
            note=note,
            status=status
        )
        
        self.members.append(new_member)
        
        # Emit event
        get_event_bus().publish(Event(
            type=EventType.MEMBER_CREATED,
            data=new_member,
            source='MembersService'
        ))
        
        return new_member
    
    def update(self, member: Member, name: str, phone: str, address: str, 
               zalo: str, note: str, status: str):
        """
        Update a member.
        Emits MEMBER_UPDATED event.
        """
        if not name or not phone:
            raise ValueError("Tên và số điện thoại là bắt buộc")
        
        if any(m.phone == phone and m.id != member.id for m in self.members):
            raise ValueError(f"Số điện thoại {phone} đã tồn tại")
        
        # Store old values for event
        old_data = member.to_dict()
        
        # Update
        member.name = name
        member.phone = phone
        member.address = address
        member.zalo = zalo
        member.note = note
        member.status = status
        
        # Emit event
        get_event_bus().publish(Event(
            type=EventType.MEMBER_UPDATED,
            data={'member': member, 'old_data': old_data},
            source='MembersService'
        ))
    
    def delete(self, member: Member):
        """
        Delete a member.
        Emits MEMBER_DELETED event.
        """
        # Check constraints
        active_groups = [g for g in self.groups if member.id in g.members and g.status == 'Đang chạy']
        if active_groups:
            raise ValueError(f"Không thể xóa: Thành viên đang tham gia {len(active_groups)} dây hụi")
        
        self.members.remove(member)
        
        # Emit event
        get_event_bus().publish(Event(
            type=EventType.MEMBER_DELETED,
            data=member,
            source='MembersService'
        ))
    
    def get_stats(self, member_id: str):
        """Get member statistics."""
        groups_in = [g for g in self.groups if member_id in g.members]
        collected = [t for t in self.transactions if t.memberId == member_id and t.type == 'COLLECT']
        total_debt = FinanceService.get_member_total_debt(member_id, self.groups, self.transactions)
        
        return {
            'num_groups': len(groups_in),
            'num_collected': len(collected),
            'total_debt': total_debt
        }
