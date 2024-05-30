"""
Author: Phaticusthiccy
"""

"""
The code in gui.py is a Python script that creates a graphical user interface (GUI) application using the Tkinter library. The purpose of this application is to monitor running games on the user's computer and update their Telegram profile status accordingly.

The application takes input from the user in the form of game names. The user can add games to a list by typing the game name in an entry field and clicking the "Add" button or pressing Enter. The user can also remove games from the list by selecting a game and clicking the "Remove" button or pressing the Delete key.

The main output of the application is the user's Telegram profile status, which is updated to reflect the game they are currently playing and the elapsed time since they started playing it. If no game is being played, the profile status is set to a default biography entered by the user.

To achieve its purpose, the code follows this logic:

The user interface is created using Tkinter, with various widgets such as entry fields, listboxes, and buttons.
The user adds game names to the list, which are stored in the added_games list.
The code loads a mapping of game names to their corresponding process names from a JSON file (process_mapping.json).
The application continuously checks if any of the games in the added_games list are running on the user's computer using the psutil library.
If a game is running, the application calculates the elapsed time since the game started and updates the user's Telegram profile status using the Telethon library.
If no game is running, the application sets the user's Telegram profile status to the default biography entered by the user.
The application runs in an asynchronous event loop, updating the Telegram profile status every 60 seconds and periodically updating the GUI to keep it responsive.
Important logic flows and data transformations:

The find_process_name function is used to find the process name corresponding to a given game name by searching through the loaded process mapping.
The get_process_name and get_friendly_name functions are used to convert between game names and their corresponding process names, using the loaded process mapping.
The is_game_running function checks if a game with a given name is currently running on the user's computer by iterating over the running processes and comparing their names.
The update_status function is an asynchronous function that updates the user's Telegram profile status based on the currently running game and the elapsed time.
The main function is the core of the application, running in an asynchronous event loop and continuously checking for running games and updating the Telegram profile status accordingly.
The code also includes helper functions for handling user input, displaying messages, and managing the GUI window.
"""


import asyncio
import psutil
import sys
import time
import tkinter as tk
from tkinter import messagebox
import tkinter.font as tkfont
from telethon import TelegramClient
from telethon.tl.functions.account import UpdateProfileRequest
import json
from dotenv import load_dotenv
import os
import platform
from PIL import Image, ImageTk
import requests


load_dotenv()
added_games = []
default_bio = os.getenv("DEFAULT_BIO")
start = False
default_start = False
me_welcome = None
api_id = os.getenv("API_ID")
api_hash = os.getenv("API_HASH")
app_icon = os.getenv("APP_ICON")
ACTION_EMOJI_LESS_10_MIN = os.getenv("ACTION_EMOJI_LESS_10_MIN")
ACTION_EMOJI_10_TO_60_MIN = os.getenv("ACTION_EMOJI_10_TO_60_MIN")
ACTION_EMOJI_60_TO_120_MIN = os.getenv("ACTION_EMOJI_60_TO_120_MIN")
ACTION_EMOJI_MORE_120_MIN = os.getenv("ACTION_EMOJI_MORE_120_MIN")
global latest_version
global local_version
local_version = os.getenv("VERSION")

def get_latest_version():
    """
    Retrieves the latest version from the specified URL.

    Returns:
        str: The latest version number.
    """
    try:
        response = requests.get("https://raw.githubusercontent.com/phaticusthiccy/Telegram-Activity/master/sample.env")
        response.raise_for_status()
        for line in response.text.split("\n"):
            if line.startswith("VERSION="):
                return line.split("=")[1].strip('"')
    except requests.exceptions.RequestException as e:
        print(f"Error retrieving latest version: {e}")
    return None

async def print_me():
    """
    Asynchronously retrieves the user's own Telegram account information and stores it in the `me_welcome` global variable.
    """
    global me_welcome;
    me_welcome = await client.get_me()

