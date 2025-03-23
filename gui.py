"""
Author: Phaticusthiccy

This Python script is a graphical user interface (GUI) application built using the Tkinter library. The application allows users to monitor and display their activity status on the Telegram messaging platform based on the games they are currently playing.

The main features of the application include:

1. Adding and removing games to a list of monitored games.
2. Displaying a list of available games to choose from.
3. Setting a default biography message.
4. Updating the user's Telegram status with the current game being played and the elapsed time.
5. Displaying notifications and error messages.
6. Changing the application theme between light and dark mode.
7. Sending Telegram notifications to specified users when a game starts.

The application uses the Telethon library to interact with the Telegram API and update the user's status. It also utilizes the psutil library to monitor running processes and detect the games being played.

The application loads a mapping of game names to their corresponding process names from a JSON file. This mapping is used to identify the games being played based on the running processes.

The main components of the GUI include:

- A welcome label displaying the user's first name.
- An entry field and button for adding games to the monitored list.
- A listbox displaying the added games.
- Buttons for removing games from the list, displaying a list of available games, and starting the monitoring process.
- A text area for setting the default biography message.
- A button for changing the application theme.
- An entry field for specifying Telegram usernames to notify.

The application also includes logging functionality to log debug messages, errors, and other information to the console and a log file.

Usage:
1. Enter your Telegram API credentials and other required configuration values in the `.env` file.
2. Run the script to launch the GUI application.
3. Add the games you want to monitor to the list.
4. Set the default biography message.
5. Enter Telegram usernames to notify (optional).
6. Click the "Start" button to begin monitoring and updating your Telegram status.

Note: This application requires a Telegram account and API credentials to function correctly.
"""


import asyncio
from turtle import color
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
import sv_ttk
import logging
from datetime import datetime
import GPUtil

"""
Configures the logging system for the application.

Adds a console handler and a file handler to the root logger, both set to log at the DEBUG level. The console handler and file handler use a common formatter that includes the timestamp, log level, and log message.

The root logger is also set to log at the DEBUG level, ensuring that all log messages at or above the DEBUG level will be captured by the configured handlers.
"""
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
file_handler = logging.FileHandler('./debug/debug.log')
file_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(console_handler)
logger.addHandler(file_handler)

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
STATS_FILE = os.getenv("STATS_FILE")
game_stats = json.load(open('./game_stats.json'))
notification_usernames = []
global playing_game
playing_game = None
notification_message_text_global = None

if "notification_usernames" in game_stats:
    notification_usernames = game_stats["notification_usernames"]
else:
    game_stats["notification_usernames"] = []

if "notification_message" in game_stats:
    notification_message_text_global_str = game_stats["notification_message"]
else:
    game_stats["notification_message"] = os.getenv("NOTIFICATION_MESSAGE")
    notification_message_text_global_str = os.getenv("NOTIFICATION_MESSAGE")

if "default_bio" in game_stats:
    default_bio = game_stats["default_bio"]
else:
    game_stats["default_bio"] = os.getenv("DEFAULT_BIO")
    default_bio = os.getenv("DEFAULT_BIO")


def get_cpu_usage():
    """
    Gets the current CPU usage as a percentage.

    Args:
        process_name (str): The name of the process to get the CPU usage for.

    Returns:
        float: The current CPU usage as a percentage.
    """
    return psutil.cpu_percent()

def get_gpu_usage():
    """
    Gets the current GPU usage as a percentage.

    Returns:
        float: The current GPU usage as a percentage.
    """
    return (max(GPUtil.getGPUs(), key=lambda gpu: gpu.load).load) * 100

def log_game_start(game_name):
    """
    Logs the start of a game session in the game_stats dictionary.

    Args:
        game_name (str): The name of the game being played.

    Notes:
        The start time is recorded in ISO format using datetime.now().isoformat().
        If the game is not already in the daily stats dictionary, a new entry is created with a start time and total duration of 0.
    """
    current_time = datetime.now().isoformat()
    if game_name not in game_stats["daily"]:
        game_stats["daily"][game_name] = {"start_time": current_time, "total_duration": 1}

def log_game_end(game_name):
    """
    Logs the end of a game session in the game_stats dictionary.

    Args:
        game_name (str): The name of the game being played.

    Notes:
        The end time is recorded in ISO format using datetime.now().isoformat().
        The duration of the session is calculated by taking the difference between the start and end times.
        The total duration of all sessions for the game is incremented by the duration of this session.
        The updated game_stats dictionary is written to the file specified by STATS_FILE by calling _save_stats_to_file.
    """
    if game_name in game_stats["daily"]:
        start_time = datetime.fromisoformat(game_stats["daily"][game_name]["start_time"])
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds() / 60
        game_stats["daily"][game_name]["total_duration"] += duration
        game_stats["daily"][game_name]["total_duration"] = game_stats["daily"][game_name]["total_duration"] / 10
        _save_stats_to_file()


def _save_stats_to_file():
    """Writes the game_stats dictionary to the file specified by STATS_FILE in JSON format."""
    with open(STATS_FILE, 'w') as f:
        json.dump(game_stats, f, indent=4)

