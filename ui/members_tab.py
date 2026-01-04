from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
                             QDialog, QFormLayout, QLineEdit, QMessageBox, QComboBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont
import time
import qtawesome as qta
from data_models import AppState, Member, MemberStatus
from services.finance_service import FinanceService

class MemberDialog(QDialog):
    def __init__(self, parent=None, member: Member = None):
        super().__init__(parent)
        self.setWindowTitle("Thông Tin Thành Viên")
        self.member = member
        self.data_result = None
        self.resize(450, 350)
        
        layout = QFormLayout(self)
        layout.setSpacing(15)
        
        self.inp_name = QLineEdit()
        self.inp_phone = QLineEdit()
        self.inp_address = QLineEdit()
        self.inp_zalo = QLineEdit()
        self.inp_note = QLineEdit()
        self.inp_status = QComboBox()
        for status in MemberStatus:
            self.inp_status.addItem(status.value)
        
        # Styling inputs slightly better via QSS is already done globally, 
        # but let's add placeholders
        self.inp_name.setPlaceholderText("Nguyễn Văn A")
        self.inp_phone.setPlaceholderText("0912345678")
        self.inp_note.setPlaceholderText("Ghi chú thêm về thành viên...")
        
        if member:
            self.inp_name.setText(member.name)
            self.inp_phone.setText(member.phone)
            self.inp_address.setText(member.address)
            self.inp_zalo.setText(member.zalo or "")
            self.inp_note.setText(member.note or "")
            self.inp_status.setCurrentText(member.status)
            
        layout.addRow("Họ Tên *", self.inp_name)
        layout.addRow("Số ĐT *", self.inp_phone)
        layout.addRow("Địa Chỉ", self.inp_address)
        layout.addRow("Zalo", self.inp_zalo)
        layout.addRow("Trạng Thái", self.inp_status)
        layout.addRow("Ghi Chú", self.inp_note)
        
        # Buttons
        btns = QHBoxLayout()
        btns.setSpacing(10)
        
        btn_save = QPushButton("Lưu Thông Tin")
        btn_save.setIcon(qta.icon('fa5s.save', color='white'))
        btn_save.setProperty("primary", True)
        btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_save.clicked.connect(self.save)
        
        btn_cancel = QPushButton("Hủy Bỏ")
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancel.clicked.connect(self.reject)
        
        btns.addStretch()
        btns.addWidget(btn_cancel)
        btns.addWidget(btn_save)
        
        layout.addRow(btns)
        
    def save(self):
        name = self.inp_name.text()
        phone = self.inp_phone.text()
        if not name or not phone:
            QMessageBox.warning(self, "Thiếu thông tin", "Vui lòng nhập tên và số điện thoại.")
            return
            
        self.data_result = {
            "name": name,
            "phone": phone,
            "address": self.inp_address.text(),
            "zalo": self.inp_zalo.text(),
            "note": self.inp_note.text(),
            "status": self.inp_status.currentText()
        }
        self.accept()

