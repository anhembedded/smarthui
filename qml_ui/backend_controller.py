from PySide6.QtCore import QObject, Signal, Slot, Property, QAbstractListModel, QModelIndex, QByteArray, Qt
from data_models import AppState, Member
from storage import get_initial_data, save_data
import time
from datetime import datetime

class MembersModel(QAbstractListModel):
    ID_ROLE = Qt.ItemDataRole.UserRole + 1
    NAME_ROLE = Qt.ItemDataRole.UserRole + 2
    PHONE_ROLE = Qt.ItemDataRole.UserRole + 3
    ADDRESS_ROLE = Qt.ItemDataRole.UserRole + 4
    STATUS_ROLE = Qt.ItemDataRole.UserRole + 5

    _roles = {
        ID_ROLE: b'id',
        NAME_ROLE: b'name',
        PHONE_ROLE: b'phone',
        ADDRESS_ROLE: b'address',
        STATUS_ROLE: b'status',
    }

    def __init__(self, members=None):
        super().__init__()
        self._members = members or []

    def data(self, index: QModelIndex, role: int):
        if not index.isValid() or not (0 <= index.row() < len(self._members)):
            return None
        member = self._members[index.row()]
        if role == self.ID_ROLE: return member.id
        if role == self.NAME_ROLE: return member.name
        if role == self.PHONE_ROLE: return member.phone
        if role == self.ADDRESS_ROLE: return member.address
        if role == self.STATUS_ROLE: return member.status
        return None

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self._members)

    def roleNames(self) -> dict[int, QByteArray]:
        return self._roles

    def refresh_data(self, new_members):
        self.beginResetModel()
        self._members = new_members
        self.endResetModel()


class BackendController(QObject):
    statsChanged = Signal()
    membersChanged = Signal()

    def __init__(self):
        super().__init__()
        self._app_state: AppState = get_initial_data()
        self._members_model = MembersModel(self._app_state.members)
        self._stats = {}
        self.refresh_stats()

        self.membersChanged.connect(lambda: self._members_model.refresh_data(self._app_state.members))

    def refresh_stats(self):
        total_members = len(self._app_state.members)
        active_groups = len([g for g in self._app_state.groups if g.status == 'Đang chạy'])
        total_groups = len(self._app_state.groups)
        total_in = sum(t.amount for t in self._app_state.transactions if t.type == 'CONTRIBUTE')
        total_out = sum((t.netAmount or t.amount) for t in self._app_state.transactions if t.type == 'COLLECT')

        self._stats = {
            "totalMembers": total_members,
            "activeGroups": f"{active_groups}/{total_groups}",
            "totalIn": f"{total_in:,.0f} đ",
            "totalOut": f"{total_out:,.0f} đ"
        }
        self.statsChanged.emit()

    @Property(str, constant=True)
    def appName(self):
        return "SmartHui QML"

    @Property(QObject, constant=True)
    def membersModel(self):
        return self._members_model

    @Property(int, notify=statsChanged)
    def totalMembers(self):
        return self._stats.get("totalMembers", 0)

    @Property(str, notify=statsChanged)
    def activeGroups(self):
        return self._stats.get("activeGroups", "0/0")

    @Property(str, notify=statsChanged)
    def totalIn(self):
        return self._stats.get("totalIn", "0 đ")

    @Property(str, notify=statsChanged)
    def totalOut(self):
        return self._stats.get("totalOut", "0 đ")

    def save_state(self):
        save_data(self._app_state)
        self.refresh_stats()
        self.membersChanged.emit()

    @Slot(str, str)
    def addMember(self, name, phone):
        if not name or not phone:
            print("Warning: Name and phone cannot be empty.")
            return

        new_member = Member(
            id=f"m{int(time.time())}",
            name=name,
            phone=phone,
            address="",
            joinDate=datetime.now().isoformat()
        )
        self._app_state.members.append(new_member)
        self.save_state()
        print(f"Added new member: {name}")
