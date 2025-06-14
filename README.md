# YOLO目标检测GUI

一个基于YOLOv8和PyQt5的目标检测图形界面程序，支持实时检测、图片检测和自定义标签。

## 功能特点

- 支持CUDA加速（自动检测并使用可用的GPU），如不可使用则会自动切换为CPU模式
- 实时全屏检测
- 窗口选择检测
- 图片文件检测
- 自定义标签名称
- 可调节置信度阈值
- 实时FPS显示
- 深色主题UI
- 检测结果实时统计
![示例](image.png)

## 要求

- Windows 10/11
- CUDA支持（可选，用于GPU加速）(https://developer.nvidia.com/cuda-toolkit-archive)
- 已安装anaconda(https://www.anaconda.com/download)
- 已安装pip(配置好镜像源)
   - 可参考https://blog.csdn.net/qq_42257666/article/details/117884849

## 安装步骤

1. 克隆或下载仓库：
```bash
git clone https://github.com/Wang-baizhu/yolo_detect_gui.git
```

2. 一键运行脚本
点击run.bat即可一键安装依赖并运行程序

### 安装对应CUDA版本的PyTorch说明（额外说明，自动脚本会自动运行）

首先检查CUDA版本：
```bash
nvcc --version
```
然后根据CUDA版本安装对应的PyTorch：
https://pytorch.org/get-started/previous-versions/
以下是根据文件内容整理的 CUDA 版本与对应最新 PyTorch 版本的 pip 安装命令的 Markdown 格式说明：

## CUDA 版本与 PyTorch 安装命令对应表

#### CUDA 12.6
```bash
pip install torch==2.6.0 torchvision==0.21.0 torchaudio==2.6.0 --index-url https://download.pytorch.org/whl/cu126
```

#### CUDA 12.4
```bash
pip install torch==2.6.0 torchvision==0.21.0 torchaudio==2.6.0 --index-url https://download.pytorch.org/whl/cu124
```

#### CUDA 12.1
```bash
pip install torch==2.5.1 torchvision==0.20.1 torchaudio==2.5.1 --index-url https://download.pytorch.org/whl/cu121
```

#### CUDA 11.8
```bash
pip install torch==2.6.0 torchvision==0.21.0 torchaudio==2.6.0 --index-url https://download.pytorch.org/whl/cu118
```

#### CUDA 11.7
```bash
pip install torch==2.0.1 torchvision==0.15.2 torchaudio==2.0.2 --index-url https://download.pytorch.org/whl/cu117
```

#### CUDA 11.6
```bash
pip install torch==1.13.1+cu116 torchvision==0.14.1+cu116 torchaudio==0.13.1 --extra-index-url https://download.pytorch.org/whl/cu116
```

#### CUDA 11.3
```bash
pip install torch==1.12.1+cu113 torchvision==0.13.1+cu113 torchaudio==0.12.1 --extra-index-url https://download.pytorch.org/whl/cu113
```

#### CUDA 11.1
```bash
pip install torch==1.9.0+cu111 torchvision==0.10.0+cu111 torchaudio==0.9.0 -f https://download.pytorch.org/whl/torch_stable.html
```

#### CUDA 10.2
```bash
pip install torch==1.12.1+cu102 torchvision==0.13.1+cu102 torchaudio==0.12.1 --extra-index-url https://download.pytorch.org/whl/cu102
```

#### CUDA 10.1
```bash
pip install torch==1.7.1+cu101 torchvision==0.8.2+cu101 torchaudio==0.7.2 -f https://download.pytorch.org/whl/torch_stable.html
```

#### CUDA 9.2
```bash
pip install torch==1.6.0+cu92 torchvision==0.7.0+cu92 -f https://download.pytorch.org/whl/torch_stable.html
```

## 功能说明

1. 自动检测安装对应版本pytorch

2. 加载模型：
   - 点击"加载模型"按钮
   - 选择YOLOv8/11模型文件（.pt格式）

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
- 自定义标签会自动保存到custom_labels.json文件中

## 许可证

MIT License