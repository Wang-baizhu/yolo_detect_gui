from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtCore import Qt

def get_dark_palette():
    """返回深色主题调色板"""
    palette = QPalette()
    
    # 设置窗口背景色
    palette.setColor(QPalette.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.WindowText, Qt.white)
    
    # 设置按钮颜色
    palette.setColor(QPalette.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ButtonText, Qt.white)
    
    # 设置输入框颜色
    palette.setColor(QPalette.Base, QColor(25, 25, 25))
    palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    
    # 设置文本颜色
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Disabled, QPalette.Text, QColor(128, 128, 128))
    
    # 设置高亮颜色
    palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.HighlightedText, Qt.black)
    
    return palette

def get_window_style():
    """返回窗口样式"""
    return """
        QMainWindow {
            background-color: #2c2c2c;
        }
        QMainWindow::title {
            background-color: #1a1a1a;
            color: white;
            padding: 5px;
        }
        QMenuBar {
            background-color: #1a1a1a;
            color: white;
        }
        QStatusBar {
            background-color: #1a1a1a;
            color: white;
        }
    """

def get_button_style():
    """返回按钮样式"""
    return """
        QPushButton {
            background-color: #2c2c2c;
            border: 1px solid #555;
            border-radius: 4px;
            color: white;
            padding: 5px 15px;
            min-height: 25px;
        }
        QPushButton:hover {
            background-color: #3c3c3c;
            border: 1px solid #666;
        }
        QPushButton:pressed {
            background-color: #444;
        }
        QPushButton:disabled {
            background-color: #222;
            border: 1px solid #444;
            color: #666;
        }
    """

def get_combobox_style():
    """返回下拉框样式"""
    return """
        QComboBox {
            background-color: #2c2c2c;
            border: 1px solid #555;
            border-radius: 4px;
            color: white;
            padding: 5px;
            min-height: 25px;
        }
        QComboBox:hover {
            border: 1px solid #666;
        }
        QComboBox::drop-down {
            border: none;
            width: 20px;
        }
        QComboBox::down-arrow {
            image: url(src/ui/assets/down_arrow.png);
            width: 12px;
            height: 12px;
        }
        QComboBox QAbstractItemView {
            background-color: #2c2c2c;
            color: white;
            selection-background-color: #3c7fb1;
            selection-color: white;
            border: 1px solid #555;
        }
    """

def get_text_edit_style():
    """返回文本编辑框样式"""
    return """
        QTextEdit {
            background-color: #1e1e1e;
            border: 1px solid #555;
            border-radius: 4px;
            color: white;
            padding: 5px;
            font-family: Consolas, monospace;
        }
    """

def get_label_style():
    """返回标签样式"""
    return """
        QLabel {
            color: white;
            font-size: 12px;
        }
    """ 