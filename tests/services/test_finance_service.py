import pytest
from data_models import HuiGroup, Transaction, Member, HuiType, HuiStatus, MemberStatus, BiddingRule
from services.finance_service import FinanceService

# --- Arrange: Reusable Test Data ---

@pytest.fixture
def sample_members():
    """Provides a list of sample members for tests."""
    return [
        Member(id="m1", name="Alice", phone="", address="", joinDate=""),
        Member(id="m2", name="Bob", phone="", address="", joinDate=""),
        Member(id="m3", name="Charlie", phone="", address="", joinDate=""),
        Member(id="m4", name="Diana", phone="", address="", joinDate=""),
    ]

@pytest.fixture
def active_hui_group():
    """Provides a standard, active Hui group."""
    return HuiGroup(
        id="g1",
        name="Test Hui",
        type=HuiType.MONTHLY.value,
        amountPerShare=1000000,
        commissionRate=5,  # 5%
        commissionType='PERCENT',
        totalMembers=4,
        startDate="2024-01-01",
        status=HuiStatus.ACTIVE.value,
        members=["m1", "m2", "m3", "m4"],  # 4 members, 1 slot each
        currentPeriod=3,
        biddingRule=BiddingRule.OPEN_BID.value
    )

@pytest.fixture
def sample_transactions():
    """Provides a history of transactions for periods 1 and 2."""
    return [
        # Period 1: m1 wins with a bid of 100k
        Transaction(id="t1", huiGroupId="g1", memberId="m1", type='COLLECT', amount=0, bidAmount=100000, period=1, date=""),
        Transaction(id="t2", huiGroupId="g1", memberId="m2", type='CONTRIBUTE', amount=900000, period=1, date=""), # 1M - 100k
        Transaction(id="t3", huiGroupId="g1", memberId="m3", type='CONTRIBUTE', amount=900000, period=1, date=""),
        Transaction(id="t4", huiGroupId="g1", memberId="m4", type='CONTRIBUTE', amount=900000, period=1, date=""),
        # Period 2: m2 wins with a bid of 150k
        Transaction(id="t5", huiGroupId="g1", memberId="m2", type='COLLECT', amount=0, bidAmount=150000, period=2, date=""),
        Transaction(id="t6", huiGroupId="g1", memberId="m1", type='CONTRIBUTE', amount=1000000, period=2, date=""), # m1 is dead, pays full
        Transaction(id="t7", huiGroupId="g1", memberId="m3", type='CONTRIBUTE', amount=850000, period=2, date=""), # 1M - 150k
        # m4 only pays 500k instead of 850k
        Transaction(id="t8", huiGroupId="g1", memberId="m4", type='CONTRIBUTE', amount=500000, period=2, date=""),
    ]

# --- Tests for calculate_payout ---

def test_calculate_payout_period_3(active_hui_group, sample_transactions):
    """
    Test case: Calculate payout for Period 3.
    - Previous winners (dead): m1, m2
    - Live members (excluding winner): m4
    - Winner: m3
    """
    # Arrange
    group = active_hui_group
    all_transactions = sample_transactions
    period = 3
    bid_amount = 50000  # m3 wins with a 50k bid
    winner_id = "m3"

    # Act
    payout = FinanceService.calculate_payout(group, period, bid_amount, winner_id, all_transactions)

    # Assert
    assert payout.deadMembers == 2  # m1, m2
    assert payout.liveMembers == 1  # m4 (m3 is the winner)
    assert payout.amountPerDead == 1000000
    assert payout.amountPerLive == 950000 # 1M - 50k bid
    assert payout.totalPot == (2 * 1000000) + (1 * 950000)  # 2,950,000
    assert payout.commission == 1000000 * 0.05  # 50,000 (5% of share amount)
    # A winning member should only have deductions if they have outstanding debt.
    # m3 has no debt, so deductions should be 0.
    assert payout.deductions == 0
    assert payout.netReceived == 2950000 - 50000 - 0 # 2,900,000

# --- Tests for get_contribution_plan ---

def test_get_contribution_plan_period_3(active_hui_group, sample_transactions):
    """
    Test case: Get the contribution plan for Period 3.
    - Winner: m3, Bid: 50k
    - Dead members: m1, m2
    - Live member: m4
    """
    # Arrange
    group = active_hui_group
    all_transactions = sample_transactions
    period = 3
    bid_amount = 50000
    winner_id = "m3"

    # Act
    plan = FinanceService.get_contribution_plan(group, period, bid_amount, winner_id, all_transactions)

    # Assert
    assert len(plan) == 4

    plan_dict = {item.memberId: item for item in plan}

    # m1 is dead, must pay full amount
    assert plan_dict["m1"].requiredAmount == 1000000
    # m2 is dead, must pay full amount
    assert plan_dict["m2"].requiredAmount == 1000000
    # m3 is the winner, pays nothing
    assert plan_dict["m3"].requiredAmount == 0
    # m4 is live, pays share - bid
    assert plan_dict["m4"].requiredAmount == 950000 # 1M - 50k

def test_get_contribution_plan_status(active_hui_group, sample_transactions):
    """Test case: Verify the contribution status for period 2 where m4 underpaid."""
    # Arrange
    group = active_hui_group
    all_transactions = sample_transactions
    period = 2
    bid_amount = 150000 # m2's bid
    winner_id = "m2"

    # Act
    plan = FinanceService.get_contribution_plan(group, period, bid_amount, winner_id, all_transactions)
    plan_dict = {item.memberId: item for item in plan}

    # Assert
    assert plan_dict["m1"].status == 'FULL'
    assert plan_dict["m2"].status == 'FULL' # Winner, required is 0
    assert plan_dict["m3"].status == 'FULL'
    assert plan_dict["m4"].status == 'PARTIAL'
    assert plan_dict["m4"].requiredAmount == 850000
    assert plan_dict["m4"].paidAmount == 500000
    assert plan_dict["m4"].remainingAmount == 350000

# --- Tests for get_member_total_debt ---

def test_get_member_total_debt(active_hui_group, sample_transactions, sample_members):
    """Test case: Calculate total debt for all members."""
    # Arrange
    groups = [active_hui_group]
    transactions = sample_transactions

    # Act
    debt_m1 = FinanceService.get_member_total_debt("m1", groups, transactions)
    debt_m2 = FinanceService.get_member_total_debt("m2", groups, transactions)
    debt_m3 = FinanceService.get_member_total_debt("m3", groups, transactions)
    debt_m4 = FinanceService.get_member_total_debt("m4", groups, transactions)

    # Assert
    # Assert the correct debt amounts.
    assert debt_m1 == 0
    assert debt_m2 == 0
    assert debt_m3 == 0
    assert debt_m4 == 350000 # Underpaid by 350k in period 2

# --- Tests for calculate_cashflow_projection ---

def test_calculate_cashflow_projection(active_hui_group):
    """
    Test case: Verify the cashflow projection for a simple scenario.
    """
    # Arrange
    # One active group with 4 members, 1M per share
    groups = [active_hui_group]

    # Act
    projection = FinanceService.calculate_cashflow_projection(groups)

    # Assert
    # The function should return projections for the next 6 months
    assert len(projection) == 6

    # For each month, the estimated in/out should be (total_slots - 1) * amountPerShare
    # (4 - 1) * 1,000,000 = 3,000,000
    first_month = projection[0]
    assert first_month["in"] == 3000000
    assert first_month["out"] == 3000000
    assert first_month["commission"] == 3000000 * 0.02 # 60,000
