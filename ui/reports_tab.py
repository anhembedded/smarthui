from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QTextEdit, QSplitter)
from PySide6.QtCore import Qt
from data_models import AppState
from services.finance_service import FinanceService
import json

# Try importing matplotlib, fail gracefully if not present
try:
    from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

class ReportsTab(QWidget):
    def __init__(self, data: AppState):
        super().__init__()
        self.data = data
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout(self)
        
        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)
        
        # Left: Charts
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        lbl_chart = QLabel("Dự Phóng Dòng Tiền (Cashflow)")
        lbl_chart.setProperty("heading", True)
        left_layout.addWidget(lbl_chart)
        
        if HAS_MATPLOTLIB:
            self.figure = Figure(figsize=(5, 4), dpi=100)
            self.canvas = FigureCanvas(self.figure)
            left_layout.addWidget(self.canvas)
        else:
            left_layout.addWidget(QLabel("Matplotlib not installed. Cannot show chart."))
            
        splitter.addWidget(left_widget)
        
        # Right: Logs
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        lbl_logs = QLabel("AI Audit Logs (JSON)")
        lbl_logs.setProperty("heading", True)
        right_layout.addWidget(lbl_logs)
        
        self.log_viewer = QTextEdit()
        self.log_viewer.setReadOnly(True)
        self.log_viewer.setStyleSheet("background-color: #1f2937; color: #10b981; font-family: Consolas;")
        right_layout.addWidget(self.log_viewer)
        
        btn_refresh = QPushButton("Làm mới / Chạy Audit Giả Lập")
        btn_refresh.clicked.connect(self.refresh)
        right_layout.addWidget(btn_refresh)
        
        splitter.addWidget(right_widget)
        splitter.setSizes([400, 400])

    def refresh(self):
        # 1. Update Chart
        if HAS_MATPLOTLIB:
            self.figure.clear()
            ax = self.figure.add_subplot(111)
            
            projection = FinanceService.calculate_cashflow_projection(self.data.groups)
            names = [p['name'] for p in projection]
            ins = [p['in'] for p in projection]
            outs = [p['out'] for p in projection]
            
            x = range(len(names))
            width = 0.35
            
            ax.bar([i - width/2 for i in x], ins, width, label='Thu', color='#10b981')
            ax.bar([i + width/2 for i in x], outs, width, label='Chi', color='#f43f5e')
            
            ax.set_xticks(x)
            ax.set_xticklabels(names)
            ax.legend()
            ax.set_title("Dòng tiền 6 tháng tới")
            
            self.canvas.draw()
            
        # 2. Update Logs
        logs_text = ""
        for log in reversed(self.data.auditLogs):
            logs_text += f"[{log.timestamp}] {log.action}\n"
            logs_text += json.dumps(log.to_dict(), indent=2, ensure_ascii=False)
            logs_text += "\n" + "-"*40 + "\n"
            
        if not logs_text:
            logs_text = "// Chưa có log nào."
            
        self.log_viewer.setText(logs_text)
