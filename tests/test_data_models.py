import pytest
from data_models import Member, HuiGroup, MemberStatus, HuiType, HuiStatus, BiddingRule

# Arrange: Create test data for a member
MEMBER_DATA = {
    "id": "M001",
    "name": "Nguyen Van A",
    "phone": "0901234567",
    "address": "123 Duong ABC, Quan 1, TPHCM",
    "joinDate": "2023-01-15",
    "zalo": "zalo_A",
    "reputationScore": 100,
    "status": MemberStatus.NORMAL.value,
    "note": "Thanh vien moi"
}

def test_member_creation_from_dict():
    """
    Test case: Verify that a Member object can be created from a dictionary.
    """
    # Act
    member = Member.from_dict(MEMBER_DATA)

    # Assert
    assert member.id == MEMBER_DATA["id"]
    assert member.name == MEMBER_DATA["name"]
    assert member.reputationScore == 100

def test_member_conversion_to_dict():
    """
    Test case: Verify that a Member object can be converted to a dictionary.
    """
    # Arrange
    member = Member.from_dict(MEMBER_DATA)

    # Act
    member_dict = member.to_dict()

    # Assert
    assert member_dict == MEMBER_DATA

@pytest.mark.parametrize("status, expected", [
    (MemberStatus.NORMAL.value, False),
    (MemberStatus.TRUSTED.value, False),
    (MemberStatus.WATCHLIST.value, True),
    (MemberStatus.BLACKLIST.value, True),
])
def test_is_high_risk(status, expected):
    """
    Test case: Verify the business logic for identifying high-risk members.
    """
    # Arrange
    member_data = MEMBER_DATA.copy()
    member_data["status"] = status
    member = Member.from_dict(member_data)

    # Act
    result = member.is_high_risk()

    # Assert
    assert result == expected

@pytest.mark.parametrize("score, status, expected", [
    (95, MemberStatus.TRUSTED.value, True),
    (90, MemberStatus.TRUSTED.value, True),
    (89, MemberStatus.TRUSTED.value, False),
    (95, MemberStatus.NORMAL.value, False),
    (100, MemberStatus.WATCHLIST.value, False),
])
def test_is_trusted(score, status, expected):
    """
    Test case: Verify the business logic for identifying trusted members.
    """
    # Arrange
    member_data = MEMBER_DATA.copy()
    member_data["reputationScore"] = score
    member_data["status"] = status
    member = Member.from_dict(member_data)

    # Act
    result = member.is_trusted()

    # Assert
    assert result == expected

# Arrange: Create test data for a HuiGroup
HUI_GROUP_DATA = {
    "id": "H001",
    "name": "Hui Thang 5",
    "type": HuiType.MONTHLY.value,
    "amountPerShare": 1000000,
    "commissionRate": 0.05,
    "totalMembers": 10,
    "startDate": "2024-05-01",
    "status": HuiStatus.ACTIVE.value,
    "members": ["M001", "M002", "M003"],
    "currentPeriod": 1,
    "commissionType": "PERCENT",
    "biddingRule": BiddingRule.OPEN_BID.value,
    "minBidStep": 10000,
    "maxBidLimit": 500000,
    "totalPeriods": 12,
}

def test_hui_group_creation_from_dict():
    """
    Test case: Verify that a HuiGroup object can be created from a dictionary.
    """
    # Act
    hui_group = HuiGroup.from_dict(HUI_GROUP_DATA)

    # Assert
    assert hui_group.id == HUI_GROUP_DATA["id"]
    assert hui_group.name == HUI_GROUP_DATA["name"]
    assert hui_group.amountPerShare == 1000000

def test_hui_group_conversion_to_dict():
    """
    Test case: Verify that a HuiGroup object can be converted to a dictionary.
    """
    # Arrange
    hui_group = HuiGroup.from_dict(HUI_GROUP_DATA)

    # Act
    hui_group_dict = hui_group.to_dict()

    # Assert
    assert hui_group_dict == HUI_GROUP_DATA
