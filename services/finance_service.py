from typing import List, Dict, Optional
from data_models import HuiGroup, Transaction, Member, HuiStatus, AuditLog

class PayoutDetail:
    def __init__(self, liveMembers, deadMembers, amountPerLive, amountPerDead, totalPot, commission, deductions, netReceived):
        self.liveMembers = liveMembers
        self.deadMembers = deadMembers
        self.amountPerLive = amountPerLive
        self.amountPerDead = amountPerDead
        self.totalPot = totalPot
        self.commission = commission
        self.deductions = deductions
        self.netReceived = netReceived

class ContributionDetail:
    def __init__(self, memberId, deadSlots, liveSlots, requiredAmount, paidAmount, remainingAmount, status):
        self.memberId = memberId
        self.deadSlots = deadSlots
        self.liveSlots = liveSlots
        self.requiredAmount = requiredAmount
        self.paidAmount = paidAmount
        self.remainingAmount = remainingAmount
        self.status = status # 'FULL' | 'PARTIAL' | 'UNPAID' | 'OVERPAID'

class FinanceService:
    @staticmethod
    def calculate_payout(group: HuiGroup, period: int, bid_amount: float, winner_id: str, all_transactions: List[Transaction]) -> PayoutDetail:
        # 1. Determine dead slots
        dead_slots_count = 0
        for t in all_transactions:
            if t.huiGroupId == group.id and t.type == 'COLLECT' and t.period < period:
                dead_slots_count += 1
        
        N_dead = dead_slots_count
        # Total members logic: group.members is a list of member IDs.
        # But wait, group.members might contain duplicates if a member has multiple slots? 
        # React code: group.members.length. So yes, it counts slots.
        N_live = len(group.members) - N_dead - 1

        V = group.amountPerShare
        B = bid_amount

        # 2. Calculate amounts
        amount_per_live = V - B
        amount_per_dead = V

        total_pot = (N_live * amount_per_live) + (N_dead * amount_per_dead)

        # 3. Commission
        if hasattr(group, 'commissionType') and group.commissionType == 'FIXED':
            C = group.commissionRate
        else:
            C = V * (group.commissionRate or 0) / 100

        # 4. Deductions (old debts)
        D = 0
        for p in range(1, period):
            winner_slots_in_group = group.members.count(winner_id)
            
            paid_amount = sum(t.amount for t in all_transactions 
                              if t.huiGroupId == group.id and t.type == 'CONTRIBUTE' and t.period == p and t.memberId == winner_id)
            
            required_approx = winner_slots_in_group * V
            
            if paid_amount < required_approx:
                D += (required_approx - paid_amount)
        
        net_received = total_pot - C - D

        return PayoutDetail(N_live, N_dead, amount_per_live, amount_per_dead, total_pot, C, D, net_received)

    @staticmethod
    def get_contribution_plan(group: HuiGroup, period: int, bid_amount: float, winner_id: Optional[str], all_transactions: List[Transaction]) -> List[ContributionDetail]:
        unique_members = list(set(group.members))
        plan = []
        V = group.amountPerShare
        
        amount_per_live = V - bid_amount
        amount_per_dead = V

        for member_id in unique_members:
            total_slots = group.members.count(member_id)

            dead_slots = len([t for t in all_transactions if t.huiGroupId == group.id and t.type == 'COLLECT' and t.period < period and t.memberId == member_id])
            
            live_slots = total_slots - dead_slots
            
            if winner_id and member_id == winner_id:
                live_slots = max(0, live_slots - 1)
            
            required_amount = (dead_slots * amount_per_dead) + (live_slots * amount_per_live)

            paid_amount = sum(t.amount for t in all_transactions 
                              if t.huiGroupId == group.id and t.period == period and t.memberId == member_id and t.type == 'CONTRIBUTE')
            
            remaining_amount = max(0, required_amount - paid_amount)

            if required_amount == 0 and paid_amount == 0:
                status = 'FULL'
            elif paid_amount >= required_amount and required_amount > 0:
                status = 'FULL'
            elif paid_amount > required_amount:
                status = 'OVERPAID'
            elif paid_amount > 0:
                status = 'PARTIAL'
            else:
                status = 'UNPAID'
            
            if total_slots > 0:
                plan.append(ContributionDetail(member_id, dead_slots, live_slots, required_amount, paid_amount, remaining_amount, status))
        
        # Sort: Debtors first
        plan.sort(key=lambda x: (0 if x.remainingAmount > 0 else 1, -x.remainingAmount))
        return plan

    @staticmethod
    def calculate_cashflow_projection(groups: List[HuiGroup]):
        projection = []
        import datetime
        today = datetime.date.today()
        
        for i in range(6):
            # Calculate target month (roughly)
            # Python date math is annoying without dateutil, assume simple increment
            month = today.month + i
            year = today.year + (month - 1) // 12
            month = (month - 1) % 12 + 1
            
            month_key = f"T{month}/{year}"
            
            estimated_in = 0
            estimated_out = 0
            
            # Filter active groups
            active_groups = [g for g in groups if g.status == HuiStatus.ACTIVE.value]
            
            for g in active_groups:
                total_slots = len(g.members)
                # Approximation from React code:
                estimated_in += (total_slots - 1) * g.amountPerShare
                estimated_out += (total_slots - 1) * g.amountPerShare
            
            projection.append({
                "name": month_key,
                "in": estimated_in,
                "out": estimated_out,
                "commission": estimated_in * 0.02
            })
        return projection

    @staticmethod
    def get_member_total_debt(member_id: str, all_groups: List[HuiGroup], all_transactions: List[Transaction]) -> float:
        total_debt = 0
        for group in all_groups:
            if member_id not in group.members:
                continue
            
            # Count slots for this member
            slots_count = group.members.count(member_id)
            V = group.amountPerShare
            
            # Past periods: required is slots * V
            # (Wait, if they hốt in a past period, their required amount for that period was actually lower? 
            # No, usually in ROSCA, the winner's "contribution" for the period they collect is 0 or handled as reduction.
            # But in this app's logic, it seems they still "contribute"? No, look at calculate_payout deductions.
            # It checks p in range(1, period).
            
            for p in range(1, group.currentPeriod + 1):
                # Was this member the winner in this period or before?
                # If they were winner in period X, then for p > X they are "dead".
                # For p == X, they collected.
                
                # Check if they collected in period < p
                collected_before = any(t.memberId == member_id and t.huiGroupId == group.id and t.type == 'COLLECT' and t.period < p 
                                     for t in all_transactions)
                
                # Check if they are the winner in current p
                is_winner_now = any(t.memberId == member_id and t.huiGroupId == group.id and t.type == 'COLLECT' and t.period == p 
                                   for t in all_transactions)
                
                # Simple approximation: if they haven't hốt, they pay V-Bid. If they have hốt, they pay V.
                # But we don't know the Bids of past periods easily without looking at transactions.
                # For debt calculation, we can check the actual Transaction of type 'CONTRIBUTE' 
                # vs what was required.
                
                # Let's simplify: Required = sum of (dead_slots * V + live_slots * (V-Bid))
                # This is getting complex because the app doesn't store past Bids explicitly in the Group object.
                # However, calculate_payout uses 'required_approx = winner_slots_in_group * V' for deductions.
                
                # Let's use a simpler heuristic for debt: 
                # Debt = Required Contribution - Actual Contribution
                
                # For past periods, we can look at the Transactions of type 'COLLECT' to find the winner and bid.
                past_collect = [t for t in all_transactions if t.huiGroupId == group.id and t.type == 'COLLECT' and t.period <= p]
                
                # If p is a past period, we should have a 'COLLECT' transaction for it.
                winner_in_p = None
                bid_in_p = 0
                for tc in past_collect:
                    if tc.period == p:
                        winner_in_p = tc.memberId
                        bid_in_p = tc.bidAmount or 0
                        break
                
                # If no winner was recorded for p (maybe it's current period and not yet hốt), assume bid=0
                # Actually if it's past, there should be one.
                
                # Dead slots for this member in period p
                my_dead_slots = len([t for t in all_transactions if t.huiGroupId == group.id and t.type == 'COLLECT' and t.period < p and t.memberId == member_id])
                my_live_slots = slots_count - my_dead_slots
                if winner_in_p == member_id:
                    # The slot that hốt in this period p is neither live nor dead for contribution purpose?
                    # Usually, the winner doesn't pay in the period they hốt.
                    my_live_slots = max(0, my_live_slots - 1)
                
                required_in_p = (my_dead_slots * V) + (my_live_slots * (V - bid_in_p))
                
                paid_in_p = sum(t.amount for t in all_transactions if t.huiGroupId == group.id and t.memberId == member_id and t.type == 'CONTRIBUTE' and t.period == p)
                
                if paid_in_p < required_in_p:
                    total_debt += (required_in_p - paid_in_p)
                    
        return total_debt