def checkAuth():
    """
    Checks that the required configuration values are set before running the application.
    
    Raises:
        ValueError: If any of the required configuration values are missing.
    
    Returns:
        bool: True if all required configuration values are set, False otherwise.
    """
    if api_id is None or api_id == "":
        raise ValueError(os.getenv("APP_ID_MISSING"))
    if api_hash is None or api_hash == "":
        raise ValueError(os.getenv("APP_HASH_MISSING"))
    if default_bio is None or default_bio == "":
        raise ValueError(os.getenv("DEFAULT_BIO_MISSING"))
    if app_icon is None or app_icon == "":
        raise ValueError(os.getenv("APP_ICON_MISSING"))
    return True;

checkAuth()

def is_supported_os():
    """
    Checks if the current operating system is Windows, Linux or macOS.

    Returns:
        bool: True if the operating system is Windows, Linux or macOS, False otherwise.
    """
    system = platform.system().lower()
    return system == "windows" or system == "linux" or system == "darwin"

def load_process_mapping(file_path):
    """
    The function `load_process_mapping` reads and loads a JSON file from the specified file path.
    
    :param file_path: The `file_path` parameter in the `load_process_mapping` function is a string that
    represents the path to the file containing the process mapping data that you want to load and
    process. This file should be in a format that can be loaded using the `json.load()` function, such
    as a JSON
    :return: The function `load_process_mapping` reads a JSON file located at the `file_path` and
    returns the contents of the file as a Python dictionary after loading it using `json.load()`.
    """
    with open(file_path, 'r') as file:
        return json.load(file)

def handle_exit(signum, frame):
    """
    Handles the exit signal for the application.
    
    When the application receives an exit signal (e.g. from the user closing the window),
    this function is called to quit the main event loop and exit the application.
    """
    root.quit()
    sys.exit()
    
def capitalize_first_letters(text):
    """
    Capitalizes the first letter of each word in the given text.
    
    Args:
        text (str): The input text to capitalize.
    
    Returns:
        str: The input text with the first letter of each word capitalized.
    """
    words = text.split()
    capitalized_words = [word.capitalize() for word in words]
    return ' '.join(capitalized_words)

def find_process_name(name):
    """
    Finds the process name that matches the given name.
    
    Args:
        name (str): The name to search for.
    
    Returns:
        str or False: The matching process name, or False if no match is found.
    """
    name_lower = name.lower()
    for key, value in process_name_mapping.items():
        if name_lower in [item.lower() for item in value]:
            return key
    return False

def get_process_name(friendly_name):
    """
    Returns the process name for the given friendly name. If no mapping is found, the original friendly name is returned.
    
    Args:
        friendly_name (str): The friendly name to look up.
    
    Returns:
        str: The process name for the given friendly name, or the original friendly name if no mapping is found.
    """
    return friendly_name_mapping.get(friendly_name, friendly_name)

def get_friendly_name(process_name):
    """
    Returns the friendly name for the given process name. If no friendly name is
    defined, the original process name is returned.
    """
    return friendly_name_mapping.get(process_name, process_name)

def is_game_running(game_name):
    """
    Checks if a game with the given name is currently running on the system.
    
    Args:
        game_name (list[str]): A list of game names to check for.
    
    Returns:
        bool: True if a game with the given name is running, False otherwise.
    """
    for process in psutil.process_iter(['pid', 'name']):
        if any(name.lower() == process.info['name'].lower() for name in game_name):
            return True
    return False

def get_process_name(friendly_name):
    """
    Returns the process name for the given friendly name. If no mapping is found, the original friendly name is returned.
    
    Args:
        friendly_name (str): The friendly name to look up.
    
    Returns:
        str: The process name for the given friendly name, or the original friendly name if no mapping is found.
    """
    return friendly_name_mapping.get(friendly_name, friendly_name)

def get_friendly_name(process_name):
    """
    Returns a friendly name for the given process name. If no friendly name mapping is
    available, the original process name is returned.
    
    Args:
        process_name (str): The name of the process to get a friendly name for.
    
    Returns:
        str: The friendly name for the given process name, or the original process name
        if no friendly name mapping is available.
    """
    return friendly_name_mapping.get(process_name, process_name)

