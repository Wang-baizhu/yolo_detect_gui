import sys
import cv2
import numpy as np
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QPushButton, QLabel, QFileDialog, QComboBox,
                           QDialog, QTableWidget, QTableWidgetItem, QHeaderView, 
                           QDialogButtonBox, QTextEdit, QSplitter)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap
from ultralytics import YOLO
import mss
import mss.tools
from PIL import Image
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from window_utils import get_window_list, get_window_rect
import torch
import json
import os
import time

class LabelEditorDialog(QDialog):
    def __init__(self, class_names, custom_names, parent=None):
        super().__init__(parent)
        self.setWindowTitle("编辑标签名称")
        self.setGeometry(200, 200, 500, 400)
        
        self.class_names = class_names
        self.custom_names = custom_names.copy()
        
        layout = QVBoxLayout()
        
        # 创建表格
        self.table = QTableWidget(len(class_names), 2)
        self.table.setHorizontalHeaderLabels(["原始标签", "显示名称"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        # 填充表格数据
        for idx, class_name in enumerate(class_names):
            self.table.setItem(idx, 0, QTableWidgetItem(class_name))
            custom_name = custom_names.get(class_name, class_name)
            self.table.setItem(idx, 1, QTableWidgetItem(custom_name))
        
        layout.addWidget(self.table)
        
        # 添加按钮
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
    
    def get_custom_names(self):
        custom_names = {}
        for idx in range(self.table.rowCount()):
            original = self.table.item(idx, 0).text()
            custom = self.table.item(idx, 1).text()
            custom_names[original] = custom
        return custom_names

class DetectionThread(QThread):
    detection_complete = pyqtSignal(np.ndarray, list)
    log_message = pyqtSignal(str)
    
    def __init__(self, model):
        super().__init__()
        self.model = model
        self.running = False
        self.detect_mode = None
        self.selected_window = None
        self.selected_monitor = 0
        self.custom_labels = {}
    
    def set_mode(self, mode, window_hwnd=None):
        self.detect_mode = mode
        self.selected_window = window_hwnd
        if mode == 'fullscreen':
            self.log_message.emit(f"开始全屏检测...")
        elif mode == 'window' and window_hwnd:
            self.log_message.emit(f"开始窗口检测: {self.selected_window_title}")
    
    def set_custom_labels(self, custom_labels):
        self.custom_labels = custom_labels
    
    def set_window_title(self, title):
        self.selected_window_title = title
    
    def stop(self):
        self.running = False
        
    def run(self):
        self.running = True
        self.log_message.emit(f"检测线程已启动 (模式: {self.detect_mode})")
        
        # 计算FPS
        frame_count = 0
        start_time = time.time()
        
        while self.running:
            try:
                with mss.mss() as screen:
                    if self.detect_mode == 'fullscreen':
                        if len(screen.monitors) > 0:
                            screenshot = screen.grab(screen.monitors[0])
                        else:
                            continue
                    elif self.detect_mode == 'window' and self.selected_window:
                        window_rect = get_window_rect(self.selected_window)
                        if window_rect:
                            screenshot = screen.grab(window_rect)
                        else:
                            self.log_message.emit("警告: 无法获取窗口区域，请确保窗口未被最小化")
                            continue
                    else:
                        continue
            except Exception as e:
                self.log_message.emit(f"截图错误: {str(e)}")
                continue
                
            frame = np.array(screenshot)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
            
            try:
                results = self.model(frame)
            except Exception as e:
                self.log_message.emit(f"检测错误: {str(e)}")
                continue
                
            detected_labels = []
            
            for result in results:
                boxes = result.boxes
                for box in boxes:
                    x1, y1, x2, y2 = box.xyxy[0]
                    conf = box.conf[0]
                    cls = box.cls[0]
                    
                    # 获取原始标签名称
                    original_label = result.names[int(cls)]
                    
                    # 使用自定义标签名称（如果存在），否则使用原始名称
                    display_label = self.custom_labels.get(original_label, original_label)
                    
                    cv2.rectangle(frame, 
                                (int(x1), int(y1)), 
                                (int(x2), int(y2)), 
                                (0, 255, 0), 2)
                    
                    label = f'{display_label} {conf:.2f}'
                    detected_labels.append(display_label)
                    cv2.putText(frame, label, (int(x1), int(y1)-10), 
                              cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            # 计算FPS
            frame_count += 1
            if frame_count % 10 == 0:
                fps = frame_count / (time.time() - start_time)
                self.log_message.emit(f"检测帧率: {fps:.2f} FPS")
                frame_count = 0
                start_time = time.time()
            
            self.detection_complete.emit(frame, detected_labels)
            self.msleep(50)  # 限制检测频率

class YoloDetector(QMainWindow):
    def __init__(self):
        super().__init__()
        self.model = None
        self.custom_labels = {}
        self.detection_thread = None

        self.is_detecting = False
        self.detect_mode = None
        self.selected_window = None
        
        self.initUI()
        
        # 初始化设备信息
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.log_message(f"使用设备: {self.device}")
        
        # 尝试加载默认模型
        self.load_model('yolov8s.pt')

    def initUI(self):
        self.setWindowTitle('YOLO目标检测')
        self.setGeometry(100, 100, 1200, 800)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)  # 主布局改为水平布局

        # 左侧区域 - 检测显示
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        # 检测显示区域
        self.display_label = QLabel()
        self.display_label.setAlignment(Qt.AlignCenter)
        self.display_label.setMinimumSize(640, 480)
        left_layout.addWidget(self.display_label, 3)  # 占据3份空间
        
        # 底部按钮区域
        button_layout = QHBoxLayout()
        
        self.btn_fullscreen = QPushButton('全屏检测', self)
        self.btn_fullscreen.clicked.connect(self.toggle_fullscreen_detection)
        self.btn_fullscreen.setEnabled(False)
        
        self.btn_window = QPushButton('窗口检测', self)
        self.btn_window.clicked.connect(self.toggle_window_detection)
        self.btn_window.setEnabled(False)
        
        self.btn_image = QPushButton('图片检测', self)
        self.btn_image.clicked.connect(self.detect_image)
        self.btn_image.setEnabled(False)
        
        self.btn_edit_labels = QPushButton('编辑标签名称', self)
        self.btn_edit_labels.clicked.connect(self.edit_labels)
        self.btn_edit_labels.setEnabled(False)
        
        self.btn_load_model = QPushButton('加载模型', self)
        self.btn_load_model.clicked.connect(self.load_custom_model)
        
        # 窗口选择下拉框
        self.window_combo = QComboBox(self)
        self.update_window_list()
        self.window_combo.currentIndexChanged.connect(self.on_window_selected)
        self.window_combo.setEnabled(False)

        button_layout.addWidget(self.btn_load_model)
        button_layout.addWidget(self.btn_fullscreen)
        button_layout.addWidget(self.btn_window)
        button_layout.addWidget(self.window_combo)
        button_layout.addWidget(self.btn_image)
        button_layout.addWidget(self.btn_edit_labels)
        
        left_layout.addLayout(button_layout, 1)  # 占据1份空间

        # 右侧区域 - 信息面板
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        # 检测结果区域
        results_group = QWidget()
        results_layout = QVBoxLayout(results_group)
        
        results_title = QLabel("检测结果")
        results_title.setAlignment(Qt.AlignCenter)
        results_title.setStyleSheet("font-weight: bold; font-size: 14px;")
        results_layout.addWidget(results_title)
        
        self.labels_area = QLabel()
        self.labels_area.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.labels_area.setWordWrap(True)
        self.labels_area.setStyleSheet("""
            border: 1px solid #ccc; 
            padding: 10px; 
            background-color: #f9f9f9;
            min-height: 150px;
        """)
        results_layout.addWidget(self.labels_area)
        
        right_layout.addWidget(results_group, 1)  # 占据1份空间
        
        # 日志区域
        log_group = QWidget()
        log_layout = QVBoxLayout(log_group)
        
        log_title = QLabel("运行日志")
        log_title.setAlignment(Qt.AlignCenter)
        log_title.setStyleSheet("font-weight: bold; font-size: 14px;")
        log_layout.addWidget(log_title)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("""
            background-color: #f0f0f0; 
            border: 1px solid #ccc;
            font-family: Consolas, monospace;
            font-size: 10pt;
        """)
        log_layout.addWidget(self.log_text)
        
        # 添加清空日志按钮
        btn_clear_log = QPushButton("清空日志")
        btn_clear_log.clicked.connect(self.clear_log)
        log_layout.addWidget(btn_clear_log)
        
        right_layout.addWidget(log_group, 2)  # 占据2份空间
        
        # 将左右区域添加到主布局
        main_layout.addWidget(left_widget, 7)  # 左侧占70%
        main_layout.addWidget(right_widget, 3)  # 右侧占30%
        
        # 初始日志信息
        self.log_message("程序已启动")
        self.log_message(f"设备类型: {'GPU' if torch.cuda.is_available() else 'CPU'}")

    def load_model(self, model_path):
        """加载模型"""
        try:
            self.log_message(f"正在加载模型: {model_path}")
            self.model = YOLO(model_path)
            self.model.to(self.device)
            
            # 初始化检测线程
            if self.detection_thread:
                self.detection_thread.stop()
                self.detection_thread.wait()
                
            self.detection_thread = DetectionThread(self.model)
            self.detection_thread.detection_complete.connect(self.display_frame)
            self.detection_thread.log_message.connect(self.log_message)
            
            # 加载自定义标签
            self.custom_labels = self.load_custom_labels()
            self.detection_thread.set_custom_labels(self.custom_labels)
            
            # 启用按钮
            self.btn_fullscreen.setEnabled(True)
            self.btn_window.setEnabled(True)
            self.btn_image.setEnabled(True)
            self.btn_edit_labels.setEnabled(True)
            self.window_combo.setEnabled(True)
            
            self.log_message(f"模型加载成功")
            self.log_message(f"检测类别数: {len(self.model.names)}")
            self.log_message(f"模型路径: {model_path}")
            
            # 更新标签编辑器
            if hasattr(self, 'label_editor_dialog'):
                self.label_editor_dialog = None
                
            return True
        except Exception as e:
            self.log_message(f"模型加载失败: {str(e)}")
            self.model = None
            # 禁用按钮
            self.btn_fullscreen.setEnabled(False)
            self.btn_window.setEnabled(False)
            self.btn_image.setEnabled(False)
            self.btn_edit_labels.setEnabled(False)
            self.window_combo.setEnabled(False)
            return False

    def load_custom_model(self):
        """加载自定义模型"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择YOLO模型文件",
            "",
            "模型文件 (*.pt)"
        )
        if file_path:
            if self.is_detecting:
                self.stop_detection()
            self.load_model(file_path)

    def clear_log(self):
        """清空日志"""
        self.log_text.clear()

    def log_message(self, message):
        """添加日志消息"""
        timestamp = time.strftime("%H:%M:%S", time.localtime())
        log_entry = f"[{timestamp}] {message}"
        self.log_text.append(log_entry)
        # 自动滚动到底部
        self.log_text.verticalScrollBar().setValue(
            self.log_text.verticalScrollBar().maximum()
        )

    def load_custom_labels(self):
        """从文件加载自定义标签名称"""
        custom_labels = {}
        try:
            if os.path.exists('custom_labels.json'):
                with open('custom_labels.json', 'r') as f:
                    custom_labels = json.load(f)
                self.log_message("已加载自定义标签名称")
        except Exception as e:
            self.log_message(f"加载自定义标签失败: {str(e)}")
        return custom_labels

    def save_custom_labels(self):
        """保存自定义标签名称到文件"""
        try:
            with open('custom_labels.json', 'w') as f:
                json.dump(self.custom_labels, f)
            self.log_message("自定义标签已保存")
        except Exception as e:
            self.log_message(f"保存自定义标签失败: {str(e)}")

    def edit_labels(self):
        """打开标签编辑对话框"""
        if self.model is None:
            self.log_message("错误: 未加载模型，无法编辑标签")
            return
            
        # 获取模型的原始标签名称
        original_labels = list(self.model.names.values())
        
        # 创建并显示对话框
        dialog = LabelEditorDialog(original_labels, self.custom_labels, self)
        if dialog.exec_() == QDialog.Accepted:
            self.custom_labels = dialog.get_custom_names()
            self.detection_thread.set_custom_labels(self.custom_labels)
            self.save_custom_labels()
            self.log_message("标签名称已更新")

    def update_window_list(self):
        self.window_combo.clear()
        windows = get_window_list()
        for hwnd, title in windows:
            self.window_combo.addItem(title, hwnd)

    def on_window_selected(self, index):
        if index >= 0:
            hwnd = self.window_combo.itemData(index)
            title = self.window_combo.itemText(index)
            if self.is_detecting and self.detect_mode == 'window':
                self.detection_thread.set_window_title(title)
                self.detection_thread.set_mode('window', hwnd)
                self.log_message(f"已选择窗口: {title}")

    def toggle_fullscreen_detection(self):
        if self.model is None:
            self.log_message("错误: 未加载模型，请先加载模型")
            return
            
        if not self.is_detecting or self.detect_mode != 'fullscreen':
            self.is_detecting = True
            self.detect_mode = 'fullscreen'
            self.btn_fullscreen.setText('停止检测')
            self.log_message("开始全屏检测...")
            self.detection_thread.set_mode('fullscreen')
            self.detection_thread.start()
        else:
            self.stop_detection()

    def toggle_window_detection(self):
        if self.model is None:
            self.log_message("错误: 未加载模型，请先加载模型")
            return
            
        if not self.is_detecting or self.detect_mode != 'window':
            self.is_detecting = True
            self.detect_mode = 'window'
            self.btn_window.setText('停止检测')
            hwnd = self.window_combo.currentData()
            title = self.window_combo.currentText()
            if hwnd:
                self.log_message(f"开始窗口检测: {title}")
                self.detection_thread.set_window_title(title)
                self.detection_thread.set_mode('window', hwnd)
                self.detection_thread.start()
            else:
                self.log_message("请先选择一个窗口")
        else:
            self.stop_detection()

    def stop_detection(self):
        if not self.is_detecting:
            return
            
        self.is_detecting = False
        self.detect_mode = None
        self.selected_window = None
        if self.detection_thread:
            self.detection_thread.stop()
            self.detection_thread.wait()
        self.btn_fullscreen.setText('全屏检测')
        self.btn_window.setText('窗口检测')
        self.log_message("检测已停止")

    def detect_image(self):
        if self.model is None:
            self.log_message("错误: 未加载模型，请先加载模型")
            return
            
        if self.is_detecting:
            self.stop_detection()
            
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择图片",
            "",
            "图片文件 (*.jpg *.jpeg *.png *.bmp)"
        )
        
        if file_path:
            self.log_message(f"加载图片: {file_path}")
            frame = cv2.imread(file_path)
            if frame is not None:
                self.log_message("开始图片检测...")
                start_time = time.time()
                
                try:
                    results = self.model(frame)
                except Exception as e:
                    self.log_message(f"检测错误: {str(e)}")
                    return
                    
                detected_labels = []
                
                for result in results:
                    boxes = result.boxes
                    for box in boxes:
                        x1, y1, x2, y2 = box.xyxy[0]
                        conf = box.conf[0]
                        cls = box.cls[0]
                        
                        # 获取原始标签名称
                        original_label = result.names[int(cls)]
                        
                        # 使用自定义标签名称（如果存在），否则使用原始名称
                        display_label = self.custom_labels.get(original_label, original_label)
                        
                        cv2.rectangle(frame, 
                                    (int(x1), int(y1)), 
                                    (int(x2), int(y2)), 
                                    (0, 255, 0), 2)
                        
                        label = f'{display_label} {conf:.2f}'
                        detected_labels.append(display_label)
                        cv2.putText(frame, label, (int(x1), int(y1)-10), 
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                
                # 显示检测到的标签
                self.update_labels_display(detected_labels)
                self.display_frame(frame)
                
                elapsed = (time.time() - start_time) * 1000
                self.log_message(f"图片检测完成，耗时: {elapsed:.2f}ms")
                self.log_message(f"检测到 {len(detected_labels)} 个目标")
            else:
                self.log_message("无法加载图片，请检查文件格式")

    def display_frame(self, frame, detected_labels=None):
        if detected_labels is not None:
            self.update_labels_display(detected_labels)
            
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = frame.shape
        bytes_per_line = ch * w
        qt_image = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_image)
        
        # 获取显示标签的实际大小
        label_size = self.display_label.size()
        # 计算缩放比例
        scaled_pixmap = pixmap.scaled(
            label_size.width(),
            label_size.height(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        self.display_label.setPixmap(scaled_pixmap)
        # 确保标签大小策略正确
        self.display_label.setScaledContents(True)

    def update_labels_display(self, labels):
        """更新检测到的标签显示区域"""
        if not labels:
            self.labels_area.setText("未检测到目标")
            return
            
        # 统计每个标签出现的次数
        from collections import Counter
        label_counts = Counter(labels)
        
        # 创建HTML格式的文本
        html = "<div style='line-height: 1.5;'>"
        for label, count in label_counts.items():
            html += f"<div><b>{label}</b>: {count}次</div>"
        html += "</div>"
        
        self.labels_area.setText(html)

    def closeEvent(self, event):
        if self.is_detecting:
            self.stop_detection()
        self.log_message("程序已关闭")
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    detector = YoloDetector()
    detector.show()
    sys.exit(app.exec_())