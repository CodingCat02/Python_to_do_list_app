@echo off
echo ===============================
echo  Building Tkinter EXE
echo ===============================

REM Go to project root (this file's location)
cd /d "%~dp0"

REM Clean old builds
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist *.spec del *.spec

REM Build EXE
pyinstaller --onefile --noconsole --icon=icons/notepad.ico --add-data "icons;icons" python_files/main.py


echo.
echo ===============================
echo  BUILD FINISHED
echo ===============================
pause
