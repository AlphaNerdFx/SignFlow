@echo off
TITLE SignFlow Enterprise Launcher
CLS

ECHO ======================================================
ECHO      SIGNFLOW ENTERPRISE - AUTO LAUNCHER
ECHO ======================================================
ECHO.

:: 1. Check if the VENV folder already exists
IF EXIST "env" (
    ECHO [INFO] Virtual Environment found. Launching...
    GOTO LAUNCH
)

:: 2. If not, check for Python 3.10
ECHO [SETUP] First time run detected. Setting up environment...
py -3.10 --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    ECHO.
    ECHO [ERROR] Python 3.10 is missing!
    ECHO.
    ECHO SignFlow requires Python 3.10 to support MediaPipe.
    ECHO Please download it here: https://www.python.org/downloads/release/python-31011/
    ECHO.
    PAUSE
    EXIT
)

:: 3. Create Virtual Environment
ECHO [SETUP] Creating isolated Python environment (env)...
py -3.10 -m venv env

:: 4. Install Dependencies
ECHO [SETUP] Installing libraries (TensorFlow, MediaPipe, etc)...
.\env\Scripts\python -m pip install --upgrade pip
.\env\Scripts\python -m pip install -r requirements.txt

ECHO [SETUP] Setup Complete!

:LAUNCH
ECHO.
ECHO [START] Starting Application...
.\env\Scripts\python main_gui.py

PAUSE