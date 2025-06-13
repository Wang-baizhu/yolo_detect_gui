import subprocess
import sys
import re

def get_cuda_version():
    """获取CUDA版本"""
    try:
        output = subprocess.check_output(['nvcc', '--version']).decode()
        version_match = re.search(r'release (\d+\.\d+)', output)
        if version_match:
            return version_match.group(1)
    except:
        return None
    return None

def get_pytorch_install_command(cuda_version):
    """
    根据CUDA版本返回对应的PyTorch安装命令（依据 PyTorch 官网 2.7.0）
    """
    cuda = float(cuda_version)
    # 根据 CUDA Toolkit Archive 中的版本信息更新支持的 CUDA 版本
    commands = {
        12.8: "pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128",
        12.6: "pip install torch==2.6.0 torchvision==0.21.0 torchaudio==2.6.0 --index-url https://download.pytorch.org/whl/cu126",
        12.4: "pip install torch==2.6.0 torchvision==0.21.0 torchaudio==2.6.0 --index-url https://download.pytorch.org/whl/cu124",
        12.1: "pip install torch==2.5.1 torchvision==0.20.1 torchaudio==2.5.1 --index-url https://download.pytorch.org/whl/cu121",
        11.8: "pip install torch==2.6.0 torchvision==0.21.0 torchaudio==2.6.0 --index-url https://download.pytorch.org/whl/cu118",
        11.7: "pip install torch==2.0.1 torchvision==0.15.2 torchaudio==2.0.2 --index-url https://download.pytorch.org/whl/cu117",
        11.6: "pip install torch==1.13.1+cu116 torchvision==0.14.1+cu116 torchaudio==0.13.1 --extra-index-url https://download.pytorch.org/whl/cu116",
        11.3: "pip install torch==1.12.1+cu113 torchvision==0.13.1+cu113 torchaudio==0.12.1 --extra-index-url https://download.pytorch.org/whl/cu113",
        11.1: "pip install torch==1.9.0+cu111 torchvision==0.10.0+cu111 torchaudio==0.9.0 -f https://download.pytorch.org/whl/torch_stable.html",
        10.2: "pip install torch==1.12.1+cu102 torchvision==0.13.1+cu102 torchaudio==0.12.1 --extra-index-url https://download.pytorch.org/whl/cu102",
        10.1: "pip install torch==1.7.1+cu101 torchvision==0.8.2+cu101 torchaudio==0.7.2 -f https://download.pytorch.org/whl/torch_stable.html",
        9.2: "pip install torch==1.6.0+cu92 torchvision==0.7.0+cu92 -f https://download.pytorch.org/whl/torch_stable.html",
    }
    
    # 如果输入的 CUDA 版本不在列表中，选择最接近的版本
    versions = sorted(commands.keys())
    closest = min(versions, key=lambda x: abs(x - cuda))
    return commands.get(closest, "pip3 install torch torchvision torchaudio")


def uninstall_pytorch():
    """卸载所有PyTorch相关包"""
    packages = ['torch', 'torchvision', 'torchaudio']
    for package in packages:
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'uninstall', '-y', package])
        except:
            pass

def install_pytorch(cuda_version=None):
    """安装PyTorch"""
    if cuda_version:
        cmd = get_pytorch_install_command(cuda_version)
    else:
        cmd = "pip3 install torch torchvision torchaudio"
    
    try:
        subprocess.check_call(cmd.split())
        return True
    except:
        return False 