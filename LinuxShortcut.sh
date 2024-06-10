#!/bin/bash

currentDir=$(pwd)

desktopPath="$HOME/Desktop"

echo '#!/bin/bash' > "$desktopPath/Game_Monitor.sh"
echo "cd \"$currentDir\"" >> "$desktopPath/Game_Monitor.sh"
echo "python3 gui.py" >> "$desktopPath/Game_Monitor.sh"
echo "read -p 'Press any key to continue...'" >> "$desktopPath/Game_Monitor.sh"

chmod +x "$desktopPath/Game_Monitor.sh"

echo "The Game_Monitor.sh file has been created on the desktop!"