def is_game_running(game_name):
    """
    Checks if a game with the given name is currently running on the system.
    
    Args:
        game_name (Union[str, List[str]]): The name or list of names of the game to check for.
    
    Returns:
        bool: True if the game is running, False otherwise.
    """
    for process in psutil.process_iter(['pid', 'name']):
        if any(name.lower() == process.info['name'].lower() for name in game_name):
            return True
    return False

def is_any_game_running(game_names):
    """
    Checks if any of the specified games are currently running.
    
    Args:
        game_names (list[str]): A list of game names to check.
    
    Returns:
        str or None: The name of the first game found to be running, or None if no games are running.
    """
    for game_name in game_names:
        if is_game_running(game_name):
            return game_name[0]
    return None

async def update_status(game_name, elapsed_time, games):
    """
    Asynchronously updates the user's Telegram profile status based on the current game being played and the elapsed time.
    
    If no game is being played, the profile status is set to the default bio. Otherwise, the profile status is updated to show the name of the current game and the elapsed time playing it.
    
    The function also sends a message to the user's Telegram account with a list of the games that will trigger a profile status update.
    """
    await client.connect()
    global start
    if game_name == False and elapsed_time == False:

        """
        Updates the user's profile with the default biography.
        
        Attempts to update the user's profile with the default biography using the `UpdateProfileRequest` method from the Telegram client. If an exception occurs during the update, it is silently ignored.
        """
        try:
            await client(UpdateProfileRequest(about=default_bio))
        except:
            pass;

        if start == False:
            start = True
            text_start = ""
            for item in games:
                game_name2 = item[0]
                friendly_game_name2 = get_friendly_name(game_name2)
                process_name2 = find_process_name(friendly_game_name2)
                if any(key.lower() == process_name2.lower() for key in process_name_mapping):
                    friendly_game_name2 = capitalize_first_letters(process_name_mapping[process_name2][0])
                    text_start += "`" + friendly_game_name2 + "`\n"
                    
            if len(text_start) > 3800:
                text_start = text_start[:3800] + "..."
            try:
                await client.send_message("me", (os.getenv("START_MESSAGE").replace("#local_version", local_version)) + text_start, parse_mode="Markdown")
            except:
                await client.log_out()
                messagebox.showerror(os.getenv("ERROR"), os.getenv("CANT_CONNECT"))
                return handle_exit(None, None)
    else: 
        if start == False:
            start = True
            text_start = ""
            for item in games:
                game_name2 = item[0]
                friendly_game_name2 = get_friendly_name(game_name2)
                process_name2 = find_process_name(friendly_game_name2)
                if any(key.lower() == process_name2.lower() for key in process_name_mapping):
                    friendly_game_name2 = capitalize_first_letters(process_name_mapping[process_name2][0])
                    text_start += "`" + friendly_game_name2 + "`\n"

            if len(text_start) > 3800:
                text_start = text_start[:3800] + "..."
            try:
                await client.send_message("me", (os.getenv("START_MESSAGE").replace("#local_version", local_version)) + text_start, parse_mode="Markdown")
            except:
                await client.log_out()
                messagebox.showerror(os.getenv("ERROR"), os.getenv("CANT_CONNECT"))
                return handle_exit(None, None)

        friendly_game_name = get_friendly_name(game_name)
        friendly_game_name = capitalize_first_letters(process_name_mapping[find_process_name(friendly_game_name)][0])
        action_emoji = ""

        if elapsed_time < 10:
            action_emoji = ACTION_EMOJI_LESS_10_MIN
        elif elapsed_time > 9 and elapsed_time < 60:
            action_emoji = ACTION_EMOJI_10_TO_60_MIN
        elif elapsed_time > 59 and elapsed_time < 120:
            action_emoji = ACTION_EMOJI_60_TO_120_MIN
        elif elapsed_time > 119:
            action_emoji = ACTION_EMOJI_MORE_120_MIN
        
        new_status = os.getenv("ACTION_STATUS")
        new_status = new_status.replace("#action_emoji", action_emoji).replace("#game_name", friendly_game_name).replace("#elapsed_time", str(elapsed_time + 1))
        try:
            await client(UpdateProfileRequest(about=new_status))
        except:
            messagebox.showerror(os.getenv("ERROR"), os.getenv("TOO_LONG"))
            root.quit()
            sys.exit()
        
    await client.disconnect()

