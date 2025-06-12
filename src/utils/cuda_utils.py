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
    commands = {
        12.8: "pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128",
        12.6: "pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu126",
        12.4: "pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124",
        12.1: "pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121",
        11.8: "pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118",
    }
    versions = sorted(commands.keys())
    closest = min(versions, key=lambda x: abs(x - cuda))
    return commands.get(closest, "pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu")


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