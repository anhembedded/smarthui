from enum import Enum

class HuiType(Enum):
    MONTHLY = 'Tháng'
    WEEKLY = 'Tuần'
    BIWEEKLY = '15 Ngày'
    DAILY = 'Ngày'
    KIES = 'Mùa'

class HuiStatus(Enum):
    ACTIVE = 'Đang chạy'
    COMPLETED = 'Đã mãn'

class BiddingRule(Enum):
    OPEN_BID = 'Đấu công khai'
    SEALED_BID = 'Bỏ thăm kín'

class MemberStatus(Enum):
    NORMAL = 'Bình thường'
    TRUSTED = 'Uy tín'
    WATCHLIST = 'Cần chú ý'
    BLACKLIST = 'Blacklist'