async def main(games, root):
    """
    Runs the main event loop for the GUI, updating the status of any running games.
    
    This function is responsible for the core logic of the GUI application. It continuously checks if any games are running, and if so, updates the elapsed time for the currently running game. If no games are running, it updates the status to indicate that.
    
    The function runs in an asynchronous event loop, sleeping for 60 seconds between each check for running games. It also periodically updates the GUI's main window to ensure the UI stays responsive.
    
    Args:
        games (dict): A dictionary of running games, where the keys are game names and the values are game objects.
        root (tkinter.Tk): The main window of the GUI application.
    """
    start_time = None
    current_game = None

    while True:
        game_name = is_any_game_running(games)
        if game_name:
            if current_game != game_name:
                current_game = game_name
                start_time = time.time()
            elapsed_time = int((time.time() - start_time) / 60)
            await update_status(current_game, elapsed_time, games)
        else:
            await update_status(False, False, games)
            start_time = None
            current_game = None
        
        await asyncio.sleep(60)  
        root.update_idletasks()
        root.update()

def start_monitoring(games, root):
    """
    Starts the main event loop and creates a task to run the main application logic.
    
    Args:
        games (list): A list of game objects to monitor.
        root (tkinter.Tk): The root Tkinter window for the application.
    """
    loop = asyncio.get_event_loop()
    loop.create_task(main(games, root))
    loop.run_forever()

def add_game(event=None):
    """
    Adds a new game to the list of added games.
    
    This function is called when the user enters a game name in the game entry field and presses the "Add" button or hits Enter. It retrieves the process name for the entered game, checks if it's already in the list of added games, and if not, adds it to the list and the games listbox. If the game is not found in the database, a warning message is displayed.
    
    Args:
        event (Optional[tkinter.Event]): The event that triggered the function (e.g., button click or Enter key press).
    
    Raises:
        None
    """
    friendly_name = game_entry.get()
    if friendly_name:
        process_names = get_process_name(friendly_name)
        if process_names in added_games:
            messagebox.showerror(os.getenv("ERROR"), "This game has already been added!")
            return
        added_games.append(process_names)
        findgame = find_process_name(process_names)
        if findgame == False:
            return messagebox.showwarning(os.getenv("WARNING"), "This game is not in the database!")
        games_listbox.insert(tk.END, process_names)
        game_entry.delete(0, tk.END)
    else:
        messagebox.showwarning(os.getenv("WARNING"), os.getenv("VALID_GAME_NAME"))

def remove_game(arg=None):
    """
    Removes the selected game from the games_listbox and the added_games list.
    
    If no game is selected, displays a warning message.
    """
    selected_game = games_listbox.curselection()
    if selected_game:
        game_to_remove = games_listbox.get(selected_game)
        games_listbox.delete(selected_game)
        if game_to_remove in added_games:
            added_games.remove(game_to_remove)
    else:
        messagebox.showwarning(os.getenv("WARNING"), os.getenv("SELECT_GAME_TO_DEL"))

def start_button_click():
    """
    Starts the game monitoring process when the user clicks the start button.
    
    This function is called when the user clicks the "Start" button in the GUI. It retrieves the list of games selected in the listbox, checks if the default biography is within the character limit, and then starts the game monitoring process. If no games are selected, it displays a warning message.
    """
    if not is_supported_os():
        print(os.getenv("UNSUPPORTED_OS"))
        return

    games = [tuple(games_listbox.get(i).split(", ")) for i in range(games_listbox.size())]
    if games:
        global default_bio
        default_bio = default_bio_text.get("1.0", tk.END)
        if len(default_bio) > 70:
            messagebox.showerror(os.getenv("ERROR"), "The default bio cannot be more than 70 characters!")
            return
        messagebox.showinfo(os.getenv("STARTED"), os.getenv("STARTED_MESSAGE"))
        root.destroy()
        print(os.getenv("CONSOLE_START_MESSAGE"))
        start_monitoring(games, root)
    else:
        messagebox.showwarning(os.getenv("WARNING"), os.getenv("ADD_AT_LEAST_ONE_GAME"))

