import pytest
from app.models.member import Member
from app.models.enums import MemberStatus
from app.services.members_service import MembersService
from app.core.event_bus import get_event_bus, EventType

@pytest.fixture
def members_service():
    members = []
    groups = []
    transactions = []
    return MembersService(members, groups, transactions)

def test_member_risk_logic():
    """Test business rules in Member model."""
    member = Member(id="1", name="Test", phone="123", address="", joinDate="", status=MemberStatus.NORMAL.value)
    assert member.is_high_risk() is False
    
    member.status = MemberStatus.WATCHLIST.value
    assert member.is_high_risk() is True
    
    member.status = MemberStatus.BLACKLIST.value
    assert member.is_high_risk() is True

def test_member_service_create_emits_event(members_service):
    """Test that creating a member produces an event."""
    events = []
    def handler(event):
        events.append(event)
        
    get_event_bus().subscribe(EventType.MEMBER_CREATED, handler)
    
    # Act
    members_service.create(
        name="New Member",
        phone="0999888777",
        address="ABC",
        zalo="zalo",
        note="note",
        status=MemberStatus.NORMAL.value
    )
    
    # Assert
    assert len(members_service.get_all()) == 1
    assert len(events) == 1
    assert events[0].type == EventType.MEMBER_CREATED
    assert events[0].data.name == "New Member"
    
    # Cleanup
    get_event_bus().unsubscribe(EventType.MEMBER_CREATED, handler)

def test_member_service_search(members_service):
    """Test search logic in MembersService."""
    members_service.create("Anh", "111", "", "", "", MemberStatus.NORMAL.value)
    members_service.create("Em", "222", "", "", "", MemberStatus.NORMAL.value)
    
    results = members_service.search("Anh")
    assert len(results) == 1
    assert results[0].name == "Anh"
    
    results = members_service.search("222")
    assert len(results) == 1
    assert results[0].phone == "222"

def test_member_service_delete_constraint(members_service):
    """Test that member cannot be deleted if in active groups."""
    member = members_service.create("Test", "123", "", "", "", MemberStatus.NORMAL.value)
    
    # Mocking a group where member is active
    from app.models.hui_group import HuiGroup
    mock_group = HuiGroup(
        id="G1", name="Group", type="Tháng", amountPerShare=1000, 
        commissionRate=5, totalMembers=1, startDate="", 
        status="Đang chạy", members=[member.id], currentPeriod=1
    )
    members_service.groups.append(mock_group)
    
    with pytest.raises(ValueError, match="Không thể xóa"):
        members_service.delete(member)
