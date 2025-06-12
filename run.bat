@echo off
cd /d "%~dp0"
chcp 65001
setlocal EnableDelayedExpansion


echo "欢迎使用小白的 YOLO 启动脚本!"
echo     /\_/\
echo    ( o.o )
echo --------------------
:: Set environment variables
set CONDA_ENV_NAME=yolo_env
set PYTHON_VERSION=3.10

:: Check if Conda is installed
where conda >nul 2>nul
if !ERRORLEVEL! neq 0 (
    echo [ERROR] Conda not found. Please install Anaconda or Miniconda first
    echo Download: https://www.anaconda.com/download
    pause
    exit /b 1
)
echo [INFO] Conda detected [OK]

:: Check if conda environment exists
echo [INFO] Checking Conda environment: %CONDA_ENV_NAME%
call conda env list | find "%CONDA_ENV_NAME%" >nul
if !ERRORLEVEL! neq 0 (
    echo [INFO] Creating new Conda environment: %CONDA_ENV_NAME%
    call conda create -n %CONDA_ENV_NAME% python=%PYTHON_VERSION% -y
    if !ERRORLEVEL! neq 0 (
        echo [ERROR] Failed to create Conda environment
        pause
        exit /b 1
    )
)
echo [INFO] Conda environment ready [OK]

call conda init
echo [INFO] Conda init [OK]

:: Activate environment
echo [INFO] Activating environment...
call conda activate %CONDA_ENV_NAME%

if !ERRORLEVEL! neq 0 (
    echo [ERROR] Failed to activate Conda environment
    pause
    exit /b 1
)
echo [INFO] Environment activated [OK]

:: Check if PyTorch is installed
python -c "import torch" >nul 2>nul
if !ERRORLEVEL! neq 0 (
    echo [INFO] PyTorch not found. Installing...

    :: Use Python to detect CUDA version
    for /f "delims=" %%i in ('python detect_cuda.py') do (
        set "CUDA_VERSION=%%i"
    )
    echo [DEBUG] CUDA_VERSION = !CUDA_VERSION!

    :: Check if CUDA_VERSION is defined
    if not defined CUDA_VERSION (
        echo [WARN] CUDA_VERSION is not defined.
        echo.
        echo Press 1 to set CUDA_VERSION to "cpu", or press any other key to exit.
        set /p CHOICE="Enter your choice: "
        if "!CHOICE!"=="1" (
            set "CUDA_VERSION=cpu"
            echo [INFO] CUDA_VERSION set to "cpu"
        ) else (
            echo [INFO] Exiting...
            pause
            exit /b 1
        )
    )
    echo [INFO] Using Python from:
    :: Output final CUDA version
    echo [INFO] Final CUDA_VERSION = !CUDA_VERSION!

    if defined CUDA_VERSION (
        set "SHORT_CUDA=!CUDA_VERSION!"
        echo [DEBUG] SHORT_CUDA = !SHORT_CUDA!

        :: Extract major and minor versions (e.g., 12.6 → major 12, minor 6)
        for /f "tokens=1,2 delims=." %%a in ("!SHORT_CUDA!") do (
            set "CUDA_MAJOR=%%a"
            set "CUDA_MINOR=%%b"
        )

        :: Compatibility logic
        if "!CUDA_MAJOR!"=="12" (
            if "!CUDA_MINOR!" GEQ "6" (
                pip install torch==2.6.0 torchvision==0.21.0 torchaudio==2.6.0 --index-url https://download.pytorch.org/whl/cu126
            ) else if "!CUDA_MINOR!" GEQ "4" (
                pip install torch==2.6.0 torchvision==0.21.0 torchaudio==2.6.0 --index-url https://download.pytorch.org/whl/cu124
            ) else if "!CUDA_MINOR!" GEQ "1" (
                pip install torch==2.2.2 torchvision==0.17.2 torchaudio==2.2.2 --index-url https://download.pytorch.org/whl/cu121
            ) else (
                echo [WARN] CUDA 12 version too low, not supported: !SHORT_CUDA!
                pip install torch==2.6.0 torchvision==0.21.0 torchaudio==2.6.0 --index-url https://download.pytorch.org/whl/cpu
            )
        ) else if "!CUDA_MAJOR!"=="11" (
            if "!CUDA_MINOR!" GEQ "8" (
                pip install torch==2.1.2 torchvision==0.16.2 torchaudio==2.6.0 --index-url https://download.pytorch.org/whl/cu118
            ) else if "!CUDA_MINOR!" GEQ "7" (
                pip install torch==1.13.1 torchvision==0.14.1 torchaudio==2.6.0 --index-url https://download.pytorch.org/whl/cu117
            ) else if "!CUDA_MINOR!" GEQ "6" (
                pip install torch==1.12.1 torchvision==0.13.1 torchaudio==2.6.0 --index-url https://download.pytorch.org/whl/cu116
            ) else (
                echo [WARN] CUDA 11 version too low, not supported: !SHORT_CUDA!
                pip install torch==2.6.0 torchvision==0.21.0 torchaudio==2.6.0 --index-url https://download.pytorch.org/whl/cpu
            )
        ) else if "!CUDA_VERSION!"=="cpu" (
            echo [INFO] Installing CPU version of PyTorch
            pip install torch==2.6.0 torchvision==0.21.0 torchaudio==2.6.0 --index-url https://download.pytorch.org/whl/cpu
        ) else (
            echo [WARN] Unrecognized CUDA major version: !CUDA_MAJOR!
            pip install torch==2.6.0 torchvision==0.21.0 torchaudio==2.6.0 --index-url https://download.pytorch.org/whl/cpu
        )
    )
) else (
    echo [INFO] PyTorch is already installed
)

:: Install additional dependencies
echo [INFO] Checking other dependencies...
for %%P in (opencv-python ultralytics PyQt5 mss pywin32) do (
    python -c "import %%P" >nul 2>nul
    if !ERRORLEVEL! neq 0 (
        echo [INFO] Installing %%P...
        pip install %%P
    )
)
echo [INFO] Dependency installation completed [OK]

:: Run main script
echo [INFO] Launching application...
python main.py
if !ERRORLEVEL! neq 0 (
    echo [ERROR] Program failed with code: !ERRORLEVEL!
    echo Possible causes:
    echo 1. Python packages not installed properly
    echo 2. CUDA version incompatible
    echo 3. Insufficient GPU memory
    echo 4. Other system error
    echo Recommended actions:
    echo - Rerun this script
    echo - Check and install missing packages manually
    echo - Verify CUDA and NVIDIA drivers
    echo - Check logs for details
) else (
    echo [INFO] Program completed successfully [OK]
)

:end
echo [INFO] Script execution finished
cmd /k