def add_game_to_list(process_name, list_window):
    """
    Adds a game to the list of added games.
    
    Args:
        process_name (str): The name of the game to be added.
        list_window (tkinter.Toplevel): The window containing the list of games.
    
    Returns:
        callable: A function that can be called to add the game to the list.
    """
    def add_to_list():
        if process_name in added_games:
            messagebox.showerror(os.getenv("ERROR"), os.getenv("ALREADY_ADDED"))
            return
        else:
            added_games.append(process_name)
            games_listbox.insert(tk.END, process_name)
            list_window.destroy()

    return add_to_list

def add_placeholder(entry, placeholder):
    """
    Adds a placeholder text to an entry widget and handles focus events to show/hide the placeholder.
    
    Args:
        entry (tkinter.Entry): The entry widget to add the placeholder to.
        placeholder (str): The placeholder text to display.
    """
    entry.insert(0, placeholder)
    entry.config(fg='grey', cursor="hand2")

    def on_focus_in(event):
        if entry.get() == placeholder:
            entry.delete(0, tk.END)
            entry.config(fg='blue')

    def on_focus_out(event):
        if entry.get() == '':
            entry.insert(0, placeholder)
            entry.config(fg='grey')

    entry.bind("<FocusIn>", on_focus_in)
    entry.bind("<FocusOut>", on_focus_out)

def remove_all_games():
    """
    Removes all games from the games_listbox and the added_games list.
    """
    games_listbox.delete(0, tk.END)
    added_games.clear()


