# Telegram Status (Game Activity Monitor)

[<img src="https://images.emojiterra.com/openmoji/v15.0/512px/1f1ec-1f1e7.png" alt="English" width="30" height="30"> English](README.md)

[<img src="https://images.emojiterra.com/openmoji/v15.0/512px/1f1f9-1f1f7.png" alt="Türkçe" width="30" height="30"> Türkçe](README.tr.md)


## Description

Telegram Game Status is a Python application that monitors the games you're playing on your computer and automatically updates your Telegram profile status accordingly. With this app, you can showcase your gaming activity to your Telegram contacts, letting them know which game you're currently playing and for how long you've been playing it.


## Requirements

Firstly, clone the poject to your computer:

```bash
git clone https://github.com/phaticusthiccy/Telegram-Activity && cd ./Telegram-Activity
```

## 

The following libraries are required for the project to run:

- `asyncio`
- `psutil`
- `tkinter`
- `telethon`
- `python-dotenv`
- `pyinstaller`
- `pillow`
- `requests`
- `sv_ttk`

You can install these dependencies using the `requirements.txt` file:

```bash
pip install -r requirements.txt
```

## Environment Variables
To ensure the project runs correctly, you need to set certain environment variables. Copy the sample.env file to .env and fill in the required values:

The following environment variables are required for the application to function correctly:

``API_ID``: Your Telegram API ID, which is required for authenticating with the Telegram API.

``API_HASH``: Your Telegram API hash, which is also required for authentication.

``DEFAULT_BIO``: The default biography that will be set as your Telegram profile status when you're not playing any games.

⚠ Just edit these 3 variables! If you do not know the other variables, please do not change or delete them!

```bash
cp sample.env .env
```

After copying it, start the edit file with this command:

```bash
nano .env
```

## Usage
To run the GUI application, use the gui.py file:

> ```bash
> python gui.py
> ```
> or
> ```bash
> py gui.py
> ```


## Demo

![Main Menu](src/main_page_en.png)
![Game List](src/game_list_en.png)


### Before (When you close the game, your bio will be replaced with the default bio!) 

![Before](src/before.png)

### After

![After](src/after_en.png)


## Contributing
If you want to contribute, please send a pull request or open an issue. Any contributions are welcome!

> [You can create a request for a new game by clicking here!](https://github.com/phaticusthiccy/Telegram-Activity/issues/new?assignees=phaticusthiccy&labels=enhancement%2C+game+request&projects=&template=new-game-request.md&title=%5BREQUEST%5D+New+Game+Request)

⚠ Note :: This project is still in development, so there might be some bugs. Please report them if you find any. Also if you wan to add more games to the game list use method below. Make changes, create pull request and I'll merge it if its ok!

```json
{
    "actual_process_name": ["real game name", "keyword 1", "keyword 2", "keyword n..", "actual_process_name"],
    "my_game.exe": ["My Awsome Game", "awsome game", "mygame", "my_game.exe"]
}
```

## License
This project is licensed under the [MIT License](LICENSE).

## Troubleshooting

If you encounter any issues while using the application, you can try the following troubleshooting steps:

### 1. Check Environment Variables
Ensure that you have correctly set the required environment variables (`API_ID`, `API_HASH`, and `DEFAULT_BIO`). Double-check the values and make sure they are correct.

### 2. Check Telegram Connection
Make sure you have an active internet connection and that the Telegram servers are accessible. You can try sending a message to another Telegram user or group to verify your connection.

### 3. Check Game List
If the application is not detecting a game you're playing, ensure that the game is included in the `process_mapping.json` file. If not, you can add it by following the instructions in the "Contributing" section.

### 4. Check Permissions
On some systems, the application may require additional permissions to monitor running processes. Try running the application with administrative privileges.

### 5. Check Logs
The application logs errors and warnings to the console. Check the console output for any error messages or warnings that may provide clues about the issue you're facing.

### 6. Update Dependencies
Ensure that you have the latest versions of the required dependencies installed. You can update them by running the following command:

```bash
pip install -r requirements.txt --upgrade
```

### 7. Fix High CPU Usage
CPU usage may be high for 10-30 seconds after the application runs. This may occur because the application is running in a way that requires access to games. Do not worry!

This situation is only temporary. CPU usage will drop within 1 minute. If a persistently high CPU usage occurs, [follow the steps here!](https://github.com/phaticusthiccy/Telegram-Activity/wiki/High-CPU-Usage-Solution)