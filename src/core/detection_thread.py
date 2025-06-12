import cv2
import numpy as np
import mss
import time
from PyQt5.QtCore import QThread, pyqtSignal
from ..utils.window_utils import get_window_rect

class DetectionThread(QThread):
    detection_complete = pyqtSignal(np.ndarray, list)
    log_message = pyqtSignal(str)
    fps_update = pyqtSignal(float)
    
    def __init__(self, model):
        super().__init__()
        self.model = model
        self.running = False
        self.detect_mode = None
        self.selected_window = None
        self.selected_monitor = 0
        self.custom_labels = {}
        self.confidence_threshold = 0.25
        
    def set_mode(self, mode, window_hwnd=None):
        self.detect_mode = mode
        self.selected_window = window_hwnd
        if mode == 'fullscreen':
            self.log_message.emit("开始全屏检测...")
        elif mode == 'window' and window_hwnd:
            self.log_message.emit(f"开始窗口检测: {self.selected_window_title}")
            
    def set_custom_labels(self, custom_labels):
        self.custom_labels = custom_labels
        
    def set_window_title(self, title):
        self.selected_window_title = title
        
    def set_confidence_threshold(self, threshold):
        self.confidence_threshold = threshold
        self.log_message.emit(f"置信度阈值已设置为: {threshold:.2f}")
        
    def stop(self):
        self.running = False
        
    def process_frame(self, frame):
        """处理单帧图像"""
        try:
            results = self.model(frame)
            detected_labels = []
            
            for result in results:
                boxes = result.boxes
                for box in boxes:
                    x1, y1, x2, y2 = box.xyxy[0]
                    conf = box.conf[0].item()
                    
                    if conf < self.confidence_threshold:
                        continue
                        
                    cls = box.cls[0]
                    original_label = result.names[int(cls)]
                    display_label = self.custom_labels.get(original_label, original_label)
                    
                    # 绘制边界框
                    cv2.rectangle(frame, 
                                (int(x1), int(y1)), 
                                (int(x2), int(y2)), 
                                (0, 255, 0), 2)
                    
                    # 绘制标签背景
                    label = f'{display_label} {conf:.2f}'
                    (label_w, label_h), _ = cv2.getTextSize(label, 
                                                          cv2.FONT_HERSHEY_SIMPLEX, 
                                                          0.5, 2)
                    cv2.rectangle(frame,
                                (int(x1), int(y1)-20),
                                (int(x1)+label_w, int(y1)),
                                (0, 255, 0), -1)
                    
                    # 绘制标签文本
                    cv2.putText(frame, label, 
                              (int(x1), int(y1)-5),
                              cv2.FONT_HERSHEY_SIMPLEX, 
                              0.5, (0, 0, 0), 2)
                    
                    detected_labels.append(display_label)
                    
            return frame, detected_labels
            
        except Exception as e:
            self.log_message.emit(f"检测错误: {str(e)}")
            return frame, []
        
    def run(self):
        self.running = True
        self.log_message.emit(f"检测线程已启动 (模式: {self.detect_mode})")
        self.log_message.emit(f"当前置信度阈值: {self.confidence_threshold:.2f}")
        
        frame_count = 0
        fps_start_time = time.time()
        fps_update_interval = 1.0  # 每秒更新一次FPS
        
        with mss.mss() as screen:
            while self.running:
                try:
                    # 获取截图
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
                        
                    # 转换图像格式
                    frame = np.array(screenshot)
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
                    
                    # 处理帧
                    frame, detected_labels = self.process_frame(frame)
                    
                    # 发送处理结果
                    self.detection_complete.emit(frame, detected_labels)
                    
                    # 计算和更新FPS
                    frame_count += 1
                    if time.time() - fps_start_time >= fps_update_interval:
                        fps = frame_count / (time.time() - fps_start_time)
                        self.fps_update.emit(fps)
                        frame_count = 0
                        fps_start_time = time.time()
                    
                    # 限制检测频率
                    self.msleep(20)  # 约50FPS
                    
                except Exception as e:
                    self.log_message.emit(f"运行时错误: {str(e)}")
                    continue 