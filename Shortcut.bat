@echo off
set "currentDir=%cd%"

set "driveLetter=%currentDir:~0,1%"

set "desktopPath=%USERPROFILE%\Desktop"

echo @echo off > "%desktopPath%\Game Monitor.bat"

if /I "%driveLetter%"=="D" (
    echo cd /d %currentDir% >> "%desktopPath%\Game Monitor.bat"
) else (
    echo cd %currentDir% >> "%desktopPath%\Game Monitor.bat"
)

echo python gui.py >> "%desktopPath%\Game Monitor.bat"
echo pause >> "%desktopPath%\Game Monitor.bat"

echo The "Game Monitor.bat" file has been created on the desktop!
pause
