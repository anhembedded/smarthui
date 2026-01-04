from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
                             QDialog, QFormLayout, QLineEdit, QComboBox, QMessageBox,
                             QStackedWidget, QScrollArea, QFrame, QInputDialog, QSpinBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
import time
import qtawesome as qta
from datetime import datetime
from data_models import AppState, HuiGroup, HuiType, HuiStatus, Transaction, AuditLog
from services.finance_service import FinanceService
from services.audit_service import AuditService

# --- DIALOGS ---

class CycleSetupWizard(QDialog):
    def __init__(self, parent, all_members):
        super().__init__(parent)
        self.setWindowTitle("Thiết Lập Dây Hụi (Wizard)")
        self.all_members = all_members
        self.result_data = None
        self.resize(700, 600)
        
        self.total_steps = 3
        self.current_step = 1
        
        self.main_layout = QVBoxLayout(self)
        
        # Header - Step Progress
        self.lbl_progress = QLabel("Bước 1/3: Thông tin cơ bản")
        self.lbl_progress.setStyleSheet("font-weight: bold; color: #6366F1; font-size: 16px;")
        self.main_layout.addWidget(self.lbl_progress)
        
        # Content - Stacked Widget
        self.stack = QStackedWidget()
        self.main_layout.addWidget(self.stack)
        
        self.init_step1()
        self.init_step2()
        self.init_step3()
        
        # Navigation Buttons
        nav_layout = QHBoxLayout()
        self.btn_back = QPushButton(" Quay lại")
        self.btn_back.setIcon(qta.icon('fa5s.arrow-left'))
        self.btn_back.clicked.connect(self.prev_step)
        self.btn_back.setEnabled(False)
        
        self.btn_next = QPushButton("Tiếp theo ")
        self.btn_next.setIcon(qta.icon('fa5s.arrow-right', color='white'))
        self.btn_next.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.btn_next.setProperty("primary", True)
        self.btn_next.clicked.connect(self.next_step)
        
        nav_layout.addWidget(self.btn_back)
        nav_layout.addStretch()
        nav_layout.addWidget(self.btn_next)
        self.main_layout.addLayout(nav_layout)

    def init_step1(self):
        page = QWidget()
        layout = QFormLayout(page)
        layout.setSpacing(15)
        
        self.inp_name = QLineEdit()
        self.inp_name.setPlaceholderText("VD: Hụi Tháng 2tr - Bà Năm")
        
        self.inp_type = QComboBox()
        self.inp_type.addItems([e.value for e in HuiType])
        
        self.inp_amount = QLineEdit()
        self.inp_amount.setPlaceholderText("VD: 2000000")
        
        comm_layout = QHBoxLayout()
        self.inp_comm = QLineEdit()
        self.inp_comm.setText("50")
        self.inp_comm_type = QComboBox()
        self.inp_comm_type.addItems(["%", "VNĐ"])
        comm_layout.addWidget(self.inp_comm)
        comm_layout.addWidget(self.inp_comm_type)
        
        layout.addRow("Tên Dây *", self.inp_name)
        layout.addRow("Loại Hình *", self.inp_type)
        layout.addRow("Số Tiền/Phần *", self.inp_amount)
        layout.addRow("Tiền Thảo", comm_layout)
        
        self.stack.addWidget(page)

    def init_step2(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        
        lbl = QLabel("Phân Chân Hụi: Chọn thành viên và số lượng chân tham gia")
        lbl.setStyleSheet("color: #64748B;")
        layout.addWidget(lbl)
        
        # Tools
        tools = QHBoxLayout()
        btn_sel_all = QPushButton("Chọn tất cả")
        btn_sel_all.setFixedWidth(100)
        btn_sel_all.clicked.connect(self.select_all_members)
        tools.addWidget(btn_sel_all)
        tools.addStretch()
        layout.addLayout(tools)
        
        # Member Selection Table
        self.member_table = QTableWidget()
        self.member_table.setColumnCount(3)
        self.member_table.setHorizontalHeaderLabels(["Chọn", "Thành Viên", "Số Chân"])
        self.member_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.member_table.verticalHeader().setVisible(False)
        
        self.member_table.setRowCount(len(self.all_members))
        for i, m in enumerate(self.all_members):
            chk = QTableWidgetItem(m.name)
            chk.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
            chk.setCheckState(Qt.CheckState.Unchecked)
            self.member_table.setItem(i, 0, chk)
            self.member_table.setItem(i, 1, QTableWidgetItem(m.phone))
            
            spin = QSpinBox()
            spin.setMinimum(1)
            spin.setValue(1)
            self.member_table.setCellWidget(i, 2, spin)
            
        layout.addWidget(self.member_table)
        self.stack.addWidget(page)

    def init_step3(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        
        lbl = QLabel("Nhập Liệu Lịch Sử (Tùy chọn)")
        lbl.setProperty("heading", True)
        layout.addWidget(lbl)
        
        form = QFormLayout()
        self.inp_period = QSpinBox()
        self.inp_period.setMinimum(1)
        self.inp_period.setValue(1)
        self.inp_period.valueChanged.connect(self.update_history_table)
        form.addRow("Kỳ Hiện Tại:", self.inp_period)
        layout.addLayout(form)
        
        lbl_hint = QLabel("Nếu kỳ hiện tại > 1, vui lòng chọn người đã hốt cho các kỳ trước:")
        lbl_hint.setStyleSheet("color: #64748B; font-style: italic;")
        layout.addWidget(lbl_hint)
        
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(3)
        self.history_table.setHorizontalHeaderLabels(["Kỳ", "Người Hốt", "Tiền Thăm"])
        self.history_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.history_table.verticalHeader().setVisible(False)
        layout.addWidget(self.history_table)
        
        self.stack.addWidget(page)

    def update_history_table(self):
        period = self.inp_period.value()
        self.history_table.setRowCount(0)
        
        if period <= 1:
            return
            
        # Get selected members
        selected_slots = []
        for i in range(self.member_table.rowCount()):
            if self.member_table.item(i, 0).checkState() == Qt.CheckState.Checked:
                m = self.all_members[i]
                slots = self.member_table.cellWidget(i, 2).value()
                for s in range(slots):
                    selected_slots.append({'id': m.id, 'name': f"{m.name} (Chân {s+1})", 'idx': len(selected_slots)})

        for p in range(1, period):
            row = self.history_table.rowCount()
            self.history_table.insertRow(row)
            self.history_table.setItem(row, 0, QTableWidgetItem(f"Kỳ {p}"))
            
            cb = QComboBox()
            for slot in selected_slots:
                cb.addItem(slot['name'], slot['idx'])
            self.history_table.setCellWidget(row, 1, cb)
            
            bid = QLineEdit("0")
            bid.setPlaceholderText("Tiền thăm")
            self.history_table.setCellWidget(row, 2, bid)

    def next_step(self):
        if self.current_step == 1:
            if not self.inp_name.text() or not self.inp_amount.text():
                QMessageBox.warning(self, "Lỗi", "Vui lòng nhập tên và số tiền.")
                return
        
        if self.current_step == 2:
            # Refresh history table with actual selected members
            self.update_history_table()
            
        if self.current_step < self.total_steps:
            self.current_step += 1
            self.stack.setCurrentIndex(self.current_step - 1)
            self.update_nav()
        else:
            self.finish()

    def prev_step(self):
        if self.current_step > 1:
            self.current_step -= 1
            self.stack.setCurrentIndex(self.current_step - 1)
            self.update_nav()

    def update_nav(self):
        self.lbl_progress.setText(f"Bước {self.current_step}/3: " + 
                                 ["Thông tin cơ bản", "Phân chân hụi", "Dữ liệu lịch sử"][self.current_step-1])
        self.btn_back.setEnabled(self.current_step > 1)
        self.btn_next.setText("Hoàn tất" if self.current_step == self.total_steps else "Tiếp theo")

    def finish(self):
        # Collect members
        members_list = []
        for i in range(self.member_table.rowCount()):
            if self.member_table.item(i, 0).checkState() == Qt.CheckState.Checked:
                m_id = self.all_members[i].id
                slots = self.member_table.cellWidget(i, 2).value()
                for _ in range(slots):
                    members_list.append(m_id)
        
        if len(members_list) < 2:
            QMessageBox.warning(self, "Lỗi", "Cần ít nhất 2 chân hụi tham gia.")
            self.current_step = 2
            self.stack.setCurrentIndex(1)
            self.update_nav()
            return
            
        # Collect history
        past_winners = []
        if self.inp_period.value() > 1:
            for r in range(self.history_table.rowCount()):
                cb = self.history_table.cellWidget(r, 1)
                bid_inp = self.history_table.cellWidget(r, 2)
                slot_idx = cb.currentData()
                past_winners.append({
                    'period': r + 1,
                    'memberId': members_list[slot_idx],
                    'bid': float(bid_inp.text() or 0)
                })

        self.result_data = {
            "name": self.inp_name.text(),
            "type": self.inp_type.currentText(),
            "amount": float(self.inp_amount.text()),
            "commission": float(self.inp_comm.text() or 0),
            "commissionType": 'FIXED' if self.inp_comm_type.currentText() == 'VNĐ' else 'PERCENT',
            "members": members_list,
            "currentPeriod": self.inp_period.value(),
            "pastWinners": past_winners
        }
        self.accept()

    def select_all_members(self):
        for i in range(self.member_table.rowCount()):
            self.member_table.item(i, 0).setCheckState(Qt.CheckState.Checked)

# --- BIDDING DIALOG ---

class BiddingDialog(QDialog):
    def __init__(self, parent, group: HuiGroup, all_members, all_transactions):
        super().__init__(parent)
        self.setWindowTitle(f"Hốt Hụi - {group.name}")
        self.group = group
        self.all_members = all_members
        self.all_transactions = all_transactions
        self.result_data = None
        self.resize(800, 600)
        
        main_layout = QHBoxLayout(self)
        
        # Left Panel - Input
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        lbl_title = QLabel("Thông Tin Đấu Hụi")
        lbl_title.setProperty("heading", True)
        left_layout.addWidget(lbl_title)
        
        form = QFormLayout()
        form.setSpacing(15)
        
        # Winner selection
        self.cb_winner = QComboBox()
        unique_members = {m.id: m for m in all_members if m.id in group.members}
        for mid in sorted(unique_members.keys()):
            self.cb_winner.addItem(unique_members[mid].name, mid)
        self.cb_winner.currentIndexChanged.connect(self.update_preview)
        
        # Bid input
        self.inp_bid = QLineEdit()
        self.inp_bid.setPlaceholderText("Nhập số tiền thăm...")
        self.inp_bid.textChanged.connect(self.update_preview)
        
        form.addRow("Người Hốt:", self.cb_winner)
        form.addRow("Tiền Thăm (VNĐ):", self.inp_bid)
        
        left_layout.addLayout(form)
        
        # Warning label
        self.lbl_warning = QLabel()
        self.lbl_warning.setStyleSheet("color: #EF4444; font-weight: bold; padding: 10px; background: #FEE2E2; border-radius: 6px;")
        self.lbl_warning.setWordWrap(True)
        self.lbl_warning.hide()
        left_layout.addWidget(self.lbl_warning)
        
        left_layout.addStretch()
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_cancel = QPushButton("Hủy")
        btn_cancel.clicked.connect(self.reject)
        
        self.btn_confirm = QPushButton("Xác Nhận Hốt Hụi")
        self.btn_confirm.setIcon(qta.icon('fa5s.check', color='white'))
        self.btn_confirm.setProperty("primary", True)
        self.btn_confirm.clicked.connect(self.confirm)
        self.btn_confirm.setEnabled(False)
        
        btn_layout.addWidget(btn_cancel)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_confirm)
        left_layout.addLayout(btn_layout)
        
        # Right Panel - Preview
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        lbl_preview = QLabel("Xem Trước Tính Toán")
        lbl_preview.setProperty("heading", True)
        right_layout.addWidget(lbl_preview)
        
        # Breakdown table
        self.breakdown_table = QTableWidget()
        self.breakdown_table.setColumnCount(2)
        self.breakdown_table.setHorizontalHeaderLabels(["Hạng Mục", "Số Tiền"])
        self.breakdown_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.breakdown_table.verticalHeader().setVisible(False)
        self.breakdown_table.setShowGrid(False)
        right_layout.addWidget(self.breakdown_table)
        
        # Net result display
        net_frame = QFrame()
        net_frame.setStyleSheet("background: #F1F5F9; border-radius: 8px; padding: 15px;")
        net_layout = QVBoxLayout(net_frame)
        
        lbl_net_title = QLabel("THỰC NHẬN")
        lbl_net_title.setStyleSheet("font-size: 14px; color: #64748B; font-weight: bold;")
        
        self.lbl_net_amount = QLabel("0 đ")
        self.lbl_net_amount.setStyleSheet("font-size: 28px; font-weight: bold; color: #059669;")
        
        net_layout.addWidget(lbl_net_title)
        net_layout.addWidget(self.lbl_net_amount)
        right_layout.addWidget(net_frame)
        
        # Add panels to main layout
        main_layout.addWidget(left_panel, 1)
        main_layout.addWidget(right_panel, 1)
        
        self.update_preview()
    
    def update_preview(self):
        try:
            bid = float(self.inp_bid.text() or 0)
        except:
            bid = 0.0
        
        winner_id = self.cb_winner.currentData()
        
        # Validate
        warnings = []
        if bid > self.group.amountPerShare:
            warnings.append(f"⚠️ Tiền thăm ({bid:,.0f}) vượt quá vốn ({self.group.amountPerShare:,.0f})")
        
        if bid < 0:
            warnings.append("⚠️ Tiền thăm không thể âm")
            bid = 0
        
        # Calculate
        calc = FinanceService.calculate_payout(self.group, self.group.currentPeriod, bid, winner_id, self.all_transactions)
        
        if calc.deductions > 0:
            warnings.append(f"💰 Người thắng có nợ cũ: {calc.deductions:,.0f} đ")
        
        # Update warning
        if warnings:
            self.lbl_warning.setText("\n".join(warnings))
            self.lbl_warning.show()
        else:
            self.lbl_warning.hide()
        
        # Update breakdown table
        self.breakdown_table.setRowCount(0)
        
        def add_row(label, value, color="#334155", bold=False):
            row = self.breakdown_table.rowCount()
            self.breakdown_table.insertRow(row)
            
            lbl_item = QTableWidgetItem(label)
            val_item = QTableWidgetItem(f"{value:,.0f} đ")
            val_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            val_item.setForeground(QColor(color))
            
            if bold:
                font = val_item.font()
                font.setBold(True)
                val_item.setFont(font)
                lbl_item.setFont(font)
            
            self.breakdown_table.setItem(row, 0, lbl_item)
            self.breakdown_table.setItem(row, 1, val_item)
        
        add_row(f"Chân Sống ({calc.liveMembers} × {self.group.amountPerShare - bid:,.0f})", 
                calc.liveMembers * calc.amountPerLive)
        add_row(f"Chân Chết ({calc.deadMembers} × {self.group.amountPerShare:,.0f})", 
                calc.deadMembers * calc.amountPerDead)
        add_row("─────────────────", 0, "#94A3B8")
        add_row("Tổng Gom", calc.totalPot, "#059669", True)
        add_row("Trừ: Tiền Thảo", -calc.commission, "#EF4444")
        add_row("Trừ: Nợ Cũ", -calc.deductions, "#EF4444")
        
        # Update net amount
        net_color = "#059669" if calc.netReceived >= 0 else "#EF4444"
        self.lbl_net_amount.setText(f"{calc.netReceived:,.0f} đ")
        self.lbl_net_amount.setStyleSheet(f"font-size: 28px; font-weight: bold; color: {net_color};")
        
        # Enable confirm button
        self.btn_confirm.setEnabled(bid > 0 and calc.netReceived >= 0)
        
        self.calc_result = calc
    
    def confirm(self):
        try:
            bid = float(self.inp_bid.text())
        except:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập số tiền thăm hợp lệ.")
            return
        
        winner_id = self.cb_winner.currentData()
        
        self.result_data = {
            'winner_id': winner_id,
            'bid': bid,
            'calc': self.calc_result
        }
        self.accept()

# --- MAIN TAB ---

class HuiListTab(QWidget):
    def __init__(self, data: AppState, save_callback):
        super().__init__()
        self.data = data
        self.save_callback = save_callback
        
        self.stack = QStackedWidget()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.stack)
        
        # Page 1: List
        self.page_list = QWidget()
        self.init_list_page()
        self.stack.addWidget(self.page_list)
        
        # Page 2: Detail
        self.page_detail = QWidget()
        self.detail_layout = QVBoxLayout(self.page_detail)
        self.detail_layout.setSpacing(15)
        self.stack.addWidget(self.page_detail)
        
        self.current_group: HuiGroup = None

    def init_list_page(self):
        layout = QVBoxLayout(self.page_list)
        layout.setSpacing(15)
        
        # Header
        top = QHBoxLayout()
        
        lbl_icon = QLabel()
        lbl_icon.setPixmap(qta.icon('fa5s.list-ul', color='#334155').pixmap(24,24))

        lbl = QLabel("Danh Sách Dây Hụi")
        lbl.setProperty("heading", True)
        
        btn_add = QPushButton("Tạo Dây Mới")
        btn_add.setIcon(qta.icon('fa5s.plus', color='white'))
        btn_add.setProperty("primary", True)
        btn_add.clicked.connect(self.open_create_dialog)
        
        top.addWidget(lbl_icon)
        top.addWidget(lbl)
        top.addStretch()
        top.addWidget(btn_add)
        layout.addLayout(top)
        
        # Table
        self.table_list = QTableWidget()
        self.table_list.setColumnCount(6)
        self.table_list.setHorizontalHeaderLabels(["Dây Hụi", "Loại", "Số Tiền", "Kỳ Hiện Tại", "Trạng Thái", "Hành Động"])
        self.table_list.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_list.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table_list.setAlternatingRowColors(True)
        self.table_list.setShowGrid(False)
        self.table_list.verticalHeader().setVisible(False)
        
        layout.addWidget(self.table_list)
        
    def refresh(self):
        # Refresh list
        self.table_list.setRowCount(0)
        for g in self.data.groups:
            row = self.table_list.rowCount()
            self.table_list.insertRow(row)
            
            # Name
            name_item = QTableWidgetItem(g.name)
            font = name_item.font()
            font.setBold(True)
            name_item.setFont(font)
            self.table_list.setItem(row, 0, name_item)
            
            self.table_list.setItem(row, 1, QTableWidgetItem(g.type))
            self.table_list.setItem(row, 2, QTableWidgetItem(f"{g.amountPerShare:,.0f}"))
            
            # Period Badge-ish
            period_item = QTableWidgetItem(f"Kỳ {g.currentPeriod}")
            period_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table_list.setItem(row, 3, period_item)
            
            # Status
            status_item = QTableWidgetItem(g.status)
            if g.status == HuiStatus.ACTIVE.value:
                status_item.setForeground(QColor("#059669"))
            else:
                status_item.setForeground(QColor("#64748B"))
            self.table_list.setItem(row, 4, status_item)
            
            # Action
            btn_detail = QPushButton("Chi tiết")
            btn_detail.setIcon(qta.icon('fa5s.arrow-right', color='#475569'))
            btn_detail.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_detail.clicked.connect(lambda checked, grp=g: self.open_detail(grp))
            self.table_list.setCellWidget(row, 5, btn_detail)
            
        # Refresh detail if open
        if self.current_group:
            self.render_detail(self.current_group)

    def open_create_dialog(self):
        dlg = CycleSetupWizard(self, self.data.members)
        if dlg.exec():
            d = dlg.result_data
            new_group = HuiGroup(
                id=str(int(time.time())),
                name=d['name'],
                type=d['type'],
                amountPerShare=d['amount'],
                commissionRate=d['commission'],
                commissionType=d['commissionType'],
                totalMembers=len(d['members']),
                startDate=datetime.now().isoformat(),
                status=HuiStatus.ACTIVE.value,
                members=d['members'],
                currentPeriod=d['currentPeriod']
            )
            self.data.groups.append(new_group)
            
            # Handle Historical Transactions
            for pw in d['pastWinners']:
                # Calculate what the total pot was (simplified for history)
                # Actually, FinanceService.calculate_payout provides the real logic, 
                # but for history we might not have all previous transactions recorded yet.
                # Let's create a COLLECT transaction for the history.
                
                # We need to approximate the payout for history if we don't have past bids recorded for OTHER people.
                # Actually d['pastWinners'] has the bid for that period.
                
                # To be accurate, we should ideally run calculate_payout, 
                # but it requires transactions that don't exist yet. 
                # So we just record the winner and bid.
                
                new_tx = Transaction(
                    id=f"hist-col-{int(time.time())}-{pw['period']}",
                    huiGroupId=new_group.id,
                    memberId=pw['memberId'],
                    type='COLLECT',
                    amount=0, # Will be calculated by FinanceService later or kept minimal
                    bidAmount=pw['bid'],
                    netAmount=0,
                    date=datetime.now().isoformat(),
                    period=pw['period'],
                    note='Dữ liệu lịch sử (Hốt hụi)'
                )
                self.data.transactions.append(new_tx)

            self.save_callback()
            self.refresh()

    def open_detail(self, group: HuiGroup):
        self.current_group = group
        self.render_detail(group)
        self.stack.setCurrentWidget(self.page_detail)

    def go_back(self):
        self.current_group = None
        self.stack.setCurrentWidget(self.page_list)

    def render_detail(self, group: HuiGroup):
        # Clear layout
        while self.detail_layout.count():
            item = self.detail_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()
            
        # Header Row
        top = QHBoxLayout()
        btn_back = QPushButton("Quay lại")
        btn_back.setIcon(qta.icon('fa5s.arrow-left'))
        btn_back.setFixedWidth(100)
        btn_back.clicked.connect(self.go_back)
        
        lbl_title = QLabel(f"{group.name}")
        lbl_title.setProperty("heading", True)
        lbl_title.setStyleSheet("margin-bottom: 0px;")
        
        top.addWidget(btn_back)
        top.addSpacing(10)
        top.addWidget(lbl_title)
        top.addStretch()
        
        # Info Badge
        lbl_info = QLabel(f"Kỳ {group.currentPeriod} • {group.totalMembers} Chân • {group.amountPerShare:,.0f} đ/phần")
        lbl_info.setStyleSheet("color: #64748B; font-size: 14px; font-weight: 500; margin-left:110px;")
        
        self.detail_layout.addLayout(top)
        self.detail_layout.addWidget(lbl_info)
        
        # Divider
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        line.setStyleSheet("color: #E2E8F0;")
        self.detail_layout.addWidget(line)
        
        # Check Winner of current period
        txs = [t for t in self.data.transactions if t.huiGroupId == group.id]
        collector_tx = next((t for t in txs if t.period == group.currentPeriod and t.type == 'COLLECT'), None)
        
        # Actions Row
        actions = QHBoxLayout()
        if not collector_tx:
            lbl_status = QLabel("Trạng thái: Chưa đấu")
            lbl_status.setStyleSheet("color: #F59E0B; font-weight: bold;")
            
            btn_collect = QPushButton("Mở Hốt Hụi (Đấu)")
            btn_collect.setIcon(qta.icon('fa5s.gavel', color='white'))
            btn_collect.setProperty("primary", True)
            btn_collect.clicked.connect(lambda: self.do_collect(group))
            
            actions.addWidget(lbl_status)
            actions.addStretch()
            actions.addWidget(btn_collect)
        else:
            winner_name = next((m.name for m in self.data.members if m.id == collector_tx.memberId), "???")
            
            icon_win = QLabel()
            icon_win.setPixmap(qta.icon('fa5s.trophy', color='#F59E0B').pixmap(24,24))
            
            lbl_winner = QLabel(f"Người Hốt: {winner_name}")
            lbl_winner.setStyleSheet("color: #1E293B; font-weight: bold; font-size: 16px;")
            
            lbl_bid = QLabel(f"Tiền Thăm: {collector_tx.bidAmount:,.0f} đ")
            lbl_bid.setStyleSheet("color: #EF4444; font-weight: bold; margin-left: 10px;")

            actions.addWidget(icon_win)
            actions.addWidget(lbl_winner)
            actions.addWidget(lbl_bid)
            actions.addStretch()
            
        self.detail_layout.addLayout(actions)
        
        # Tracking Table (Checklist)
        plan = FinanceService.get_contribution_plan(
            group, 
            group.currentPeriod, 
            collector_tx.bidAmount if collector_tx else 0,
            collector_tx.memberId if collector_tx else None,
            self.data.transactions
        )
        
        table = QTableWidget()
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(["Thành Viên", "Phải Đóng", "Đã Đóng", "Còn Nợ (Balance)", "Hành Động"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.setAlternatingRowColors(True)
        table.setShowGrid(False)
        table.verticalHeader().setVisible(False)
        table.setRowCount(len(plan))
        
        for i, item in enumerate(plan):
            member = next((m for m in self.data.members if m.id == item.memberId), None)
            m_name = member.name if member else "Unknown"
            
            is_winner = (collector_tx and collector_tx.memberId == item.memberId)
            
            # Name Column
            name_widget = QWidget()
            name_layout = QVBoxLayout(name_widget)
            name_layout.setContentsMargins(5, 5, 5, 5)
            name_lbl = QLabel(m_name)
            name_lbl.setStyleSheet("font-weight: bold;")
            sub_lbl = QLabel(f"{item.liveSlots} Sống / {item.deadSlots} Chết")
            sub_lbl.setStyleSheet("color: #64748B; font-size: 11px;")
            name_layout.addWidget(name_lbl)
            name_layout.addWidget(sub_lbl)
            table.setCellWidget(i, 0, name_widget)
            
            # Amount Helper
            def money_item(val, color="#334155", bold=False):
                it = QTableWidgetItem(f"{val:,.0f}")
                it.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                it.setForeground(QColor(color))
                if bold:
                    f = it.font()
                    f.setBold(True)
                    it.setFont(f)
                return it

            table.setItem(i, 1, money_item(item.requiredAmount))
            
            paid_color = "#059669" if item.paidAmount >= item.requiredAmount and item.requiredAmount > 0 else "#334155"
            table.setItem(i, 2, money_item(item.paidAmount, paid_color))
            
            balance_color = "#EF4444" if item.remainingAmount > 0 else "#64748B"
            table.setItem(i, 3, money_item(item.remainingAmount, balance_color, bold=(item.remainingAmount > 0)))
            
            # Action Button
            if not is_winner and item.remainingAmount > 0:
                btn_pay = QPushButton("Đóng")
                btn_pay.setIcon(qta.icon('fa5s.money-bill-wave', color='#059669'))
                btn_pay.setStyleSheet("border: 1px solid #059669; color: #059669;")
                btn_pay.clicked.connect(lambda checked, it=item, m=member: self.do_payment(group, it, m))
                table.setCellWidget(i, 4, btn_pay)
            elif is_winner:
                lbl_w = QLabel("Người Hốt")
                lbl_w.setAlignment(Qt.AlignmentFlag.AlignCenter)
                lbl_w.setStyleSheet("color: #F59E0B; font-weight: bold;")
                table.setCellWidget(i, 4, lbl_w)
            else:
                lbl_d = QLabel("Hoàn tất")
                lbl_d.setAlignment(Qt.AlignmentFlag.AlignCenter)
                lbl_d.setStyleSheet("color: #059669;")
                table.setCellWidget(i, 4, lbl_d)
                
        table.resizeRowsToContents()
        self.detail_layout.addWidget(table)
        
    def do_collect(self, group):
        dlg = BiddingDialog(self, group, self.data.members, self.data.transactions)
        if dlg.exec():
            result = dlg.result_data
            
            # Add Transaction
            new_tx = Transaction(
                id=str(int(time.time())),
                huiGroupId=group.id,
                memberId=result['winner_id'],
                type='COLLECT',
                amount=result['calc'].totalPot,
                bidAmount=result['bid'],
                netAmount=result['calc'].netReceived,
                date=datetime.now().isoformat(),
                period=group.currentPeriod,
                note='Hốt hụi'
            )
            self.data.transactions.append(new_tx)
            
            # Add Audit Log
            log = AuditService.create_collect_log(group, result['winner_id'], result['bid'], result['calc'])
            self.data.auditLogs.append(log)
            
            self.save_callback()

    def do_payment(self, group, item, member):
        amount, ok = QInputDialog.getInt(self, "Đóng Tiền", 
                                       f"Ghi nhận đóng tiền cho {member.name}:", 
                                       int(item.remainingAmount), 0, 1000000000, 1000)
        if ok and amount > 0:
            new_tx = Transaction(
                id=f"pay-{int(time.time())}",
                huiGroupId=group.id,
                memberId=member.id,
                type='CONTRIBUTE',
                amount=float(amount),
                date=datetime.now().isoformat(),
                period=group.currentPeriod,
                note='Đóng tiền'
            )
            self.data.transactions.append(new_tx)
            
            # Audit
            log = AuditService.create_payment_log(group, member.id, item.requiredAmount, amount, item.remainingAmount - amount)
            self.data.auditLogs.append(log)
            
            self.save_callback()