def show_list():
    """
    Displays a list of games in a separate window, allowing the user to search and add games to a list.
    
    The `show_list()` function creates a new window with a list of games, a search field, and buttons to add selected games to a list and close the window.
    
    The list of games is retrieved from the `process_name_mapping` dictionary, which maps game names to their corresponding process names. The list is filtered based on the user's search input, and the matching games are displayed in a listbox.
    
    When the user selects a game from the listbox and presses the "Add" button, the selected game is added to the `added_games` list and displayed in the main application's games listbox.
    """
    def filter_list(event):
        """
        Filters the listbox display based on the search term entered by the user.
        
        This function is called whenever the user types into the search box. It updates the listbox to only display items that match the search term, either in the key (game name) or the process name mapping.
        
        Args:
            event (tkinter.Event): The event object passed to the function by the Tkinter event handler.
        """
        search_term = search_var.get().lower()
        if search_term == os.getenv("FRAME_HINT_PLACEHOLDER").lower():
            search_term = None
        listbox.delete(0, tk.END)
        for key in sorted_keys:
            if key in added_games:
                continue
            if not search_term or search_term in key.lower() or search_term in process_name_mapping[key][0].lower():
                display_text = f"{capitalize_first_letters(process_name_mapping[key][0])} :: {key}"
                listbox.insert(tk.END, display_text)

                
    def add_on_double_click(event):
        """
        Adds the double-clicked game from the listbox to the list of added games, and updates the games listbox accordingly.
        """
        try:
            selected_game = listbox.get(listbox.curselection())
        except:
            return;
        if selected_game:
            try:
                selected_game = selected_game.split(":: ")[1]
            except:
                return

            if selected_game in added_games:
                messagebox.showerror(os.getenv("ERROR"), os.getenv("ALREADY_ADDED"))
                return
            else:
                added_games.append(selected_game)
                games_listbox.insert(tk.END, selected_game)
                listbox.selection_clear(0, tk.END)
                filter_list(None)

    def add_all_games():
        """
        Adds all games from the process_name_mapping to the added_games list and the games_listbox.
        """
        for game in sorted_keys:
            if game not in added_games:
                added_games.append(game)
                games_listbox.insert(tk.END, game)
        list_window.destroy()

    list_window = tk.Toplevel(root)
    list_window.title(os.getenv("FRAME_GAME_LIST"))
    list_frame = tk.Frame(list_window)
    list_frame.pack(padx=20, pady=20)


    search_var = tk.StringVar()
    search_entry = tk.Entry(list_frame, textvariable=search_var, font=(poppins_font, 12), width=50)
    search_entry.grid(row=0, column=0, columnspan=2, pady=10)
    add_placeholder(search_entry, os.getenv("FRAME_HINT_PLACEHOLDER"))
    search_entry.bind("<KeyRelease>", filter_list)

    label_Text_Found_Games = os.getenv("FRAME_FOUND_GAMES")
    label_Text_Found_Games = label_Text_Found_Games.replace("#game_count", str(len(process_name_mapping)))
    label = tk.Label(list_frame, text=label_Text_Found_Games, font=(poppins_font, 12))
    label.grid(row=1, column=0, columnspan=2, pady=10)

    listbox = tk.Listbox(list_frame, width=60, height=20, selectmode=tk.SINGLE, cursor="hand2")
    listbox.grid(row=2, column=0, columnspan=2, pady=10)
    
    unique_keys = set()
    sorted_keys = sorted(process_name_mapping.keys())

    for key in sorted_keys:
        if key in added_games:
            continue
        if key not in unique_keys:
            unique_keys.add(key)
            display_text = f"{capitalize_first_letters(process_name_mapping[key][0])} :: {key}"
            listbox.insert(tk.END, display_text)


    def add_to_list(arg=None):
        """
        Adds the selected game from the listbox to the list of added games, and updates the games listbox accordingly.
        
        Args:
            arg (Optional[Any]): Unused argument, required for the Tkinter event handler.
        
        Raises:
            None
        """
        selected_game = listbox.get(tk.ANCHOR)
        if selected_game:
            try:
                selected_game = selected_game.split(":: ")[1]
            except:
                return

            if selected_game in added_games:
                messagebox.showerror(os.getenv("ERROR"), os.getenv("ALREADY_ADDED"))
                return
            else:
                added_games.append(selected_game)
                games_listbox.insert(tk.END, selected_game)
                listbox.selection_clear(0, tk.END)  
                filter_list(None)

    listbox.bind("<Return>", add_to_list)
    listbox.bind("<Double-1>", add_on_double_click)
    add_button = tk.Button(list_frame, text=os.getenv("ADD"), command=add_to_list)
    add_button.grid(row=3, column=0, padx=10, pady=10)

    add_all_button = tk.Button(list_frame, text=os.getenv("ADD_ALL"), command=add_all_games, font=(poppins_font, 12))
    add_all_button.grid(row=3, column=2, padx=10, pady=10)

    close_button = tk.Button(list_frame, text=os.getenv("CLOSE"), command=list_window.destroy)
    close_button.grid(row=3, column=1, padx=10, pady=10)

    list_window.resizable(False, False)



"""
Loads the process mapping from a JSON file located at the specified path.

Args:
    mapping_file_path (str): The path to the JSON file containing the process mapping.

Returns:
    dict: A dictionary containing the process name mapping.
"""

mapping_file_path = os.getenv("GAME_DATA_JSON")
process_name_mapping = load_process_mapping(mapping_file_path)

"""
Initializes a Telegram client and starts the client session.

The `TelegramClient` object is used to interact with the Telegram API. This code initializes a new client instance with the provided API ID and hash, and then starts the client session.

The client session is required for making API calls to Telegram, such as sending messages, retrieving data, and more.
"""
client = TelegramClient(os.getenv("SESSION_NAME"), int(api_id), api_hash)
client.start()

"""
Builds a mapping of friendly names to process names by converting all process names to lowercase and creating a dictionary that maps each friendly name to its corresponding process name.

The `process_name_mapping` dictionary is used to store the mapping of process names to their friendly names. The `friendly_name_mapping` dictionary is then created by iterating over the `process_name_mapping` and creating a new dictionary that maps each friendly name to its corresponding process name.
"""
for key, value in process_name_mapping.items():
    process_name_mapping[key] = [name.lower() for name in value]
