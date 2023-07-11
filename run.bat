@echo off
%~d0
cd %~dp0
set PYTHONPATH=%PYTHONPATH%;%~dp0
python main.py
pause