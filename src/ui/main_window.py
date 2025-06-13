import sys
import cv2
import numpy as np
import json
import os
import time
import torch
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                           QPushButton, QLabel, QFileDialog, QComboBox,
                           QTextEdit, QSplitter, QInputDialog, QMessageBox,
                           QApplication, QFrame)
from PyQt5.QtCore import Qt, QTimer, QPoint
from PyQt5.QtGui import QImage, QPixmap, QIcon, QFont
from ultralytics import YOLO

from .styles import (get_dark_palette, get_button_style, get_combobox_style,
                    get_text_edit_style, get_label_style, get_window_style)
from .label_editor import LabelEditorDialog
from .progress_dialog import ProgressDialog
from .install_thread import PyTorchInstallThread
from ..core.detection_thread import DetectionThread
from ..utils.window_utils import get_window_list
from ..utils.cuda_utils import (get_cuda_version, uninstall_pytorch,
                              install_pytorch)

class YoloDetector(QMainWindow):
    def __init__(self, is_cuda_available):
        super().__init__()
        self.model = None
        self.custom_labels = {}
        self.detection_thread = None
        self.install_thread = None
        self.confidence_threshold = 0.25
        self.is_cuda_available = is_cuda_available
        self.is_detecting = False
        self.detect_mode = None
        self.selected_window = None
        
        # 窗口无边框设置
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # 用于窗口拖动和状态
        self._drag_pos = None
        self._is_maximized = False
        self._normal_geometry = None
        
        self.init_ui()
        self.check_pytorch_installation()
        self.load_model('yolov8s.pt')  # 加载默认模型
        
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle('YOLO目标检测')
        self.setGeometry(100, 100, 1200, 800)
        
        # 设置深色主题
        self.setPalette(get_dark_palette())
        self.setStyleSheet(get_window_style())
        
        # 创建主窗口部件
        main_widget = QWidget()
        main_widget.setObjectName("mainWidget")
        main_widget.setStyleSheet("""
            QWidget#mainWidget {
                background-color: #2b2b2b;
                border: 1px solid #3a3a3a;
                border-radius: 8px;
            }
        """)
        self.setCentralWidget(main_widget)
        
        # 主布局
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 创建标题栏
        title_bar = QWidget()
        title_bar.setFixedHeight(35)
        title_bar.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
            }
        """)
        
        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(10, 0, 10, 0)
        
        # 图标
        icon_label = QLabel()
        icon_label.setFixedSize(20, 20)
        icon_label.setPixmap(QPixmap("icon.png").scaled(20, 20, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        title_layout.addWidget(icon_label)
        
        # 标题
        title_label = QLabel("YOLO目标检测")
        title_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 14px;
                font-weight: bold;
            }
        """)
        title_layout.addWidget(title_label)
        
        title_layout.addStretch()
        
        # 最小化按钮
        min_btn = QPushButton("－")
        min_btn.setFixedSize(40, 25)
        min_btn.clicked.connect(self.showMinimized)
        min_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: white;
                border: none;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #404040;
            }
        """)
        
        # 最大化按钮
        max_btn = QPushButton("□")
        max_btn.setFixedSize(40, 25)
        max_btn.clicked.connect(self.toggle_maximize)
        max_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: white;
                border: none;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #404040;
            }
        """)
        
        # 关闭按钮
        close_btn = QPushButton("×")
        close_btn.setFixedSize(40, 25)
        close_btn.clicked.connect(self.close)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: white;
                border: none;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #e81123;
            }
        """)
        
        title_layout.addWidget(min_btn)
        title_layout.addWidget(max_btn)
        title_layout.addWidget(close_btn)
        
        # 添加标题栏到主布局
        main_layout.addWidget(title_bar)
        
        # 内容区域
        content_widget = QWidget()
        content_layout = QHBoxLayout(content_widget)
        main_layout.addWidget(content_widget)
        
        # 左侧区域 - 检测显示
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        # 检测显示区域
        self.display_label = QLabel()
        self.display_label.setAlignment(Qt.AlignCenter)
        self.display_label.setMinimumSize(640, 480)
        self.display_label.setStyleSheet("""
            QLabel {
                background-color: #1a1a1a;
                border: 2px solid #333;
                border-radius: 4px;
            }
        """)
        left_layout.addWidget(self.display_label, 3)
        
        # FPS显示
        self.fps_label = QLabel("FPS: --")
        self.fps_label.setStyleSheet(get_label_style())
        self.fps_label.setAlignment(Qt.AlignRight)
        left_layout.addWidget(self.fps_label)
        
        # 底部按钮区域
        button_layout = QHBoxLayout()
        
        # 创建按钮
        self.create_buttons()
        # 日志区域
        log_group = QWidget()
        log_layout = QVBoxLayout(log_group)
        
        log_title = QLabel("运行日志")
        log_title.setAlignment(Qt.AlignCenter)
        log_title.setStyleSheet("""
            QLabel {
                color: white;
                font-weight: bold;
                font-size: 14px;
                padding: 5px;
            }
        """)
        log_layout.addWidget(log_title)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet(get_text_edit_style())
        log_layout.addWidget(self.log_text)
        
        # 窗口选择区域
        window_layout = QHBoxLayout()
        self.window_combo = QComboBox(self)
        self.window_combo.setStyleSheet(get_combobox_style())
        self.update_window_list()
        self.window_combo.setEnabled(False)
        
        self.btn_refresh_windows = QPushButton('刷新', self)
        self.btn_refresh_windows.setToolTip("刷新窗口列表")
        self.btn_refresh_windows.setMaximumWidth(60)
        self.btn_refresh_windows.clicked.connect(self.update_window_list)
        self.btn_refresh_windows.setEnabled(False)
        self.btn_refresh_windows.setStyleSheet(get_button_style())
        
        window_layout.addWidget(self.window_combo)
        window_layout.addWidget(self.btn_refresh_windows)
        
        # 添加所有按钮到布局
        self.add_buttons_to_layout(button_layout, window_layout)
        left_layout.addLayout(button_layout)
        
        # 右侧区域 - 信息面板
        right_widget = QWidget()
        right_widget.setMinimumWidth(300)
        right_layout = QVBoxLayout(right_widget)
        
        # 检测结果区域
        results_group = QWidget()
        results_layout = QVBoxLayout(results_group)
        
        results_title = QLabel("检测结果")
        results_title.setAlignment(Qt.AlignCenter)
        results_title.setStyleSheet("""
            QLabel {
                color: white;
                font-weight: bold;
                font-size: 14px;
                padding: 1px;
            }
        """)
        results_layout.addWidget(results_title)
        
        self.labels_area = QLabel()
        self.labels_area.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.labels_area.setWordWrap(True)
        self.labels_area.setStyleSheet("""
            QLabel {
                color: white;
                background-color: #2c2c2c;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 10px;
                min-height: 150px;
            }
        """)
        results_layout.addWidget(self.labels_area)
        
        
        # 添加清空日志按钮
        btn_clear_log = QPushButton("清空日志")
        btn_clear_log.clicked.connect(self.clear_log)
        btn_clear_log.setStyleSheet(get_button_style())
        log_layout.addWidget(btn_clear_log)
        
        # 添加分割线
        splitter = QSplitter(Qt.Vertical)
        splitter.addWidget(results_group)
        splitter.addWidget(log_group)
        right_layout.addWidget(splitter)
        
        # 设置左右区域比例
        content_layout.addWidget(left_widget, 7)
        content_layout.addWidget(right_widget, 3)
        
        # 初始日志信息
        self.log_message("程序已启动")
        self.log_message(f"设备类型: {'GPU' if self.is_cuda_available else 'CPU'}")
        self.log_message(f"默认置信度阈值: {self.confidence_threshold:.2f}")
        
    def create_buttons(self):
        """创建所有按钮"""
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
        
        self.btn_set_confidence = QPushButton('设置置信度', self)
        self.btn_set_confidence.clicked.connect(self.set_confidence_threshold)
        self.btn_set_confidence.setEnabled(False)
        
        # 设置按钮样式
        for btn in [self.btn_fullscreen, self.btn_window, self.btn_image,
                   self.btn_edit_labels, self.btn_load_model, 
                   self.btn_set_confidence]:
            btn.setStyleSheet(get_button_style())
            
    def add_buttons_to_layout(self, button_layout, window_layout):
        """将按钮添加到布局中"""
        button_layout.addWidget(self.btn_load_model)
        button_layout.addWidget(self.btn_fullscreen)
        button_layout.addWidget(self.btn_window)
        button_layout.addLayout(window_layout)
        button_layout.addWidget(self.btn_image)
        button_layout.addWidget(self.btn_edit_labels)
        button_layout.addWidget(self.btn_set_confidence)
        
    def load_model(self, model_path):
        """加载模型"""
        try:
            self.log_message(f"正在加载模型: {model_path}")
            self.model = YOLO(model_path)
            
            # 初始化检测线程
            if self.detection_thread:
                self.detection_thread.stop()
                self.detection_thread.wait()
                
            self.detection_thread = DetectionThread(self.model)
            self.detection_thread.detection_complete.connect(self.display_frame)
            self.detection_thread.log_message.connect(self.log_message)
            self.detection_thread.fps_update.connect(self.update_fps)
            self.detection_thread.confidence_threshold = self.confidence_threshold
            
            # 加载自定义标签
            self.custom_labels = self.load_custom_labels()
            self.detection_thread.set_custom_labels(self.custom_labels)
            
            # 启用按钮
            self.enable_buttons(True)
            
            self.log_message(f"模型加载成功")
            self.log_message(f"检测类别数: {len(self.model.names)}")
            self.log_message(f"模型路径: {model_path}")
            
            return True
        except Exception as e:
            self.log_message(f"模型加载失败: {str(e)}")
            self.model = None
            self.enable_buttons(False)
            return False
            
    def enable_buttons(self, enabled):
        """启用或禁用按钮"""
        self.btn_fullscreen.setEnabled(enabled)
        self.btn_window.setEnabled(enabled)
        self.btn_image.setEnabled(enabled)
        self.btn_edit_labels.setEnabled(enabled)
        self.window_combo.setEnabled(enabled)
        self.btn_refresh_windows.setEnabled(enabled)
        self.btn_set_confidence.setEnabled(enabled)
        
    def update_fps(self, fps):
        """更新FPS显示"""
        self.fps_label.setText(f"FPS: {fps:.1f}")
        
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
            
        original_labels = list(self.model.names.values())
        dialog = LabelEditorDialog(original_labels, self.custom_labels, self)
        
        if dialog.exec_() == dialog.Accepted:
            self.custom_labels = dialog.get_custom_names()
            self.detection_thread.set_custom_labels(self.custom_labels)
            self.save_custom_labels()
            self.log_message("标签名称已更新")
            
    def update_window_list(self):
        """更新窗口列表"""
        self.log_message("正在刷新窗口列表...")
        self.window_combo.clear()
        windows = get_window_list()
        for hwnd, title in windows:
            self.window_combo.addItem(title, hwnd)
        self.log_message(f"找到 {len(windows)} 个窗口")
        
    def set_confidence_threshold(self):
        """设置置信度阈值"""
        if self.model is None:
            self.log_message("错误: 未加载模型，请先加载模型")
            return
            
        new_threshold, ok = QInputDialog.getDouble(
            self, 
            "设置置信度阈值", 
            "请输入置信度阈值 (0.0 - 1.0):", 
            value=self.confidence_threshold, 
            min=0.0, 
            max=1.0, 
            decimals=2
        )
        
        if ok:
            self.confidence_threshold = new_threshold
            if self.detection_thread:
                self.detection_thread.set_confidence_threshold(new_threshold)
            self.log_message(f"置信度阈值已设置为: {new_threshold:.2f}")
            
    def toggle_fullscreen_detection(self):
        """切换全屏检测状态"""
        if self.model is None:
            self.log_message("错误: 未加载模型，请先加载模型")
            return
            
        if not self.is_detecting or self.detect_mode != 'fullscreen':
            self.start_detection('fullscreen')
        else:
            self.stop_detection()
            
    def toggle_window_detection(self):
        """切换窗口检测状态"""
        if self.model is None:
            self.log_message("错误: 未加载模型，请先加载模型")
            return
            
        if not self.is_detecting or self.detect_mode != 'window':
            hwnd = self.window_combo.currentData()
            title = self.window_combo.currentText()
            if hwnd:
                self.start_detection('window', hwnd, title)
            else:
                self.log_message("请先选择一个窗口")
        else:
            self.stop_detection()
            
    def start_detection(self, mode, hwnd=None, title=None):
        """开始检测"""
        self.is_detecting = True
        self.detect_mode = mode
        
        if mode == 'fullscreen':
            self.btn_fullscreen.setText('停止检测')
            self.log_message("开始全屏检测...")
            self.detection_thread.set_mode('fullscreen')
        elif mode == 'window':
            self.btn_window.setText('停止检测')
            self.log_message(f"开始窗口检测: {title}")
            self.detection_thread.set_window_title(title)
            self.detection_thread.set_mode('window', hwnd)
            
        self.detection_thread.start()
        
    def stop_detection(self):
        """停止检测"""
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
        self.fps_label.setText("FPS: --")
        self.log_message("检测已停止")
        
    def detect_image(self):
        """检测图片"""
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
                    frame, detected_labels = self.detection_thread.process_frame(frame)
                    self.update_labels_display(detected_labels)
                    self.display_frame(frame)
                    
                    elapsed = (time.time() - start_time) * 1000
                    self.log_message(f"图片检测完成，耗时: {elapsed:.2f}ms")
                    self.log_message(f"检测到 {len(detected_labels)} 个目标")
                except Exception as e:
                    self.log_message(f"检测错误: {str(e)}")
            else:
                self.log_message("无法加载图片，请检查文件格式")
                
    def display_frame(self, frame, detected_labels=None):
        """显示检测结果帧"""
        if detected_labels is not None:
            self.update_labels_display(detected_labels)
            
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = frame.shape
        bytes_per_line = ch * w
        qt_image = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_image)
        
        # 获取显示标签的实际大小并保持纵横比
        label_size = self.display_label.size()
        scaled_pixmap = pixmap.scaled(
            label_size.width(),
            label_size.height(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        
        self.display_label.setPixmap(scaled_pixmap)
        
    def update_labels_display(self, labels):
        """更新检测到的标签显示"""
        if not labels:
            self.labels_area.setText("未检测到目标")
            return
            
        from collections import Counter
        label_counts = Counter(labels)
        
        html = "<div style='line-height: 1.5;'>"
        for label, count in label_counts.items():
            html += f"<div><b>{label}</b>: {count}次</div>"
        html += "</div>"
        
        self.labels_area.setText(html)
        
    def closeEvent(self, event):
        """关闭窗口事件"""
        if self.is_detecting:
            self.stop_detection()
        
        # 停止安装线程
        if self.install_thread and self.install_thread.isRunning():
            self.install_thread.stop()
            self.install_thread.wait()
            
        self.log_message("程序已关闭")
        event.accept()


    def check_pytorch_installation(self):
        """检查 PyTorch 安装状态并提供安装选项"""
        try:
            # 获取系统 CUDA 版本
            system_cuda_str = get_cuda_version()
            if system_cuda_str:
                try:
                    system_cuda = float(system_cuda_str)
                    if not self.check_pytorch_cuda_compatibility(system_cuda_str):
                        reply = QMessageBox.question(
                            self,
                            "PyTorch CUDA版本不匹配",
                            f"检测到系统CUDA版本({system_cuda_str})与PyTorch使用的CUDA版本({torch.version.cuda})不匹配。\n"
                            "是否要重新安装匹配的PyTorch版本？",
                            QMessageBox.Yes | QMessageBox.No,
                            QMessageBox.Yes
                        )
                        
                        if reply == QMessageBox.Yes:
                            self.reinstall_pytorch(system_cuda_str)
                except ValueError:
                    self.log_message(f"无法解析CUDA版本: {system_cuda_str}")
                    
        except ImportError:
            self.reinstall_pytorch()

    def check_pytorch_cuda_compatibility(self, system_cuda_str):
        """
        检查 PyTorch 和 CUDA 版本是否匹配（简化版本）
        """
        # 检查是否有可用的 CUDA 设备
        if torch.cuda.is_available():
            self.log_message("CUDA 设备可用，将使用 GPU 进行计算")
            return True
        else:
            self.log_message("CUDA 设备不可用，将使用 CPU 进行计算")
            return False
                
    def reinstall_pytorch(self, detected_cuda_version=None):
        """重新安装PyTorch"""
        try:
            # 如果已有安装线程在运行，先停止它
            if self.install_thread and self.install_thread.isRunning():
                self.install_thread.stop()
                self.install_thread.wait()

            # 获取CUDA版本
            cuda_version_str = detected_cuda_version or get_cuda_version()
            cuda_version = None
            
            if cuda_version_str:
                try:
                    cuda_version = float(cuda_version_str)
                    reply = QMessageBox.question(
                        self,
                        "检测到CUDA",
                        f"检测到CUDA版本 {cuda_version_str}\n是否安装CUDA版本的PyTorch？",
                        QMessageBox.Yes | QMessageBox.No,
                        QMessageBox.Yes
                    )
                    
                    use_cuda = reply == QMessageBox.Yes
                    if use_cuda:
                        cuda_version = cuda_version_str
                except ValueError:
                    self.log_message(f"无法解析CUDA版本: {cuda_version_str}")
                    use_cuda = False
            else:
                use_cuda = False
                
            # 创建并显示进度对话框
            progress = ProgressDialog(self)
            progress.setWindowModality(Qt.ApplicationModal)  # 设置为模态对话框
            progress.show()
            
            def update_progress():
                """更新进度动画"""
                if not progress.isVisible():
                    timer.stop()
                    return
                current = progress.progress_bar.value()
                if current >= 99:
                    progress.progress_bar.setValue(0)
                else:
                    progress.progress_bar.setValue(current + 1)
            
            # 创建定时器来更新进度
            timer = QTimer(self)
            timer.timeout.connect(update_progress)
            timer.start(50)  # 每50ms更新一次
            
            # 创建安装线程
            self.install_thread = PyTorchInstallThread(cuda_version if use_cuda else None)
            
            def on_progress(message):
                """处理进度信息"""
                if progress.isVisible():
                    progress.set_status(message)
                    self.log_message(message)
                
            def on_finished(success):
                """处理安装完成"""
                timer.stop()
                if progress.isVisible():
                    progress.close()
                
                if success:
                    QMessageBox.information(
                        self,
                        "安装完成",
                        "PyTorch安装成功！请重启程序以应用更改。",
                        QMessageBox.Ok
                    )
                    sys.exit(0)
                else:
                    QMessageBox.critical(
                        self,
                        "安装失败",
                        "PyTorch安装失败，请检查网络连接或手动安装。",
                        QMessageBox.Ok
                    )
            
            # 连接信号
            self.install_thread.progress.connect(on_progress)
            self.install_thread.finished.connect(on_finished)
            
            # 启动安装线程
            self.install_thread.start()
                
        except Exception as e:
            QMessageBox.critical(
                self,
                "错误",
                f"安装过程中出现错误：{str(e)}",
                QMessageBox.Ok
            )

    def mousePressEvent(self, event):
        """处理鼠标按下事件"""
        if event.button() == Qt.LeftButton:
            if not self._is_maximized:  # 只在非最大化状态下允许拖动
                self._drag_pos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        """处理鼠标移动事件"""
        if event.buttons() == Qt.LeftButton and self._drag_pos is not None:
            # 如果是全屏状态，先退出全屏并停止检测
            if self.isFullScreen():
                self.showNormal()
                if self.is_detecting and self.detect_mode == 'fullscreen':
                    self.stop_detection()
                # 更新拖动位置，避免窗口跳动
                self._drag_pos = event.globalPos() - self.frameGeometry().topLeft()
            elif self._is_maximized:
                # 如果是最大化状态，先恢复正常大小
                self.toggle_maximize()
                # 计算新的拖动起点，使窗口跟随鼠标
                cursor_x = event.globalPos().x()
                window_width = self._normal_geometry.width()
                new_x = cursor_x - window_width / 2
                new_y = event.globalPos().y() - 10  # 10是标题栏高度的估计值
                self.move(int(new_x), int(new_y))
                self._drag_pos = event.globalPos() - self.pos()
            else:
                # 正常状态下的拖动
                self.move(event.globalPos() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        """处理鼠标释放事件"""
        if event.button() == Qt.LeftButton:
            # 检查是否拖动到了屏幕顶部
            if not self._is_maximized and event.globalPos().y() <= 5:
                self.toggle_maximize()
            self._drag_pos = None
            event.accept()

    def mouseDoubleClickEvent(self, event):
        """处理鼠标双击事件"""
        if event.button() == Qt.LeftButton:
            # 获取标题栏区域
            title_bar_height = 35  # 标题栏高度
            if event.pos().y() <= title_bar_height:
                self.toggle_maximize()
                event.accept()

    def toggle_maximize(self):
        """切换最大化/还原窗口状态"""
        if self._is_maximized:
            self.showNormal()
            if self._normal_geometry:
                self.setGeometry(self._normal_geometry)
            self._is_maximized = False
        else:
            self._normal_geometry = self.geometry()
            self.showMaximized()
            # 获取屏幕尺寸并设置窗口大小
            screen = QApplication.primaryScreen()
            if screen:
                rect = screen.availableGeometry()
                self.setGeometry(rect)
            self._is_maximized = True