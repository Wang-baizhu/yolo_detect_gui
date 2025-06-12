import sys
import torch
from PyQt5.QtWidgets import QApplication
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from src.ui.main_window import YoloDetector

def check_cuda():
    """检查CUDA是否可用并打印相关信息"""
    if torch.cuda.is_available():
        cuda_version = torch.version.cuda
        device_name = torch.cuda.get_device_name(0)
        print(f"CUDA 可用 - 版本: {cuda_version}")
        print(f"GPU 设备: {device_name}")
        return True
    else:
        print("CUDA 不可用 - 使用 CPU 模式")
        return False

def main():
    """主程序入口"""
    # 检查CUDA状态
    is_cuda_available = check_cuda()
    
    # 创建应用
    app = QApplication(sys.argv)
    
    # 设置应用样式
    app.setStyle('Fusion')
    
    # 创建主窗口
    detector = YoloDetector(is_cuda_available)
    detector.show()
    
    # 运行应用
    sys.exit(app.exec_())

if __name__ == '__main__':
    main() 