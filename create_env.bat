@echo off
%~d0
cd %~dp0
conda create -p .\venv python=3.11 ipython ipykernel ipywidgets pytorch torchvision pytorch-cuda=12.1 cuda=12.1 cudnn=8 timm -c pytorch -c conda-forge -c nvidia -y

call conda activate .\venv

pip install pyside6 transformers opencv-python opencv-contrib-python pillow pyinstaller
pause
