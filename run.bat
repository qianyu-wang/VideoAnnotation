@echo off
%~d0
cd %~dp0
set PYTHONPATH=%PYTHONPATH%;%~dp0
call conda activate
python main.py
pause