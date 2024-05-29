# Telegram Status (Game Activity Monitor)

## Description

Telegram Game Status is a Python application that monitors the games you're playing on your computer and automatically updates your Telegram profile status accordingly. With this app, you can showcase your gaming activity to your Telegram contacts, letting them know which game you're currently playing and for how long you've been playing it.


## Requirements

The following libraries are required for the project to run:

- `asyncio`
- `psutil`
- `tkinter`
- `telethon`
- `python-dotenv`
- `pyinstaller`
- `pillow`

You can install these dependencies using the `requirements.txt` file:

```bash
pip install -r requirements.txt
```

## Environment Variables
To ensure the project runs correctly, you need to set certain environment variables. Copy the sampl.env file to .env and fill in the required values:

The following environment variables are required for the application to function correctly:

``API_ID``: Your Telegram API ID, which is required for authenticating with the Telegram API.

``API_HASH``: Your Telegram API hash, which is also required for authentication.

``DEFAULT_BIO``: The default biography that will be set as your Telegram profile status when you're not playing any games.

``APP_ICON``: The path to the application icon file, which will be displayed in the application window.

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

![Main Menu](src/main_page.png)
![Game List](src/game_list.png)


### Before (When you close the game, your bio will be replaced with the default bio!) 

![Before](src/before.png)

### After

![Before](src/after.png)


## Contributing
If you want to contribute, please send a pull request or open an issue. Any contributions are welcome!

## License
This project is licensed under the [MIT License](LICENSE).