async def get_first_name(username):
    """
    Asynchronously retrieves the first name of a Telegram user given their username.

    Args:
        username (str): The Telegram username of the user.

    Returns:
        str: The first name of the user, or None if the user is not found or an error occurs.
    """
    try:
        user = await client.get_entity(username)
        return user.first_name
    except Exception as e:
        logger.warning(f"Could not get first name for {username}: {e}")
        return False


def get_latest_version():
    """
    Retrieves the latest version information from a remote source.

    Returns:
        dict: A dictionary containing the latest version and update message, or None if an error occurred.
    """
    try:
        response = requests.get("https://raw.githubusercontent.com/phaticusthiccy/Telegram-Activity/master/sample.env")
        response.raise_for_status()
        message_payload = {
            "version": "",
            "message": ""
        }
        for line in response.text.split("\n"):
            if line.startswith("VERSION="):
                message_payload["version"] = line.split("=")[1].strip('"')
            if line.startswith("UPDATE_MESSAGE="):
                message_payload["message"] = line.split("=")[1].strip('"')
        return message_payload
    except requests.exceptions.RequestException as e:
        logger.error(f"Error retrieving latest version: {e}")
    return {
        "version": "",
        "message": ""
    }

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
    if not os.path.isfile(".env"):
        raise ValueError("The .env file is missing!")
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
logger.info(os.getenv("LOADING_MESSAGE"))
logger.info(os.getenv("DEBUG_ON")) if os.getenv("DEBUG") == "true" else None

local_version = os.getenv("VERSION")
logger.info(os.getenv("DEBUG_VERSION") + local_version) if os.getenv("DEBUG") == "true" else None

def toggle_debug_mode(fromTheme):
    """
    Toggles the debug mode for the application.

    Args:
        fromTheme (bool): Indicates whether the toggle was triggered from a theme change.

    Returns:
        None
    """
    if not fromTheme:
        if debug_mode_var.get():
            os.environ["DEBUG"] = "true"
            logger.info(os.getenv("DEBUG_MODE_ON"))
        else:
            os.environ["DEBUG"] = "false"
            logger.info(os.getenv("DEBUG_MODE_OFF"))

    if theme == 0:
        debug_mode_button.configure(selectcolor="black")
        hint_mode_button.configure(selectcolor="black")
    else:
        debug_mode_button.configure(selectcolor="white")
        hint_mode_button.configure(selectcolor="white")
    return

def toggle_hint_mode(fromTheme):
    if not fromTheme:
        if hint_mode_var.get():
            os.environ["HINTS"] = "true"
            logger.info(os.getenv("HINTS_ON"))
        else:
            os.environ["HINTS"] = "false"
            logger.info(os.getenv("HINTS_OFF"))

    if theme == 0:
        return hint_mode_button.configure(selectcolor="black")
    else:
        return hint_mode_button.configure(selectcolor="white")

def is_supported_os():
    """
    Returns the current system platform as a lowercase string.

    This function checks the current system platform and returns it as a lowercase string. If the DEBUG environment variable is set to "true", it will also log the system platform to the logger.

    Returns:
        str: The current system platform as a lowercase string.
    """
    system = platform.system().lower()
    logger.info(os.getenv("DEBUG_SYSTEM") + system) if os.getenv("DEBUG") == "true" else None
    return system

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
    try:
        root.quit()
    except:
        pass
    logger.info(os.getenv("DEBUG_LOGOUT") + local_version) if os.getenv("DEBUG") == "true" else None
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

def show_stats():
    """
    Creates a new window to show game statistics.
    """
    stats_window = tk.Toplevel(root)
    stats_window.title(os.getenv("STATS_TITLE"))

    time_frame = tk.StringVar(value="daily")
    tk.Radiobutton(stats_window, text=os.getenv("DAILY"), variable=time_frame, value="daily", selectcolor="gray").pack()

    tk.Button(stats_window, text=os.getenv("GENERATE_REPORT"), command=lambda: _generate_report(time_frame.get())).pack()

