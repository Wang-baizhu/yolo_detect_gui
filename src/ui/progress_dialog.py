from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QProgressBar
from PyQt5.QtCore import Qt

class ProgressDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("安装进度")
        self.setFixedSize(300, 100)
        self.setWindowFlags(Qt.Window | Qt.CustomizeWindowHint | Qt.WindowTitleHint)
        
        # 创建布局
        layout = QVBoxLayout()
        
        # 创建标签
        self.status_label = QLabel("准备中...")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 12px;
                margin-bottom: 10px;
            }
        """)
        
        # 创建进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #555;
                border-radius: 4px;
                text-align: center;
                background-color: #2c2c2c;
                color: white;
            }
            QProgressBar::chunk {
                background-color: #3c7fb1;
                width: 10px;
            }
        """)
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(0)  # 设置为0表示不确定进度
        
        # 添加到布局
        layout.addWidget(self.status_label)
        layout.addWidget(self.progress_bar)
        
        self.setLayout(layout)
        
        # 设置窗口样式
        self.setStyleSheet("""
            QDialog {
                background-color: #1a1a1a;
                border: 1px solid #555;
            }
        """)
        
    def set_status(self, text):
        """更新状态文本"""
        self.status_label.setText(text)
        
    def set_progress(self, value, maximum=100):
        """设置进度值"""
        if maximum == 0:
            self.progress_bar.setMaximum(0)  # 不确定进度
        else:
            self.progress_bar.setMaximum(maximum)
            self.progress_bar.setValue(value) 