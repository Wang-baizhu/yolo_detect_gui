from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QTableWidget, 
                           QTableWidgetItem, QHeaderView, QDialogButtonBox)
from PyQt5.QtCore import Qt
from .styles import get_button_style

class LabelEditorDialog(QDialog):
    def __init__(self, class_names, custom_names, parent=None):
        super().__init__(parent)
        self.setWindowTitle("编辑标签名称")
        self.setGeometry(200, 200, 500, 400)
        
        self.class_names = class_names
        self.custom_names = custom_names.copy()
        
        self.init_ui()
        
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout()
        
        # 创建表格
        self.table = QTableWidget(len(self.class_names), 2)
        self.table.setHorizontalHeaderLabels(["原始标签", "显示名称"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        # 设置表格样式
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: white; /* 背景改为白色 */
                color: black; /* 字体改为黑色 */
                gridline-color: #ccc; /* 网格线颜色改为浅灰色 */
                border: 1px solid #ccc; /* 边框颜色改为浅灰色 */
                border-radius: 4px; /* 边框圆角 */
            }
            QTableWidget::item {
                padding: 5px; /* 单元格内边距 */
            }
            QTableWidget::item:selected {
                background-color: #e0e0e0; /* 选中项背景改为浅灰色 */
                color: black; /* 选中项字体保持黑色 */
            }
            QHeaderView::section {
                background-color: #f0f0f0; /* 表头背景改为浅灰色 */
                color: black; /* 表头字体改为黑色 */
                padding: 5px; /* 表头内边距 */
                border: 1px solid #ccc; /* 表头边框颜色改为浅灰色 */
            }
        """)
        
        # 填充表格数据
        for idx, class_name in enumerate(self.class_names):
            # 原始标签（只读）
            original_item = QTableWidgetItem(class_name)
            original_item.setFlags(original_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(idx, 0, original_item)
            
            # 自定义标签
            custom_name = self.custom_names.get(class_name, class_name)
            custom_item = QTableWidgetItem(custom_name)
            self.table.setItem(idx, 1, custom_item)
        
        layout.addWidget(self.table)
        
        # 添加按钮
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        # 设置按钮样式
        button_box.setStyleSheet(get_button_style())
        
        layout.addWidget(button_box)
        self.setLayout(layout)
    
    def get_custom_names(self):
        """获取自定义标签名称"""
        custom_names = {}
        for idx in range(self.table.rowCount()):
            original = self.table.item(idx, 0).text()
            custom = self.table.item(idx, 1).text()
            if original != custom:  # 只保存被修改的标签
                custom_names[original] = custom
        return custom_names 