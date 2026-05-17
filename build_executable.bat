@echo off
setlocal
cd /d "%~dp0"

echo Installing build dependencies...
python -m pip install --upgrade pip -q
if errorlevel 1 goto :fail
python -m pip install pygame numpy pyinstaller -q
if errorlevel 1 goto :fail

echo Verifying main.py...
python -m py_compile main.py
if errorlevel 1 goto :fail

echo Building single-file executable (may take several minutes)...
python -m PyInstaller Heliosylva.spec --noconfirm --clean
if errorlevel 1 goto :fail

if not exist "dist\Heliosylva.exe" (
    echo Build finished but dist\Heliosylva.exe was not found.
    exit /b 1
)

echo.
echo Success!
echo   Ship this file:  %CD%\dist\Heliosylva.exe
echo.
echo Players: download Heliosylva.exe, then double-click to play.
exit /b 0

:fail
echo Build failed.
exit /b 1
