import pytest
from datetime import datetime
from data_models import HuiGroup, AuditLog, HuiType, HuiStatus
from services.audit_service import AuditService
from services.finance_service import PayoutDetail

# --- Arrange: Reusable Test Data ---

@pytest.fixture
def sample_hui_group():
    """Provides a sample HuiGroup for audit tests."""
    return HuiGroup(
        id="g1",
        name="Audit Test Hui",
        type=HuiType.MONTHLY.value,
        amountPerShare=1000000,
        commissionRate=5,
        totalMembers=5,
        startDate="2024-01-01",
        status=HuiStatus.ACTIVE.value,
        members=["m1", "m2", "m3", "m4", "m5"],
        currentPeriod=3,
        commissionType='PERCENT'
    )

@pytest.fixture
def sample_payout_detail():
    """Provides a sample PayoutDetail object for the collect log test."""
    return PayoutDetail(
        liveMembers=3,
        deadMembers=1,
        amountPerLive=900000,
        amountPerDead=1000000,
        totalPot=3700000,
        commission=50000,
        deductions=100000,
        netReceived=3550000
    )

# --- Tests for AuditService ---

def test_create_collect_log(sample_hui_group, sample_payout_detail):
    """
    Test case: Verify that a correct AuditLog is created for a 'COLLECT' action.
    """
    # Arrange
    group = sample_hui_group
    winner_id = "m3"
    bid_amount = 100000
    payout = sample_payout_detail

    # Act
    log_entry = AuditService.create_collect_log(group, winner_id, bid_amount, payout)

    # Assert
    assert isinstance(log_entry, AuditLog)
    assert log_entry.action == 'COLLECT_EXECUTION'
    assert log_entry.userId == winner_id
    assert log_entry.scenario == f"Thực hiện hốt hụi kỳ {group.currentPeriod} cho dây {group.name}"

    # Verify stateBefore dictionary
    assert log_entry.stateBefore["currentPeriod"] == group.currentPeriod
    assert log_entry.stateBefore["debtExisting"] == payout.deductions

    # Verify resultCalculated dictionary
    assert log_entry.resultCalculated["netAmountReceived"] == payout.netReceived
    assert "Payout = (3 * (V - B)) + (1 * V) - Commission - Deductions" in log_entry.resultCalculated["logicDescription"]

    # Verify AI Context
    assert log_entry.ai_context["input_params"]["winning_bid"] == bid_amount
    assert log_entry.ai_context["app_output"]["final_payout_to_winner"] == payout.netReceived

def test_create_payment_log(sample_hui_group):
    """
    Test case: Verify that a correct AuditLog is created for a 'PAYMENT_RECORD' action.
    """
    # Arrange
    group = sample_hui_group
    member_id = "m4"
    required = 900000
    paid = 800000
    remaining = 100000

    # Act
    log_entry = AuditService.create_payment_log(group, member_id, required, paid, remaining)

    # Assert
    assert isinstance(log_entry, AuditLog)
    assert log_entry.action == 'PAYMENT_RECORD'
    assert log_entry.userId == member_id
    assert log_entry.scenario == f"Ghi nhận đóng tiền kỳ {group.currentPeriod}"

    # Verify inputParameters
    assert log_entry.inputParameters["paymentAmount"] == paid

    # Verify resultCalculated
    assert log_entry.resultCalculated["remainingDebt"] == remaining
    assert "Remaining = Required (900000) - Paid (800000)" in log_entry.resultCalculated["logicDescription"]
