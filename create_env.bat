@echo off
%~d0
cd %~dp0
conda create -p .\env python=3.10 pytorch torchvision pytorch-cuda=11.8 cudatoolkit=11.8 cudnn=8 -c pytorch -c conda-forge -c nvidia -y
call conda activate .\env
pip install pyside6 transformers opencv-python opencv-contrib-python pillow
pause
