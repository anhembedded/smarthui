from data_models import AuditLog, HuiGroup
from datetime import datetime
import time

class AuditService:
    @staticmethod
    def create_collect_log(group: HuiGroup, winner_id: str, bid_amount: float, calculation_result) -> AuditLog:
        # calculation_result is expected to be a PayoutDetail object or dict access compatible
        # If it's an object use .attribute, if dict use ['key']
        # Since I defined PayoutDetail as a class, I'll access attributes.
        
        cr = calculation_result
        
        ai_context = {
            "scenario_name": f"Kỳ đấu hụi số {group.currentPeriod} - Dây {group.name}",
            "input_params": {
                "base_value": group.amountPerShare,
                "total_slots": len(group.members),
                "dead_slots_count": cr.deadMembers,
                "live_slots_count": cr.liveMembers,
                "winning_bid": bid_amount,
                "commission": cr.commission
            },
            "app_output": {
                "total_collected_from_live": cr.liveMembers * cr.amountPerLive,
                "total_collected_from_dead": cr.deadMembers * cr.amountPerDead,
                "final_payout_to_winner": cr.netReceived
            }
        }
        
        return AuditLog(
            id=f"LOG-{int(time.time()*1000)}",
            timestamp=datetime.now().isoformat(),
            action='COLLECT_EXECUTION',
            userId=winner_id,
            scenario=f"Thực hiện hốt hụi kỳ {group.currentPeriod} cho dây {group.name}",
            stateBefore={
                "currentPeriod": group.currentPeriod,
                "totalMembers": len(group.members),
                "liveMembersCount": cr.liveMembers,
                "deadMembersCount": cr.deadMembers,
                "debtExisting": cr.deductions
            },
            inputParameters={
                "baseAmount": group.amountPerShare,
                "bidAmount": bid_amount,
                "commissionRate": group.commissionRate
            },
            resultCalculated={
                "netAmountReceived": cr.netReceived,
                "logicDescription": f"Payout = ({cr.liveMembers} * (V - B)) + ({cr.deadMembers} * V) - Commission - Deductions"
            },
            ai_context=ai_context
        )

    @staticmethod
    def create_payment_log(group: HuiGroup, member_id: str, required_amount: float, paid_amount: float, remaining_amount: float) -> AuditLog:
        return AuditLog(
            id=f"LOG-{int(time.time()*1000)}",
            timestamp=datetime.now().isoformat(),
            action='PAYMENT_RECORD',
            userId=member_id,
            scenario=f"Ghi nhận đóng tiền kỳ {group.currentPeriod}",
            stateBefore={
                "currentPeriod": group.currentPeriod,
                "totalMembers": len(group.members),
                "liveMembersCount": -1,
                "deadMembersCount": -1,
                "debtExisting": required_amount
            },
            inputParameters={
                "baseAmount": group.amountPerShare,
                "paymentAmount": paid_amount
            },
            resultCalculated={
                "remainingDebt": remaining_amount,
                "logicDescription": f"Remaining = Required ({required_amount}) - Paid ({paid_amount})"
            }
        )
