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
        12.9: "pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu129",
        12.8: "pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128",
        12.6: "pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu126",
        12.4: "pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124",
        12.1: "pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121",
        11.8: "pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118",
        11.7: "pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu117",
        11.6: "pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu116",
        11.3: "pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu113",
        11.1: "pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu111",
        10.2: "pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu102",
        10.1: "pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu101",
        9.2: "pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu92",
        9.0: "pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu90",
        8.0: "pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu80",
        7.5: "pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu75",
        7.0: "pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu70",
        6.5: "pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu65",
        6.0: "pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu60",
        5.5: "pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu55",
        5.0: "pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu50",
        4.0: "pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu40",
        3.0: "pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu30",
        2.0: "pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu20",
        1.0: "pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu10",
        0.0: "pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu",
    }
    
    # 如果输入的 CUDA 版本不在列表中，选择最接近的版本
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