class MembersTab(QWidget):
    def __init__(self, data: AppState, save_callback):
        super().__init__()
        self.data = data
        self.save_callback = save_callback
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Top bar
        top_bar = QHBoxLayout()
        
        lbl_icon = QLabel()
        lbl_icon.setPixmap(qta.icon('fa5s.users', color='#334155').pixmap(24,24))
        
        title = QLabel("Quản Lý Thành Viên")
        title.setProperty("heading", True)
        
        btn_add = QPushButton("Thêm Thành Viên")
        btn_add.setIcon(qta.icon('fa5s.plus', color='white'))
        btn_add.setProperty("primary", True)
        btn_add.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_add.clicked.connect(self.add_member)
        
        top_bar.addWidget(lbl_icon)
        top_bar.addWidget(title)
        top_bar.addStretch()
        top_bar.addWidget(btn_add)
        layout.addLayout(top_bar)
        
        # Search bar
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Tìm kiếm theo tên hoặc số điện thoại...")
        self.search_input.setClearButtonEnabled(True)
        self.search_input.textChanged.connect(self.refresh)
        
        search_icon = QLabel()
        search_icon.setPixmap(qta.icon('fa5s.search', color='#94A3B8').pixmap(16, 16))
        
        search_layout.addWidget(search_icon)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "ID", "Họ Tên", "SĐT", "Số Dây", "C.Hốt", "Tổng Nợ", "Uy Tín", "Trạng Thái", "Thao Tác"
        ])
        
        # Adjust column widths
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch) # Name stretches
        
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        layout.addWidget(self.table)
        
        self.refresh()

    def calculate_member_stats(self, member_id: str):
        groups_in = [g for g in self.data.groups if member_id in g.members]
        num_groups = len(groups_in)
        
        collected = [t for t in self.data.transactions if t.memberId == member_id and t.type == 'COLLECT']
        num_collected = len(collected)
        
        total_debt = FinanceService.get_member_total_debt(member_id, self.data.groups, self.data.transactions)
        
        return num_groups, num_collected, total_debt

    def refresh(self):
        search_text = self.search_input.text().lower()
        self.table.setRowCount(0)
        
        for m in self.data.members:
            if search_text and search_text not in m.name.lower() and search_text not in m.phone:
                continue
                
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            num_groups, num_collected, total_debt = self.calculate_member_stats(m.id)
            
            # Helper for items
            def item(msg, align=Qt.AlignmentFlag.AlignLeft):
                it = QTableWidgetItem(str(msg))
                it.setTextAlignment(align | Qt.AlignmentFlag.AlignVCenter)
                return it

            self.table.setItem(row, 0, item(m.id))
            self.table.setItem(row, 1, item(m.name))
            self.table.setItem(row, 2, item(m.phone))
            self.table.setItem(row, 3, item(num_groups, Qt.AlignmentFlag.AlignCenter))
            self.table.setItem(row, 4, item(num_collected, Qt.AlignmentFlag.AlignCenter))
            
            debt_item = item(f"{total_debt:,.0f}", Qt.AlignmentFlag.AlignRight)
            if total_debt > 0:
                debt_item.setForeground(QColor("#DC2626"))
            self.table.setItem(row, 5, debt_item)
            
            # Reputation styling
            rep_item = item(str(m.reputationScore), Qt.AlignmentFlag.AlignCenter)
            if m.reputationScore >= 90:
                rep_item.setForeground(QColor("#059669"))
                rep_item.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
            elif m.reputationScore < 50:
                rep_item.setForeground(QColor("#DC2626"))
            self.table.setItem(row, 6, rep_item)
            
            status_item = item(m.status, Qt.AlignmentFlag.AlignCenter)
            if m.status == MemberStatus.WATCHLIST.value or m.status == MemberStatus.BLACKLIST.value:
                status_item.setForeground(QColor("#DC2626"))
                # Highlight the whole row lightly if watchlist
                for col in range(self.table.columnCount()):
                    cell_item = self.table.item(row, col)
                    if cell_item:
                        cell_item.setBackground(QColor("#FEF2F2")) # Very light red
            
            self.table.setItem(row, 7, status_item)
            
            # Action buttons col
            actions = QWidget()
            act_layout = QHBoxLayout(actions)
            act_layout.setContentsMargins(2, 2, 2, 2)
            act_layout.setSpacing(5)
            
            btn_edit = QPushButton()
            btn_edit.setIcon(qta.icon('fa5s.edit', color='#6366f1'))
            btn_edit.setToolTip("Sửa")
            btn_edit.setFixedWidth(30)
            btn_edit.clicked.connect(lambda chk, mem=m: self.edit_member(mem))
            
            btn_del = QPushButton()
            btn_del.setIcon(qta.icon('fa5s.trash-alt', color='#ef4444'))
            btn_del.setToolTip("Xóa")
            btn_del.setFixedWidth(30)
            btn_del.clicked.connect(lambda chk, mem=m: self.delete_member(mem))
            
            act_layout.addWidget(btn_edit)
            act_layout.addWidget(btn_del)
            self.table.setCellWidget(row, 8, actions)

    def add_member(self):
        dlg = MemberDialog(self)
        if dlg.exec():
            d = dlg.data_result
            new_member = Member(
                id=str(int(time.time())),
                name=d['name'],
                phone=d['phone'],
                address=d['address'],
                joinDate=str(time.time()),
                zalo=d['zalo'],
                note=d['note']
            )
            self.data.members.append(new_member)
            self.save_callback()
            self.refresh()

    def edit_member(self, member: Member):
        dlg = MemberDialog(self, member)
        if dlg.exec():
            d = dlg.data_result
            member.name = d['name']
            member.phone = d['phone']
            member.address = d['address']
            member.zalo = d['zalo']
            member.note = d['note']
            member.status = d['status']
            self.save_callback()
            self.refresh()

    def delete_member(self, member: Member):
        ret = QMessageBox.question(self, "Xác nhận", f"Bạn có chắc muốn xóa thành viên {member.name}?",
                                 QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if ret == QMessageBox.StandardButton.Yes:
            self.data.members.remove(member)
            self.save_callback()
            self.refresh()
