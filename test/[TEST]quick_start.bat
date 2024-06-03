@echo off
git clone https://github.com/phaticusthiccy/Telegram-Activity
cd Telegram-Activity
pip install -r requirements.txt
copy sample.env .env
pause
start notepad .env
python gui.py
IF %ERRORLEVEL% NEQ 0 (
    py gui.py
)
pause
