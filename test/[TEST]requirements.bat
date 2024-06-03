@echo off
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    pause
    exit /b 1
)
pip --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    pause
    exit /b 1
)
pip install asyncio
pip install psutil
pip install telethon
pip install python-dotenv
pip install pillow
pip install requests
pip install sv_ttk

echo.
pause
