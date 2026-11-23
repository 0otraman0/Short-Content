@echo off
setlocal enabledelayedexpansion
title YouTube Shorts Generator

echo ======================================================
echo    YOUTUBE SHORTS GENERATOR (MINECRAFT & FACTS)
echo ======================================================
echo.

:: 1. Kiem tra Python
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [LOI] Python chua duoc cai dat hoac chua co trong PATH.
    echo Vui long cai dat Python 3.11+ tu python.org va tich vao 'Add python.exe to PATH'.
    pause
    exit /b 1
)

:: 2. Kiem tra va tao Virtual Environment
if not exist "venv\Scripts\activate.bat" (
    echo [1/5] Dang tao moi virtual environment (venv)...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo [LOI] Khong the tao virtual environment.
        pause
        exit /b 1
    )
)

echo [2/5] Kich hoat moi truong venv...
call venv\Scripts\activate.bat

:: 3. Cai dat thu vien phu thuoc
echo [3/5] Kiem tra va cai dat thu vien trong requirements.txt...
pip install -r requirements.txt --quiet

:: 4. Kiem tra FFmpeg
where ffmpeg >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo [CANH BAO] FFmpeg chua duoc tim thay tren may!
    echo De cai dat FFmpeg tren Windows, hay mo PowerShell va chay lenh:
    echo     winget install Gyan.FFmpeg
    echo Sau khi cai dat xong, hay tat va khoi chay lai start.bat.
    echo.
)

:: 5. Kiem tra file .env
if not exist ".env" (
    if exist ".env.example" (
        copy .env.example .env >nul
        echo [THONG BAO] Da tao file .env tu .env.example.
        echo Hay mo file .env va dien GEMINI_API_KEY truoc khi dung tinh nang AI!
    )
)

:: 6. Tao thu muc assets neu chua co
if not exist "assets\minecraft" mkdir "assets\minecraft"
if not exist "assets\music" mkdir "assets\music"
if not exist "projects" mkdir "projects"

:: 7. Khoi dong server va mo trinh duyet
echo [4/5] Dang khoi dong may chu web tai http://127.0.0.1:8000...
start "" http://127.0.0.1:8000

echo [5/5] May chu dang chay. Nhan Ctrl+C de dung ung dung.
echo.
uvicorn main:app --host 127.0.0.1 --port 8000
