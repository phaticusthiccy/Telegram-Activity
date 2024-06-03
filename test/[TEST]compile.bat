@echo off
git clone https://github.com/phaticusthiccy/Telegram-Activity
cd Telegram-Activity
pip install -r requirements.txt
pip install pyinstaller
copy sample.env .env
pause
start notepad .env
pyinstaller --onefile --windowed gui.py
pause
