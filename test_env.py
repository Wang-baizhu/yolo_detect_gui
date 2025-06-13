import torch
print("CUDA available:", torch.cuda.is_available())
if torch.cuda.is_available():
    print("torch version:", torch.__version__)
    print("torch support CUDA version:", torch.version.cuda)
    print("Number of GPUs:", torch.cuda.device_count())
    print("Current CUDA device:", torch.cuda.current_device())
    print("CUDA device name:", torch.cuda.get_device_name(torch.cuda.current_device()))