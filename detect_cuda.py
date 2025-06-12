# detect_cuda.py
import subprocess
import re
import sys

try:
    output = subprocess.check_output(["nvcc", "--version"], stderr=subprocess.STDOUT, text=True)
    match = re.search(r"release (\d+\.\d+)", output)
    if match:
        print(match.group(1))  # 输出格式如：12.4
    else:
        sys.exit(1)  # 没找到
except Exception:
    sys.exit(1)  # nvcc 未安装或出错
