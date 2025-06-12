# YOLO目标检测GUI

一个基于YOLOv8和PyQt5的目标检测图形界面程序，支持实时检测、图片检测和自定义标签。

## 功能特点

- 支持CUDA加速（自动检测并使用可用的GPU）
- 实时全屏检测
- 窗口选择检测
- 图片文件检测
- 自定义标签名称
- 可调节置信度阈值
- 实时FPS显示
- 深色主题UI
- 检测结果实时统计

## 系统要求

- Windows 10/11
- Python 3.8+
- CUDA支持（可选，用于GPU加速）

## 安装步骤

1. 克隆仓库：
```bash
git clone [repository_url]
cd yolo_detect_gui
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 安装对应CUDA版本的PyTorch：

首先检查CUDA版本：
```bash
nvcc --version
```

然后根据CUDA版本安装对应的PyTorch：

- CUDA 11.8:
```bash
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

- CUDA 11.7:
```bash
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu117
```

- CUDA 11.6:
```bash
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu116
```

- 仅CPU:
```bash
pip3 install torch torchvision torchaudio
```

## 使用说明

1. 运行程序：
```bash
python src/main.py
```

2. 加载模型：
   - 点击"加载模型"按钮
   - 选择YOLOv8模型文件（.pt格式）

3. 开始检测：
   - 全屏检测：点击"全屏检测"按钮
   - 窗口检测：从下拉列表选择窗口，点击"窗口检测"按钮
   - 图片检测：点击"图片检测"按钮，选择图片文件

4. 自定义标签：
   - 点击"编辑标签名称"按钮
   - 在弹出的对话框中修改显示名称
   - 点击确定保存更改

5. 调整置信度：
   - 点击"设置置信度"按钮
   - 输入0.0-1.0之间的值
   - 点击确定应用更改

## 注意事项

- 首次运行时会自动下载YOLOv8模型
- GPU加速需要正确安装CUDA和对应版本的PyTorch
- 窗口检测模式下，目标窗口不能最小化
- 自定义标签会自动保存到custom_labels.json文件中

## 许可证

MIT License