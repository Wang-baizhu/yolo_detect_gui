from PyQt5.QtCore import QThread, pyqtSignal
from ..utils.cuda_utils import uninstall_pytorch, install_pytorch

class PyTorchInstallThread(QThread):
    progress = pyqtSignal(str)  # 发送进度信息
    finished = pyqtSignal(bool)  # 发送安装结果

    def __init__(self, cuda_version=None):
        super().__init__()
        self.cuda_version = cuda_version
        self._is_running = True

    def run(self):
        try:
            if not self._is_running:
                return

            # 卸载旧版本
            self.progress.emit("正在卸载旧版本PyTorch...")
            uninstall_pytorch()

            if not self._is_running:
                return

            # 安装新版本
            self.progress.emit("正在安装新版本PyTorch...")
            success = install_pytorch(self.cuda_version)

            if not self._is_running:
                return

            # 发送结果
            self.finished.emit(success)

        except Exception as e:
            if self._is_running:
                self.progress.emit(f"安装出错: {str(e)}")
                self.finished.emit(False)

    def stop(self):
        """停止线程"""
        self._is_running = False
        self.wait() 