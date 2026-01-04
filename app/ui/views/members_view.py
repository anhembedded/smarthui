"""
Members View - Consumer
Listens to events and updates UI accordingly.
"""
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
import qtawesome as qta

from app.core.event_bus import get_event_bus, Event, EventType
from app.models.member import Member
from app.models.enums import MemberStatus
from app.services.members_service import MembersService

class MembersView(QWidget):
    """
    View for Members (Consumer).
    Subscribes to events and updates UI.
    """
    
    def __init__(self, service: MembersService, save_callback):
        super().__init__()
        self.service = service
        self.save_callback = save_callback
        
        # Subscribe to events
        self._subscribe_to_events()
        
        self.init_ui()
    
    def _subscribe_to_events(self):
        """Subscribe to relevant events (Consumer)."""
        get_event_bus().subscribe(EventType.MEMBER_CREATED, self._on_member_created)
        get_event_bus().subscribe(EventType.MEMBER_UPDATED, self._on_member_updated)
        get_event_bus().subscribe(EventType.MEMBER_DELETED, self._on_member_deleted)
        get_event_bus().subscribe(EventType.DATA_REFRESH_REQUESTED, self._on_refresh_requested)
    
    def _on_member_created(self, event: Event):
        """Handle MEMBER_CREATED event."""
        self.save_callback()
        self.refresh()
        self._show_notification(f"Đã thêm thành viên: {event.data.name}")
    
    def _on_member_updated(self, event: Event):
        """Handle MEMBER_UPDATED event."""
        self.save_callback()
        self.refresh()
        self._show_notification(f"Đã cập nhật: {event.data['member'].name}")
    
    def _on_member_deleted(self, event: Event):
        """Handle MEMBER_DELETED event."""
        self.save_callback()
        self.refresh()
        self._show_notification(f"Đã xóa thành viên: {event.data.name}")
    
    def _on_refresh_requested(self, event: Event):
        """Handle DATA_REFRESH_REQUESTED event."""
        if event.data == 'members' or event.data == 'all':
            self.refresh()
    
    def _show_notification(self, message: str):
        """Show a notification (could be toast, statusbar, etc.)."""
        # For now, just print. Later can emit NOTIFICATION_SHOW event
        print(f"[Notification] {message}")
    
    def init_ui(self):
        """Initialize UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # Header
        header_layout = QHBoxLayout()
        lbl_title = QLabel("Quản Lý Thành Viên")
        lbl_title.setProperty("heading", True)
        header_layout.addWidget(lbl_title)
        header_layout.addStretch()
        
        btn_add = QPushButton(" Thêm Thành Viên")
        btn_add.setIcon(QIcon(qta.icon('fa5s.user-plus', color='white').pixmap(16, 16)))
        btn_add.setProperty("primary", True)
        btn_add.clicked.connect(self.on_add_clicked)
        header_layout.addWidget(btn_add)
        
        layout.addLayout(header_layout)
        
        # Search
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Tìm kiếm...")
        self.search_input.setClearButtonEnabled(True)
        self.search_input.textChanged.connect(self.on_search_changed)
        
        search_icon = QLabel()
        search_icon.setPixmap(qta.icon('fa5s.search', color='#94A3B8').pixmap(16, 16))
        
        search_layout.addWidget(search_icon)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "ID", "Tên", "SĐT", "Địa chỉ", "Số Dây", "C.Hốt", "Tổng Nợ", "Uy Tín", "Trạng thái"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.doubleClicked.connect(self.on_row_double_clicked)
        
        layout.addWidget(self.table)
        
        self.refresh()
    
    def refresh(self):
        """Refresh table data."""
        query = self.search_input.text() if hasattr(self, 'search_input') else ""
        
        # Get data from service
        members = self.service.search(query) if query else self.service.get_all()
        
        self.table.setRowCount(len(members))
        
        for row, m in enumerate(members):
            stats = self.service.get_stats(m.id)
            self._render_row(row, m, stats)
    
    def _render_row(self, row: int, member: Member, stats: dict):
        """Render a table row."""
        def item(text, alignment=Qt.AlignmentFlag.AlignLeft):
            it = QTableWidgetItem(str(text))
            it.setTextAlignment(alignment | Qt.AlignmentFlag.AlignVCenter)
            return it
        
        self.table.setItem(row, 0, item(member.id[:8]))
        self.table.setItem(row, 1, item(member.name))
        self.table.setItem(row, 2, item(member.phone))
        self.table.setItem(row, 3, item(member.address))
        self.table.setItem(row, 4, item(stats['num_groups'], Qt.AlignmentFlag.AlignCenter))
        self.table.setItem(row, 5, item(stats['num_collected'], Qt.AlignmentFlag.AlignCenter))
        
        debt_item = item(f"{stats['total_debt']:,.0f}", Qt.AlignmentFlag.AlignRight)
        if stats['total_debt'] > 0:
            debt_item.setForeground(QColor("#DC2626"))
        self.table.setItem(row, 6, debt_item)
        
        rep_item = item(member.reputationScore, Qt.AlignmentFlag.AlignCenter)
        if member.reputationScore >= 90:
            rep_item.setForeground(QColor("#059669"))
        elif member.reputationScore < 50:
            rep_item.setForeground(QColor("#DC2626"))
        self.table.setItem(row, 7, rep_item)
        
        status_item = item(member.status, Qt.AlignmentFlag.AlignCenter)
        if member.is_high_risk():
            status_item.setForeground(QColor("#DC2626"))
            for col in range(self.table.columnCount()):
                cell = self.table.item(row, col)
                if cell:
                    cell.setBackground(QColor("#FEF2F2"))
        
        self.table.setItem(row, 8, status_item)
        self.table.item(row, 0).setData(Qt.ItemDataRole.UserRole, member)
    
    def on_search_changed(self):
        """Handle search input change."""
        self.refresh()
    
    def on_add_clicked(self):
        """Handle add button click."""
        dialog = MemberDialog(self, None, self.service)
        dialog.exec()
    
    def on_row_double_clicked(self, index):
        """Handle row double click."""
        member = self.table.item(index.row(), 0).data(Qt.ItemDataRole.UserRole)
        dialog = MemberDialog(self, member, self.service)
        dialog.exec()
    
    def closeEvent(self, event):
        """Cleanup when widget is closed."""
        # Unsubscribe from events
        get_event_bus().unsubscribe(EventType.MEMBER_CREATED, self._on_member_created)
        get_event_bus().unsubscribe(EventType.MEMBER_UPDATED, self._on_member_updated)
        get_event_bus().unsubscribe(EventType.MEMBER_DELETED, self._on_member_deleted)
        get_event_bus().unsubscribe(EventType.DATA_REFRESH_REQUESTED, self._on_refresh_requested)
        super().closeEvent(event)

class MemberDialog(QDialog):
    """Dialog for add/edit member (Producer)."""
    
    def __init__(self, parent, member: Member, service: MembersService):
        super().__init__(parent)
        self.member = member
        self.service = service
        self.setWindowTitle("Sửa Thành Viên" if member else "Thêm Thành Viên")
        self.resize(500, 400)
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI."""
        layout = QFormLayout(self)
        layout.setSpacing(15)
        
        self.inp_name = QLineEdit()
        self.inp_phone = QLineEdit()
        self.inp_address = QLineEdit()
        self.inp_zalo = QLineEdit()
        self.inp_note = QTextEdit()
        self.inp_note.setMaximumHeight(80)
        self.inp_status = QComboBox()
        self.inp_status.addItems([e.value for e in MemberStatus])
        
        if self.member:
            self.inp_name.setText(self.member.name)
            self.inp_phone.setText(self.member.phone)
            self.inp_address.setText(self.member.address)
            self.inp_zalo.setText(self.member.zalo or "")
            self.inp_note.setPlainText(self.member.note or "")
            self.inp_status.setCurrentText(self.member.status)
        
        layout.addRow("Tên *", self.inp_name)
        layout.addRow("SĐT *", self.inp_phone)
        layout.addRow("Địa chỉ", self.inp_address)
        layout.addRow("Zalo", self.inp_zalo)
        layout.addRow("Ghi chú", self.inp_note)
        layout.addRow("Trạng thái", self.inp_status)
        
        btn_layout = QHBoxLayout()
        btn_save = QPushButton("Lưu")
        btn_save.setProperty("primary", True)
        btn_save.clicked.connect(self.on_save)
        
        btn_cancel = QPushButton("Hủy")
        btn_cancel.clicked.connect(self.reject)
        
        if self.member:
            btn_delete = QPushButton("Xóa")
            btn_delete.setStyleSheet("background-color: #DC2626; color: white;")
            btn_delete.clicked.connect(self.on_delete)
            btn_layout.addWidget(btn_delete)
        
        btn_layout.addStretch()
        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(btn_save)
        layout.addRow(btn_layout)
    
    def on_save(self):
        """Handle save - produces event via service."""
        try:
            if self.member:
                self.service.update(
                    self.member,
                    self.inp_name.text(),
                    self.inp_phone.text(),
                    self.inp_address.text(),
                    self.inp_zalo.text(),
                    self.inp_note.toPlainText(),
                    self.inp_status.currentText()
                )
            else:
                self.service.create(
                    self.inp_name.text(),
                    self.inp_phone.text(),
                    self.inp_address.text(),
                    self.inp_zalo.text(),
                    self.inp_note.toPlainText(),
                    self.inp_status.currentText()
                )
            self.accept()
        except ValueError as e:
            QMessageBox.warning(self, "Lỗi", str(e))
    
    def on_delete(self):
        """Handle delete - produces event via service."""
        reply = QMessageBox.question(
            self, "Xác nhận",
            f"Xóa thành viên '{self.member.name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.service.delete(self.member)
                self.accept()
            except ValueError as e:
                QMessageBox.warning(self, "Lỗi", str(e))
