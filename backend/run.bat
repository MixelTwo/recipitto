@echo off
setlocal

REM Change to the directory where this bat file is located
cd /d "%~dp0"

REM Create virtual environment if it doesn't exist
if not exist ".venv\" (
    echo Creating virtual environment...
    python -m venv .venv
)

REM Activate virtual environment
call .venv\Scripts\activate

REM Install requirements if file exists
if exist "requirements.txt" (
    echo Installing dependencies...
    pip install -r requirements.txt
)

REM Create .env if it doesn't exist
if not exist ".env" (
    if exist ".env.example" (
        echo Creating .env from .env.example...
        copy ".env.example" ".env"
    )
)

REM Run python project
echo Starting application...
python main.py dev

endlocal
pause