friendly_name_mapping = {name: process_name for process_name, names in process_name_mapping.items() for name in names}

loop = asyncio.get_event_loop()
loop.run_until_complete(print_me())

root = tk.Tk()
root.title(f"{os.getenv('APP_TITLE')} v{local_version}")
icon_image = Image.open(str(app_icon))
icon_image = icon_image.convert('RGBA')
icon = ImageTk.PhotoImage(icon_image)
root.iconphoto(False, icon)

label_frame = tk.Frame(root)
label_frame.pack(pady=0)

poppins_font = tkfont.Font(family="/fonts/Poppins-Regular.ttf")

welcome_label = os.getenv("WELCOME")
welcome_label = welcome_label.replace("#firs_name", me_welcome.first_name)
label = tk.Label(label_frame, text=welcome_label, font=(poppins_font, 20))
label.pack()

frame = tk.Frame(root)
frame.pack(padx=40, pady=0)

frame = tk.Frame(root)
frame.pack(padx=40, pady=40)

label = tk.Label(frame, text=os.getenv("ADD_GAME"), font=(poppins_font, 12))
label.grid(row=0, column=0, sticky="w", padx=5, pady=5)

game_entry = tk.Entry(frame, width=30, font=(poppins_font, 12), cursor="hand2")
game_entry.grid(row=0, column=1, padx=5, pady=5)
game_entry.bind("<Return>", add_game)

add_button = tk.Button(frame, text=os.getenv("ADD_GAME_BUTTON"), command=add_game, font=(poppins_font, 12), cursor="hand2")
add_button.grid(row=0, column=2, padx=5, pady=5)

list_button = tk.Button(frame, text=os.getenv("LIST_OF_GAMES"), command=show_list, font=(poppins_font, 12), cursor="hand2")
list_button.grid(row=0, column=3, padx=5, pady=5)

games_listbox = tk.Listbox(frame, selectmode=tk.SINGLE, width=50, font=(poppins_font, 12))
games_listbox.grid(row=1, column=0, columnspan=4, padx=5, pady=5)
games_listbox.bind("<Delete>", remove_game)

remove_button = tk.Button(frame, text=os.getenv("DELETE"), command=remove_game, font=(poppins_font, 12), cursor="hand2")
remove_button.grid(row=2, column=0, padx=5, pady=5, sticky="ew")

remove_all_button = tk.Button(frame, text=os.getenv("DELETE_ALL"), command=remove_all_games, font=(poppins_font, 12), cursor="hand2")
remove_all_button.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

start_button = tk.Button(frame, text=os.getenv("RUN"), command=start_button_click, font=(poppins_font, 12), cursor="hand2")
start_button.grid(row=2, column=2, columnspan=2, padx=5, pady=5, sticky="ew")

default_bio_label = tk.Label(frame, text=os.getenv("DEFAULT_BIO_LABEL"), font=(poppins_font, 12))
default_bio_label.grid(row=3, column=0, sticky="w", padx=5, pady=5)

default_bio_text = tk.Text(frame, width=50, height=4, font=(poppins_font, 12), cursor="hand2")
default_bio_text.insert(tk.END, default_bio)
default_bio_text.grid(row=3, column=1, columnspan=3, padx=5, pady=5)

emoji_font = tkfont.Font(family="Segoe UI Emoji", size=12)
emoji_font2 = tkfont.Font(family="Noto Color Emoji", size=12)
default_bio_text.configure(font=emoji_font)
default_bio_text.configure(font=emoji_font2)


latest_version = get_latest_version()

"""
Displays a warning message to the user if a newer version of the application is available.

The message includes the latest version number and the current version number, and is displayed using the Tkinter messagebox.showwarning() function.
"""
if latest_version and local_version and str(latest_version) != str(local_version):
    messagebox.showwarning(os.getenv("UPDATE_AVAILABLE"), os.getenv("UPDATE_AVAILABLE_MESSAGE").replace("#latest_version", latest_version).replace("#current_version", local_version))

root.mainloop()