"""
Members Module - Presenter
Business logic coordinator between Model and View.
No direct UI code, only data manipulation and service calls.
"""
from typing import List, Callable
from app.models.member import Member, MemberStats, MemberStatus
from services.finance_service import FinanceService

class MembersPresenter:
    """
    Presenter for Members module.
    Handles all business logic and coordinates between services and view.
    """
    
    def __init__(self, members: List[Member], groups, transactions):
        self.members = members
        self.groups = groups
        self.transactions = transactions
        self._view = None
    
    def attach_view(self, view):
        """Attach the view to this presenter."""
        self._view = view
    
    def get_all_members(self) -> List[Member]:
        """Get all members."""
        return self.members
    
    def search_members(self, query: str) -> List[Member]:
        """
        Search members by name or phone.
        Business logic: case-insensitive search.
        """
        query_lower = query.lower()
        return [
            m for m in self.members
            if query_lower in m.name.lower() or query_lower in m.phone
        ]
    
    def get_member_stats(self, member_id: str) -> MemberStats:
        """
        Calculate statistics for a member.
        Business logic: aggregates data from multiple sources.
        """
        # Count groups
        groups_in = [g for g in self.groups if member_id in g.members]
        num_groups = len(groups_in)
        
        # Count collections
        collected = [t for t in self.transactions if t.memberId == member_id and t.type == 'COLLECT']
        num_collected = len(collected)
        
        # Calculate debt
        total_debt = FinanceService.get_member_total_debt(member_id, self.groups, self.transactions)
        
        return MemberStats(
            member_id=member_id,
            num_groups=num_groups,
            num_collected=num_collected,
            total_debt=total_debt
        )
    
    def create_member(self, name: str, phone: str, address: str, zalo: str, note: str, status: str) -> Member:
        """
        Create a new member.
        Business logic: validation and ID generation.
        """
        import time
        
        # Validation
        if not name or not phone:
            raise ValueError("Tên và số điện thoại là bắt buộc")
        
        # Check duplicate phone
        if any(m.phone == phone for m in self.members):
            raise ValueError(f"Số điện thoại {phone} đã tồn tại")
        
        # Create member
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
        return new_member
    
    def update_member(self, member: Member, name: str, phone: str, address: str, 
                     zalo: str, note: str, status: str):
        """
        Update an existing member.
        Business logic: validation and duplicate check.
        """
        if not name or not phone:
            raise ValueError("Tên và số điện thoại là bắt buộc")
        
        # Check duplicate phone (excluding current member)
        if any(m.phone == phone and m.id != member.id for m in self.members):
            raise ValueError(f"Số điện thoại {phone} đã tồn tại")
        
        member.name = name
        member.phone = phone
        member.address = address
        member.zalo = zalo
        member.note = note
        member.status = status
    
    def delete_member(self, member: Member) -> bool:
        """
        Delete a member.
        Business logic: check if member can be deleted.
        """
        # Check if member is in any active group
        active_groups = [g for g in self.groups if member.id in g.members and g.status == 'Đang chạy']
        if active_groups:
            raise ValueError(f"Không thể xóa: Thành viên đang tham gia {len(active_groups)} dây hụi")
        
        self.members.remove(member)
        return True
    
    def get_high_risk_members(self) -> List[Member]:
        """Get all high-risk members (Watchlist/Blacklist)."""
        return [m for m in self.members if m.is_high_risk()]
    
    def get_trusted_members(self) -> List[Member]:
        """Get all trusted members."""
        return [m for m in self.members if m.is_trusted()]