def _generate_report(time_frame):
    """
    Generates a bar chart with the total durations of each game in the given time frame.

    Args:
        time_frame (str): The time frame to generate the report for, either "daily" or "weekly".

    Returns:
        None
    """
    import matplotlib.pyplot as plt
    import numpy as np
    from matplotlib.patches import ConnectionPatch
    from matplotlib.widgets import Button

    data = game_stats["daily"] 

    labels = list(data.keys())
    total_durations = [v['total_duration'] for v in data.values()]
    sum_total = sum(total_durations)
    overall_ratios = [dur / sum_total for dur in total_durations]

    fig = plt.figure(figsize=(12, 6))
    ax1 = fig.add_axes([0.3, 0.1, 0.35, 0.8])
    ax2 = fig.add_axes([0.7, 0.1, 0.25, 0.8])

    def draw_plots(selected_label):
        idx = labels.index(selected_label)
        explode = [0] * len(labels)
        explode[idx] = 0.1
        ax1.clear()
        ax2.clear()

        angle = -180 * overall_ratios[idx]
        wedges, texts, autotexts = ax1.pie(overall_ratios, autopct='%1.1f%%',
                                        startangle=angle, labels=labels,
                                        explode=explode, textprops={'fontsize': 8})
        
        game_data = data[selected_label]
        played_time = game_data['total_duration']
        ax1.text(0, -1.5, f'{os.getenv("PLAYED_TIME")} {played_time:.2f} {os.getenv("DURATION")}', 
                ha='center', fontsize=10, bbox=dict(facecolor='white', alpha=0.5))
        
        wedge = wedges[idx]
        theta1, theta2 = wedge.theta1, wedge.theta2
        center, r = wedge.center, wedge.r
        
        game_data = data[selected_label]
        cpu = game_data['avgCPUusage'] / 100
        gpu = game_data['avgGPUusage'] / 100
        age_ratios = [cpu, gpu]
        age_labels = ['CPU', 'GPU']
        
        bottom = 1
        width = 0.2
        colors = ['#1f77b4', '#ff7f0e']
        
        for j, (height, label) in enumerate(reversed(list(zip(age_ratios, age_labels)))): 
            bottom -= height
            bars = ax2.bar(0, height, width, bottom=bottom, color=colors[j],
                        label=label, alpha=0.7)
            ax2.bar_label(bars, labels=[f"{height*100:.0f}%"],
                        label_type='center', color='white')
        
        
        ax2.set_title(f'{os.getenv("COMPUTE_USAGE")} ({selected_label})', pad=20)
        ax2.legend(loc='upper right')
        ax2.axis('off')
        ax2.set_xlim(-2.5 * width, 2.5 * width)
        
        bar_top = 1.0
        bar_bottom = 1.0 - sum(age_ratios)
        
        x_top = r * np.cos(np.pi / 180 * theta2) + center[0]
        y_top = r * np.sin(np.pi / 180 * theta2) + center[1]
        con_top = ConnectionPatch(xyA=(-width/2, bar_top), coordsA=ax2.transData,
                                xyB=(x_top, y_top), coordsB=ax1.transData, color='gray')
        ax2.add_artist(con_top)
        
        x_bot = r * np.cos(np.pi / 180 * theta1) + center[0]
        y_bot = r * np.sin(np.pi / 180 * theta1) + center[1]
        con_bot = ConnectionPatch(xyA=(-width/2, bar_bottom), coordsA=ax2.transData,
                                xyB=(x_bot, y_bot), coordsB=ax1.transData, color='gray')
        ax2.add_artist(con_bot)
        
        fig.canvas.draw_idle()

    try:
        current_selection = labels[0]
    except:
        messagebox.showinfo("Error", os.getenv("NO_GAME_DATA"))
        return
        
    draw_plots(current_selection)

    menu_start_pos = [-0.25, 0.1, 0.2, 0.8]
    menu_end_pos = [0.05, 0.1, 0.2, 0.8]

    menu_ax = fig.add_axes(menu_start_pos)
    menu_ax.set_xlim(0, 1)
    menu_ax.set_ylim(0, 1)
    menu_ax.set_clip_on(True)
    menu_ax.axis('off')
    menu_texts = []

    n = len(labels)
    for i, lab in enumerate(labels):
        y = 0.9 - i * (0.8 / n)
        txt = menu_ax.text(0.1, y, lab, fontsize=12, picker=True,
                        bbox=dict(boxstyle="round", fc="white", ec="black"))
        txt.set_clip_on(True)
        menu_texts.append(txt)

    global menu_visible
    menu_visible = False

    def slide_menu(show=True):
        start = menu_start_pos[0] if show else menu_end_pos[0]
        end = menu_end_pos[0] if show else menu_start_pos[0]
        steps = 20
        delta = (end - start) / steps
        for i in range(steps):
            new_x = start + delta * (i + 1)
            pos = [new_x, menu_end_pos[1], menu_end_pos[2], menu_end_pos[3]]
            menu_ax.set_position(pos)
            fig.canvas.draw_idle()
            plt.pause(0.01)

    def on_menu_click(event):
        global current_selection, menu_visible
        if menu_visible and event.inaxes != menu_ax:
            slide_menu(show=False)
            menu_visible = False

    def on_menu_pick(event):
        global current_selection, menu_visible
        artist = event.artist
        if artist in menu_texts:
            selected = artist.get_text()
            current_selection = selected
            draw_plots(selected)
            slide_menu(show=False)
            menu_visible = False

    fig.canvas.mpl_connect('pick_event', on_menu_pick)
    fig.canvas.mpl_connect('button_press_event', on_menu_click)

    ax_button = fig.add_axes([0.01, 0.9, 0.1, 0.05])
    menu_button = Button(ax_button, 'Menu')

    def toggle_menu(event):
        global menu_visible
        if not menu_visible:
            slide_menu(show=True)
            menu_visible = True
        else:
            slide_menu(show=False)
            menu_visible = False

    menu_button.on_clicked(toggle_menu)

    plt.show()



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
    Returns a friendly name for the given process name. If no friendly name mapping is
    available, the original process name is returned.

    Args:
        process_name (str): The name of the process to get a friendly name for.

    Returns:
        str: The friendly name for the given process name, or the original process name
        if no friendly name mapping is available.
    """
    return friendly_name_mapping.get(process_name, process_name)

def is_any_game_running(game_names):
    """
    Checks if any of the specified games are currently running.

    Args:
        game_names (list[str]): A list of game names to check.

    Returns:
        str or None: The name of the first game found to be running, or None if no games are running.
    """
    running_processes = [proc.info['name'].lower() for proc in psutil.process_iter(['name'])]
    for game_name in game_names:
        if any(name.lower() in running_processes for name in game_name):
            return game_name[0]
    return None


async def update_status(game_name, elapsed_time, games):
    global start
    global notification_usernames
    global playing_game
    global notification_message_text_global

    if game_name:
        log_game_start(game_name)
    else:
        for game in list(game_stats["daily"].keys()):
            log_game_end(game)

    if game_name is False and elapsed_time is False:
        try:
            await client(UpdateProfileRequest(about=default_bio))
            playing_game = None
        except Exception as e:
            logger.warning(os.getenv("ERROR_UPDATE_DEFAULT_BIO"))
            logger.critical(e) if os.getenv("DEBUG") == "true" else None

        if not start:
            start = True
            text_start = ""
            for item in games:
                game_name2 = item[0]
                friendly_game_name2 = get_friendly_name(game_name2)
                process_name2 = find_process_name(friendly_game_name2)
                if any(process_name2 is not False and key.lower() == process_name2.lower() for key in process_name_mapping):
                    friendly_game_name2 = capitalize_first_letters(process_name_mapping[process_name2][0])
                    text_start += friendly_game_name2.replace("`", "").replace("_", "").replace("*", "") + "\n"

            if len(text_start) > 3800:
                text_start = text_start[:3800] + "..."
            try:
                await client.send_message("me", (os.getenv("START_MESSAGE").replace("#local_version", local_version)) + text_start, parse_mode="Markdown")
                logger.info(os.getenv("DEBUG_START")) if os.getenv("DEBUG") == "true" else None
            except Exception as e:
                await client.log_out()
                messagebox.showerror(os.getenv("ERROR"), os.getenv("CANT_CONNECT"))
                logger.warning(os.getenv("ERROR_START_MESSAGE")) if os.getenv("DEBUG") == "true" else None
                logger.critical(e) if os.getenv("DEBUG") == "true" else None
                return handle_exit(None, None)
    else:
        friendly_game_name = get_friendly_name(game_name)
        friendly_game_name_cap = capitalize_first_letters(process_name_mapping[find_process_name(friendly_game_name)][0])

        if not start:
            start = True
            text_start = ""
            for item in games:
                game_name2 = item[0]
                friendly_game_name2 = get_friendly_name(game_name2)
                process_name2 = find_process_name(friendly_game_name2)
                if any(process_name2 is not False and key.lower() == process_name2.lower() for key in process_name_mapping):
                    friendly_game_name2 = capitalize_first_letters(process_name_mapping[process_name2][0])
                    text_start += friendly_game_name2.replace("`", "").replace("_", "").replace("*", "") + "\n"

            if len(text_start) > 3800:
                text_start = text_start[:3800] + "..."
            try:
                await client.send_message("me", (os.getenv("START_MESSAGE").replace("#local_version", local_version)) + text_start, parse_mode="Markdown")
                logger.info(os.getenv("DEBUG_START")) if os.getenv("DEBUG") == "true" else None
            except Exception as e:
                await client.log_out()
                messagebox.showerror(os.getenv("ERROR"), os.getenv("CANT_CONNECT"))
                logger.warning(os.getenv("ERROR_START_MESSAGE")) if os.getenv("DEBUG") == "true" else None
                logger.critical(e) if os.getenv("DEBUG") == "true" else None
                return handle_exit(None, None)


        action_emoji = ""

        if elapsed_time < 10:
            action_emoji = ACTION_EMOJI_LESS_10_MIN
        elif 9 < elapsed_time < 60:
            action_emoji = ACTION_EMOJI_10_TO_60_MIN
        elif 59 < elapsed_time < 120:
            action_emoji = ACTION_EMOJI_60_TO_120_MIN
        else:
            action_emoji = ACTION_EMOJI_MORE_120_MIN

        new_status = (os.getenv("ACTION_STATUS").replace("#action_emoji", action_emoji).replace("#game_name", friendly_game_name_cap).replace("#elapsed_time", str(elapsed_time + 1))).replace(" (Steam)", "").replace(" (Non-Steam)", "").replace(" (x86)", "").replace(" (steam)", "").replace(" (non-steam)", "").replace(" (Retail)", "").replace(" (retail)", "").replace(" (Release)", "").replace(" (release)", "").replace(" (Dev)", "").replace(" (dev)", "").replace(" (x64)", "").replace(" (dx11)", "").replace(" (dx12)", "")
        try:
            await client(UpdateProfileRequest(about=new_status))
            if playing_game != friendly_game_name_cap:
                if notification_usernames:
                    notification_message_template = notification_message_text_global.get("1.0", tk.END).strip()
                    if not notification_message_template:
                        notification_message_template = os.getenv("NOTIFICATION_MESSAGE")

                    now = datetime.now()
                    current_time_str = now.strftime("%H:%M")


                    for username in notification_usernames:
                        first_name = await get_first_name(username)
                        if first_name != False:
                            notification_message = notification_message_template.replace("#game_name", friendly_game_name_cap).replace("#name", first_name).replace("#time", current_time_str)
                            try:
                                await client.send_message(username, notification_message)
                                logger.info(os.getenv("DEBUG_NOTIFICATION_SENT").replace("#name", first_name).replace("#game_name", friendly_game_name_cap)) if os.getenv("DEBUG") == "true" else None
                            except Exception as e:
                                logger.warning(os.getenv("ERROR_NOTIFICATION_FAILED").replace("#name", first_name).replace("#game_name", friendly_game_name_cap)) if os.getenv("DEBUG") == "true" else None
                                logger.critical(e) if os.getenv("DEBUG") == "true" else None
                        

            playing_game = friendly_game_name_cap
            logger.info(os.getenv("DEBUG_PLAYING") + friendly_game_name_cap + os.getenv("DEBUG_PLAYTIME") + str(elapsed_time + 1)) if os.getenv("DEBUG") == "true" else None
        except Exception as e:
            messagebox.showerror(os.getenv("ERROR"), os.getenv("TOO_LONG"))
            logger.warning(os.getenv("TOO_LONG")) if os.getenv("DEBUG") == "true" else None
            logger.critical(e) if os.getenv("DEBUG") == "true" else None
            root.quit()
            sys.exit()

current_game = None

async def main(games):
    """
    Continuously monitors a list of games and updates the status of the currently running game.
    """
    global current_game

    for proc in psutil.process_iter(['name', 'exe', 'username']):
        if proc.info['name'] == 'python.exe':
            try:
                proc.nice(psutil.IDLE_PRIORITY_CLASS)
                logger.debug(os.getenv("DEBUG_SET_LOW_PRIORITY")) if os.getenv("DEBUG") == "true" else None
                break
            except:
                False

    start_time = None
    check_interval = int(os.getenv("INTERVAL_TIME"))
    while True:
        try:
            await client.connect()
        except:
            pass
        game_name = is_any_game_running(games)
        if game_name:
            if current_game != game_name:
                current_game_before_update = current_game
                current_game = game_name
                start_time = time.time()
            elapsed_time = int((time.time() - start_time) / check_interval)
            await update_status(game_name, elapsed_time, games)

            cpu_usage = get_cpu_usage()
            gpu_usage = get_gpu_usage()

            if game_name in game_stats["daily"]:
                game_stats["daily"][game_name]["avgCPUusage"] = cpu_usage if cpu_usage is not None else 1
                game_stats["daily"][game_name]["avgGPUusage"] = gpu_usage if gpu_usage is not None else 1
                _save_stats_to_file()

        else:
            current_game = None
            await update_status(False, False, games)
            start_time = None
        try:
            await client.disconnect()
        except:
            pass
        await asyncio.sleep(check_interval)


def start_monitoring(games):
    """
    Starts the main event loop and creates a task to run the main application logic.

    Args:
        games (list): A list of game objects to monitor.
    """
    loop = asyncio.get_event_loop()
    loop.create_task(main(games))
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
            messagebox.showerror(os.getenv("ERROR"), os.getenv("ALREADY_ADDED"))
            logger.debug(os.getenv("ALREADY_ADDED") + " - " + process_names) if os.getenv("DEBUG") == "true" else None
            return
        findgame = find_process_name(process_names)
        if findgame == False:
            logger.debug(os.getenv("NOT_IN_DATABASE") + " - " + process_names) if os.getenv("DEBUG") == "true" else None
            return messagebox.showwarning(os.getenv("WARNING"), os.getenv("NOT_IN_DATABASE"))
        added_games.append(process_names)
        games_listbox.insert(tk.END, process_names)
        game_entry.delete(0, tk.END)
        logger.info(os.getenv("DEBUG_GAME_ADDED") + " - " + process_names) if os.getenv("DEBUG") == "true" else None
    else:
        messagebox.showwarning(os.getenv("WARNING"), os.getenv("VALID_GAME_NAME"))
        logger.debug(os.getenv("DEBUG_VALID_NAME") + " - " + friendly_name) if os.getenv("DEBUG") == "true" else None

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
            logger.info(os.getenv("DEBUG_GAME_REMOVED") + " - " + game_to_remove) if os.getenv("DEBUG") == "true" else None
    else:
        messagebox.showwarning(os.getenv("WARNING"), os.getenv("SELECT_GAME_TO_DEL"))
        logger.debug(os.getenv("DEBUG_DELETE_GAME")) if os.getenv("DEBUG") == "true" else None

def start_button_click():
    """
    Starts the game monitoring process when the user clicks the start button.

    This function is called when the user clicks the "Start" button in the GUI. It retrieves the list of games selected in the listbox, checks if the default biography is within the character limit, and then starts the game monitoring process. If no games are selected, it displays a warning message.
    """

    games = [tuple(games_listbox.get(i).split(", ")) for i in range(games_listbox.size())]
    if games:
        global default_bio
        global notification_usernames
        global notification_message_text_global

        default_bio = default_bio_text.get("1.0", tk.END).strip()
        if len(default_bio) > 70:
            messagebox.showerror(os.getenv("ERROR"), os.getenv("DEFAULT_BIO_MAX_LENGTH"))
            logger.error(os.getenv("DEBUG_DEFAULT_BIO_IS_TOO_LONG") + " - " + default_bio) if os.getenv("DEBUG") == "true" else None
            return

        usernames_str = notification_usernames_entry.get()
        if usernames_str != os.getenv("NOTIFICATION_USERNAMES_PLACEHOLDER"):
            notification_usernames = [uname.strip() for uname in usernames_str.replace(',', ' ').split() if uname.strip()]
            notification_message_text_global_str = notification_message_text.get("1.0", tk.END).strip()
            game_stats["notification_usernames"] = notification_usernames

        try:
            game_stats["default_bio"] = default_bio
            game_stats["notification_message"] = notification_message_text_global_str
        except:
            pass
        _save_stats_to_file()


        messagebox.showinfo(os.getenv("STARTED"), os.getenv("STARTED_MESSAGE"))
        logger.info(os.getenv("STARTED_MESSAGE")) if os.getenv("DEBUG") == "true" else None
        root.destroy()
        try:
            root.quit()
        except:
            pass
        logger.info(os.getenv("CONSOLE_START_MESSAGE"))
        start_monitoring(games)
    else:
        logger.warning(os.getenv("DEBUG_EMPTY_GAME_LIST")) if os.getenv("DEBUG") == "true" else None
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
            logger.debug(os.getenv("DEBUG_ALREADY_ADDED") + " - " + process_name) if os.getenv("DEBUG") == "true" else None
            messagebox.showerror(os.getenv("ERROR"), os.getenv("ALREADY_ADDED"))
            return
        else:
            logger.info(os.getenv("DEBUG_GAME_ADDED") + " - " + process_name) if os.getenv("DEBUG") == "true" else None
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
    entry.config(fg='grey', cursor="xterm")
    global theme
    def on_focus_in(event):
        if entry.get() == placeholder:
            entry.delete(0, tk.END)
            if theme == 1:
                entry.config(fg='blue')
            else:
                entry.config(fg='yellow')

    def on_focus_out(event):
        if entry.get() == '':
            entry.insert(0, placeholder)
            entry.config(fg='grey')

    entry.bind("<FocusIn>", on_focus_in)
    entry.bind("<FocusOut>", on_focus_out)

def remove_all_games():
    """
    Removes all games from the games_listbox and the added_games list.
    If there are no games in the list, it shows a toast message.
    """
    if not games_listbox.size():
        show_toast(os.getenv("NO_GAMES_TO_REMOVE"))
        logger.debug(os.getenv("DEBUG_NO_GAMES_TO_REMOVE")) if os.getenv("DEBUG") == "true" else None
    else:
        games_listbox.delete(0, tk.END)
        added_games.clear()
        show_toast(os.getenv("DEBUG_ALL_GAMES_REMOVED"))
        logger.info(os.getenv("DEBUG_ALL_GAMES_REMOVED")) if os.getenv("DEBUG") == "true" else None

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
        logger.debug(os.getenv("DEBUG_SEARCH_QUERY") + " - " + search_term) if (os.getenv("DEBUG") == "true" and search_term is not None) else None
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
                logger.debug(os.getenv("DEBUG_ALREADY_ADDED") + " - " + selected_game) if os.getenv("DEBUG") == "true" else None
                messagebox.showerror(os.getenv("ERROR"), os.getenv("ALREADY_ADDED"))
                return
            else:
                logger.info(os.getenv("DEBUG_GAME_ADDED") + " - " + selected_game) if os.getenv("DEBUG") == "true" else None
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
        logger.debug(os.getenv("DEBUG_ALL_GAMES") + " - " + str(len(sorted_keys))) if os.getenv("DEBUG") == "true" else None
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
    logger.info(os.getenv("DEBUG_ALL_GAMES_MENU") + " - " + str(len(process_name_mapping))) if os.getenv("DEBUG") == "true" else None
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
                logger.debug(os.getenv("DEBUG_ALREADY_ADDED") + " - " + selected_game) if os.getenv("DEBUG") == "true" else None
                messagebox.showerror(os.getenv("ERROR"), os.getenv("ALREADY_ADDED"))
                return
            else:
                logger.info(os.getenv("DEBUG_GAME_ADDED") + " - " + selected_game) if os.getenv("DEBUG") == "true" else None
                added_games.append(selected_game)
                games_listbox.insert(tk.END, selected_game)
                listbox.selection_clear(0, tk.END)
                filter_list(None)

    listbox.bind("<Return>", add_to_list)
    listbox.bind("<Double-1>", add_on_double_click)
    add_button = tk.Button(list_frame, text=os.getenv("ADD"), command=add_to_list, cursor="hand2")
    add_button.grid(row=3, column=0, padx=10, pady=10)

    add_all_button = tk.Button(list_frame, text=os.getenv("ADD_ALL"), command=add_all_games, font=(poppins_font, 12), cursor="hand2")
    add_all_button.grid(row=3, column=2, padx=10, pady=10)

    close_button = tk.Button(list_frame, text=os.getenv("CLOSE"), command=list_window.destroy, cursor="hand2")
    close_button.grid(row=3, column=1, padx=10, pady=10)

    list_window.resizable(False, False)


theme = 0
def change_theme():
    """
    Changes the theme of the application between light and dark mode.
    """
    global theme
    if theme == 0:
        theme = 1
        remove_button.configure(fg="maroon")
        remove_all_button.configure(fg="violet red")
        start_button.configure(fg="SteelBlue1")
        sv_ttk.set_theme("light")
        logger.debug(os.getenv("DEBUG_CHANGE_THEMA_LIGHT_MODE")) if os.getenv("DEBUG") == "true" else None
        show_toast(os.getenv("CHANGE_THEMA_LIGHT_MODE"))
    else:
        theme = 0
        remove_button.configure(fg="hot pink")
        remove_all_button.configure(fg="red")
        start_button.configure(fg="DeepSkyBlue2")
        sv_ttk.set_theme("dark")
        logger.debug(os.getenv("DEBUG_CHANGE_THEMA_DARK_MODE")) if os.getenv("DEBUG") == "true" else None
        show_toast(os.getenv("CHANGE_THEMA_DARK_MODE"))

    toggle_debug_mode(True)
    toggle_hint_mode(True)

    game_stats["theme"] = theme
    _save_stats_to_file()


toast_window = None

def show_toast(message, duration=5000, after=2000):
    """
    Displays a toast notification on the screen for a specified duration.

    Args:
        message (str): The message to display in the toast notification.
        duration (int, optional): The duration of the toast notification in milliseconds. Defaults to 5000 (5 seconds).
    """
    global toast_window

    if toast_window is not None:
        try:
            toast_window.destroy()
        except:
            pass

    toast_window = tk.Toplevel(root)
    toast_window.overrideredirect(True)
    toast_window.geometry("+500+400")

    bg_color = "white"
    fg_color = "black"
    if (theme == 1):
        bg_color = "black"
        fg_color = "white"
    toast_label = tk.Label(toast_window, text=message, bg=bg_color, fg=fg_color, padx=20, pady=10)
    toast_label.pack()

    def start_fade(window, remaining_time):
        if remaining_time > 0:
            alpha = remaining_time / duration
            window.attributes("-alpha", alpha)
            window.after(50, start_fade, window, remaining_time - 50)
        else:
            window.destroy()


    try:
        toast_window.after(after, start_fade, toast_window, duration - 4800)
    except:
        pass

current_os = is_supported_os()
"""
Checks if the current operating system is not Windows or Linux, and if so, logs a critical message and exits the application.
"""
if current_os != 'windows' and current_os != 'linux':
    logger.critical(os.getenv("UNSUPPORTED_OS"))
    handle_exit(None, None)

if current_os == "windows":
    mapping_file_path = os.getenv("GAME_DATA_JSON_WINDOWS")
elif current_os == "linux":
    mapping_file_path = os.getenv("GAME_DATA_JSON_LINUX")

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

sv_ttk.set_theme("dark")

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

game_entry = tk.Entry(frame, width=30, font=(poppins_font, 12), cursor="xterm")
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

default_bio_text = tk.Text(frame, width=50, height=4, font=(poppins_font, 12), cursor="xterm")
default_bio_text.insert(tk.END, default_bio)
default_bio_text.grid(row=3, column=1, columnspan=3, padx=5, pady=5)

chthema = tk.Button(frame, text=os.getenv("CHANGE_THEMA_LABEL"), command=change_theme, font=(poppins_font, 12), cursor="hand2")
chthema.grid(row=4, column=0, columnspan=1, padx=0, pady=5)

stats_button = tk.Button(frame, text=os.getenv("STATS"), command=show_stats, font=(poppins_font, 12), cursor="hand2")
stats_button.grid(row=5, column=0, columnspan=1, padx=0, pady=5)

debug_mode_var = tk.BooleanVar()
hint_mode_var = tk.BooleanVar()

debug_mode_button = tk.Checkbutton(frame, text=os.getenv("DEBUG_MODE_LABEL"), variable=debug_mode_var, command=lambda: toggle_debug_mode(False), font=(poppins_font, 12), cursor="hand2")
debug_mode_button.grid(row=4, column=2, columnspan=2, padx=5, pady=5)


hint_mode_button = tk.Checkbutton(frame, text=os.getenv("SHOW_HINTS"), variable=hint_mode_var, command=lambda: toggle_hint_mode(False), font=(poppins_font, 12), cursor="hand2")
hint_mode_button.grid(row=5, column=2, columnspan=2, padx=5, pady=5)

notification_usernames_label = tk.Label(frame, text=os.getenv("NOTIFICATION_USERNAMES_LABEL"), font=(poppins_font, 12))
notification_usernames_label.grid(row=6, column=0, sticky="w", padx=5, pady=5)

notification_usernames_entry = tk.Entry(frame, width=50, font=(poppins_font, 12), cursor="xterm")
notification_usernames_entry.grid(row=6, column=1, columnspan=3, padx=5, pady=5)
if notification_usernames:
    notification_usernames_entry.insert(0, ", ".join(notification_usernames)) 
    notification_usernames_entry.xview_moveto(1)
else:
    add_placeholder(notification_usernames_entry, os.getenv("NOTIFICATION_USERNAMES_PLACEHOLDER"))

notification_message_label = tk.Label(frame, text=os.getenv("NOTIFICATION_MESSAGE_LABEL_CUSTOM"), font=(poppins_font, 12))
notification_message_label.grid(row=7, column=0, sticky="nw", padx=5, pady=5)

notification_message_text = tk.Text(frame, width=50, height=3, font=(poppins_font, 12), cursor="xterm")
notification_message_text.insert(tk.END, notification_message_text_global_str)
notification_message_text.grid(row=7, column=1, columnspan=3, padx=5, pady=5)
notification_message_text_global = notification_message_text

notification_variables_label = tk.Label(frame, text=os.getenv("NOTIFICATION_VARIABLES_LABEL"), font=(poppins_font, 10), justify=tk.LEFT)
notification_variables_label.grid(row=8, column=1, columnspan=3, sticky="nw", padx=5, pady=0)


if theme == 0:
    remove_button.configure(fg="maroon")
    remove_all_button.configure(fg="violet red")
    start_button.configure(fg="SteelBlue1")
    debug_mode_button.configure(selectcolor="black")
    hint_mode_button.configure(selectcolor="black")
else:
    remove_button.configure(fg="hot pink")
    remove_all_button.configure(fg="red")
    start_button.configure(fg="DeepSkyBlue2")
    debug_mode_button.configure(selectcolor="white")
    hint_mode_button.configure(selectcolor="white")

if os.getenv("DEBUG") == "true":
    debug_mode_var.set(True)

if os.getenv("HINTS") == "true":
    hint_mode_var.set(True)

if "theme" in game_stats:
    if game_stats["theme"] == 1:
        change_theme()


# HINTS
def on_enter(hint_message=None):
    if os.getenv("HINTS") == "true":
        if hint_message == "default_bio_text":
            show_toast(os.getenv("DEFAULT_BIO_HINT"), duration=20000)
        if hint_message == "debug_mode_button":
            show_toast(os.getenv("DEBUG_MODE_HINT"), duration=20000)
        if hint_message == "remove_button":
            show_toast(os.getenv("REMOVE_HINT"), duration=20000)
        if hint_message == "remove_all_button":
            show_toast(os.getenv("REMOVE_ALL_HINT"), duration=20000)
        if hint_message == "start_button":
            show_toast(os.getenv("START_HINT"), duration=20000)
        if hint_message == "chthema":
            show_toast(os.getenv("CHANGE_THEMA_HINT"), duration=20000)
        if hint_message == "list_button":
            show_toast(os.getenv("GAME_LIST_HINT"), duration=20000)
        if hint_message == "notification_usernames_entry":
            show_toast(os.getenv("NOTIFICATION_USERNAMES_HINT"), duration=20000)
        if hint_message == "notification_message_text":
            show_toast(os.getenv("NOTIFICATION_MESSAGE_CUSTOM_HINT"), duration=20000)

def on_leave(event):
    global toast_window
    if toast_window is not None:
        try:
            toast_window.destroy()
        except:
            pass
    toast_window = None

default_bio_text.bind("<Enter>", lambda event: on_enter(hint_message="default_bio_text"))
default_bio_text.bind("<Leave>", on_leave)
debug_mode_button.bind("<Enter>", lambda event: on_enter(hint_message="debug_mode_button"))
debug_mode_button.bind("<Leave>", on_leave)
remove_button.bind("<Enter>", lambda event: on_enter(hint_message="remove_button"))
remove_button.bind("<Leave>", on_leave)
remove_all_button.bind("<Enter>", lambda event: on_enter(hint_message="remove_all_button"))
remove_all_button.bind("<Leave>", on_leave)
start_button.bind("<Enter>", lambda event: on_enter(hint_message="start_button"))
start_button.bind("<Leave>", on_leave)
chthema.bind("<Enter>", lambda event: on_enter(hint_message="chthema"))
chthema.bind("<Leave>", on_leave)
list_button.bind("<Enter>", lambda event: on_enter(hint_message="list_button"))
list_button.bind("<Leave>", on_leave)
notification_usernames_entry.bind("<Enter>", lambda event: on_enter(hint_message="notification_usernames_entry"))
notification_usernames_entry.bind("<Leave>", on_leave)
notification_message_text.bind("<Enter>", lambda event: on_enter(hint_message="notification_message_text"))
notification_message_text.bind("<Leave>", on_leave)


emoji_font = tkfont.Font(family="Segoe UI Emoji", size=12)
emoji_font2 = tkfont.Font(family="Noto Color Emoji", size=12)
default_bio_text.configure(font=emoji_font)
default_bio_text.configure(font=emoji_font2)

latest_version = get_latest_version()

"""
Displays a warning message to the user if a newer version of the application is available.

The message includes the latest version number and the current version number, and is displayed using the Tkinter messagebox.showwarning() function.
"""
if latest_version["version"] != "" and local_version and str(latest_version["version"]) != str(local_version):
    messagebox.showwarning(os.getenv("UPDATE_AVAILABLE"), os.getenv("UPDATE_AVAILABLE_MESSAGE").replace("#latest_version", latest_version["version"]).replace("#current_version", local_version).replace("#update_message", latest_version["message"]))

root.mainloop()