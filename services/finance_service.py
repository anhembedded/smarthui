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
        dead_slots_count = len([t for t in all_transactions if t.huiGroupId == group.id and t.type == 'COLLECT' and t.period < period])
        
        N_dead = dead_slots_count
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

        # 4. Deductions (old debts) - now calls the corrected debt function
        D = FinanceService.get_member_total_debt(winner_id, [group], all_transactions)
        
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
                # The winner of the current period does not contribute
                live_slots = 0
                dead_slots = 0
            
            required_amount = (dead_slots * amount_per_dead) + (live_slots * amount_per_live)

            paid_amount = sum(t.amount for t in all_transactions 
                              if t.huiGroupId == group.id and t.period == period and t.memberId == member_id and t.type == 'CONTRIBUTE')
            
            remaining_amount = required_amount - paid_amount

            if required_amount == 0:
                status = 'FULL' # Covers winner and those with no slots
            elif remaining_amount <= 0:
                status = 'FULL'
            elif paid_amount > 0:
                status = 'PARTIAL'
            else:
                status = 'UNPAID'
            
            if total_slots > 0:
                plan.append(ContributionDetail(member_id, dead_slots, live_slots, required_amount, paid_amount, remaining_amount, status))
        
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
            
            slots_count = group.members.count(member_id)
            V = group.amountPerShare
            
            # Iterate through PAST periods only
            for p in range(1, group.currentPeriod):
                # Find the bid amount for this past period
                bid_in_p = 0
                winner_in_p = None
                for t in all_transactions:
                    if t.huiGroupId == group.id and t.type == 'COLLECT' and t.period == p:
                        bid_in_p = t.bidAmount or 0
                        winner_in_p = t.memberId
                        break
                
                # Determine member's status in this period (p)
                my_dead_slots_in_p = len([t for t in all_transactions if t.huiGroupId == group.id and t.type == 'COLLECT' and t.period < p and t.memberId == member_id])
                my_live_slots_in_p = slots_count - my_dead_slots_in_p

                required_in_p = 0
                if member_id == winner_in_p:
                    # Winner does not contribute in the period they win
                    required_in_p = 0
                else:
                    required_in_p = (my_dead_slots_in_p * V) + (my_live_slots_in_p * (V - bid_in_p))

                paid_in_p = sum(t.amount for t in all_transactions if t.huiGroupId == group.id and t.memberId == member_id and t.type == 'CONTRIBUTE' and t.period == p)
                
                shortfall = required_in_p - paid_in_p
                if shortfall > 0:
                    total_debt += shortfall
                    
        return total_debt
