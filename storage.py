import json
import os
from data_models import AppState

DATA_FILE = "data.json"

def get_initial_data() -> AppState:
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return AppState.from_dict(data)
        except Exception as e:
            print(f"Error loading data: {e}")
            return create_default_data()
    else:
        return create_default_data()

def create_default_data() -> AppState:
    from data_models import Member, HuiGroup, Transaction, HuiType, HuiStatus, MemberStatus
    from datetime import datetime
    import time
    
    # Sample Members
    members = [
        Member(
            id="m1",
            name="Nguyễn Văn An",
            phone="0912345678",
            address="123 Lê Lợi, Q1, TP.HCM",
            joinDate=datetime.now().isoformat(),
            zalo="0912345678",
            reputationScore=95,
            status=MemberStatus.TRUSTED.value,
            note="Thành viên uy tín, luôn đóng tiền đúng hạn"
        ),
        Member(
            id="m2",
            name="Trần Thị Bình",
            phone="0923456789",
            address="456 Nguyễn Huệ, Q1, TP.HCM",
            joinDate=datetime.now().isoformat(),
            zalo="0923456789",
            reputationScore=88,
            status=MemberStatus.NORMAL.value,
            note=""
        ),
        Member(
            id="m3",
            name="Lê Văn Cường",
            phone="0934567890",
            address="789 Trần Hưng Đạo, Q5, TP.HCM",
            joinDate=datetime.now().isoformat(),
            zalo="0934567890",
            reputationScore=92,
            status=MemberStatus.NORMAL.value,
            note="Hay đi công tác"
        ),
        Member(
            id="m4",
            name="Phạm Thị Dung",
            phone="0945678901",
            address="321 Võ Văn Tần, Q3, TP.HCM",
            joinDate=datetime.now().isoformat(),
            zalo="0945678901",
            reputationScore=78,
            status=MemberStatus.NORMAL.value,
            note=""
        ),
        Member(
            id="m5",
            name="Hoàng Văn Em",
            phone="0956789012",
            address="654 Cách Mạng Tháng 8, Q10, TP.HCM",
            joinDate=datetime.now().isoformat(),
            zalo="0956789012",
            reputationScore=45,
            status=MemberStatus.WATCHLIST.value,
            note="Đã nợ 2 kỳ, cần theo dõi"
        ),
    ]
    
    # Sample Groups
    groups = [
        HuiGroup(
            id="g1",
            name="Hụi Tháng 2 Triệu - Bà Năm",
            type=HuiType.MONTHLY.value,
            amountPerShare=2000000,
            commissionRate=2,
            commissionType='PERCENT',
            totalMembers=10,
            startDate=datetime.now().isoformat(),
            status=HuiStatus.ACTIVE.value,
            members=["m1", "m2", "m2", "m3", "m3", "m4", "m4", "m5", "m1", "m3"],  # 10 slots, some members have multiple
            currentPeriod=3
        ),
        HuiGroup(
            id="g2",
            name="Hụi Tuần 500K - Chợ Bến Thành",
            type=HuiType.WEEKLY.value,
            amountPerShare=500000,
            commissionRate=10000,
            commissionType='FIXED',
            totalMembers=5,
            startDate=datetime.now().isoformat(),
            status=HuiStatus.ACTIVE.value,
            members=["m1", "m2", "m3", "m4", "m5"],
            currentPeriod=1
        ),
    ]
    
    # Sample Transactions (for group g1 - periods 1 and 2 already completed)
    transactions = [
        # Period 1 - m1 won
        Transaction(
            id="t1",
            huiGroupId="g1",
            memberId="m1",
            type='COLLECT',
            amount=18000000,  # 9 live × (2M - 100k)
            bidAmount=100000,
            netAmount=17560000,  # minus commission
            date=datetime.now().isoformat(),
            period=1,
            note='Hốt hụi kỳ 1'
        ),
        # Period 2 - m3 won
        Transaction(
            id="t2",
            huiGroupId="g2",
            memberId="m3",
            type='COLLECT',
            amount=16200000,  # 8 live × (2M - 200k) + 1 dead × 2M
            bidAmount=200000,
            netAmount=15760000,
            date=datetime.now().isoformat(),
            period=2,
            note='Hốt hụi kỳ 2'
        ),
        # Some contribution transactions
        Transaction(
            id="t3",
            huiGroupId="g1",
            memberId="m2",
            type='CONTRIBUTE',
            amount=3800000,  # 2 slots × (2M - 100k)
            date=datetime.now().isoformat(),
            period=1,
            note='Đóng tiền kỳ 1'
        ),
        Transaction(
            id="t4",
            huiGroupId="g1",
            memberId="m4",
            type='CONTRIBUTE',
            amount=3800000,
            date=datetime.now().isoformat(),
            period=1,
            note='Đóng tiền kỳ 1'
        ),
        # Period 2 contributions
        Transaction(
            id="t5",
            huiGroupId="g1",
            memberId="m2",
            type='CONTRIBUTE',
            amount=3600000,  # 2 slots × (2M - 200k)
            date=datetime.now().isoformat(),
            period=2,
            note='Đóng tiền kỳ 2'
        ),
        # m5 only paid partial
        Transaction(
            id="t6",
            huiGroupId="g1",
            memberId="m5",
            type='CONTRIBUTE',
            amount=1000000,  # Should be 1.8M but only paid 1M
            date=datetime.now().isoformat(),
            period=2,
            note='Đóng tiền kỳ 2 (thiếu)'
        ),
    ]
    
    return AppState(members=members, groups=groups, transactions=transactions, auditLogs=[])

def save_data(state: AppState):
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(state.to_dict(), f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error saving data: {e}")
