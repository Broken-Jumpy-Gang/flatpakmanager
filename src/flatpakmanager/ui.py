import curses
import time
import signal
from .commands import get_installed_flatpaks, get_running_flatpaks, run_flatpak, stop_flatpak, get_flatpak_description
from .utils import confirm_action
from .installer import install_package_mode
from .uninstaller import uninstall_package_mode

# A flag to indicate whether an exit has been requested.
exit_requested = False

def signal_handler(sig, frame):
    """
    Signal handler to set the exit flag when SIGINT is received.
    """
    global exit_requested
    exit_requested = True

def display_help_page(stdscr) -> None:
    """
    Display an interactive help screen.
    
    :param stdscr: The curses window.
    """
    stdscr.timeout(-1)
    stdscr.clear()
    help_lines = [
        "Flatpak Manager Help",
        "---------------------",
        "",
        "Navigation:",
        "  Up/Down arrows    : Navigate the list.",
        "  Left/Right arrows : Switch between Installed and Running apps.",
        "  Enter             : Launch an app (or stop it if running).",
        "  Ctrl+I            : Enter package installation mode.",
        "  Ctrl+U            : Enter package uninstallation mode.",
        "  Ctrl+H            : Display this help page.",
        "  ESC               : Exit the application.",
        "",
        "Installation Mode:",
        "  - Type a search term to find packages.",
        "  - Use arrow keys to select a package.",
        "  - Press Enter to install the selected package.",
        "  - Press ESC to cancel installation mode.",
        "",
        "Uninstallation Mode:",
        "  - Type a search term to filter installed packages.",
        "  - Use arrow keys to select a package.",
        "  - Press Enter to confirm uninstallation.",
        "",
        "Press any key to return..."
    ]
    for idx, line in enumerate(help_lines):
        try:
            stdscr.addstr(idx, 0, line)
        except curses.error:
            pass
    stdscr.refresh()
    stdscr.getch()
    stdscr.timeout(200)

def main_loop(stdscr) -> None:
    """
    Main event loop for the Flatpak Manager interface.
    """
    global exit_requested
    signal.signal(signal.SIGINT, signal_handler)
    curses.curs_set(0)
    stdscr.timeout(200)  # Poll every 200 ms for input

    selected_index = 0
    selected_running_index = 0
    is_left_panel = True
    search_term = ""
    
    last_refresh_time = 0
    refresh_interval = 2  # seconds
    installed_apps = []
    running_apps = {}

    while True:
        current_time = time.time()
        if current_time - last_refresh_time > refresh_interval:
            installed_apps = get_installed_flatpaks()
            running_apps = get_running_flatpaks()
            last_refresh_time = current_time

        stdscr.clear()
        stdscr.addstr(0, 0, "Flatpak Manager", curses.A_BOLD)
        stdscr.addstr(1, 0, "Search: " + search_term)
        
        # Display installed apps.
        stdscr.addstr(3, 0, "Installed Apps:", curses.A_UNDERLINE)
        filtered_apps = [app for app in installed_apps if search_term.lower() in app[1].lower()]
        
        # Clamp selected_index to valid range.
        if filtered_apps:
            if selected_index >= len(filtered_apps):
                selected_index = len(filtered_apps) - 1
        else:
            selected_index = 0
        
        for idx, (app_id, name) in enumerate(filtered_apps):
            if idx == selected_index and is_left_panel:
                stdscr.addstr(4 + idx, 0, name, curses.A_REVERSE)
            else:
                stdscr.addstr(4 + idx, 0, name)
        
        # Display running apps.
        stdscr.addstr(3, 40, "Running Apps:", curses.A_UNDERLINE)
        running_app_ids = list(running_apps.keys())
        for idx, app_id in enumerate(running_app_ids):
            if idx == selected_running_index and not is_left_panel:
                stdscr.addstr(4 + idx, 40, app_id, curses.A_REVERSE)
            else:
                stdscr.addstr(4 + idx, 40, app_id)
        
        # Show description for the selected installed app.
        if is_left_panel and filtered_apps:
            app_id = filtered_apps[selected_index][0]
            description = get_flatpak_description(app_id)
            stdscr.addstr(2, 40, description[:80])
        
        stdscr.refresh()
        key = stdscr.getch()
        if key != -1:
            if key == curses.KEY_UP:
                if is_left_panel and selected_index > 0:
                    selected_index -= 1
                elif not is_left_panel and selected_running_index > 0:
                    selected_running_index -= 1
            elif key == curses.KEY_DOWN:
                if is_left_panel and selected_index < len(filtered_apps) - 1:
                    selected_index += 1
                elif not is_left_panel and selected_running_index < len(running_app_ids) - 1:
                    selected_running_index += 1
            elif key == curses.KEY_LEFT:
                is_left_panel = True
            elif key == curses.KEY_RIGHT:
                is_left_panel = False
            elif key in (10, 13):
                if is_left_panel and filtered_apps:
                    app_id, app_name = filtered_apps[selected_index]
                    if app_id in running_apps:
                        if confirm_action(stdscr, f"Do you really want to stop '{app_name}'?"):
                            stop_flatpak(running_apps[app_id])
                    else:
                        run_flatpak(app_id)
                elif not is_left_panel and running_app_ids:
                    app_id = running_app_ids[selected_running_index]
                    if confirm_action(stdscr, f"Do you really want to stop '{app_id}'?"):
                        stop_flatpak(running_apps[app_id])
            elif key == 27:  # ESC key pressed, request exit.
                exit_requested = True
            elif key == 9:  # Ctrl+I for installation mode.
                install_package_mode(stdscr)
            elif key == 21:  # Ctrl+U for uninstallation mode.
                uninstall_package_mode(stdscr)
            elif key in (curses.KEY_BACKSPACE, 127):
                if search_term:
                    search_term = search_term[:-1]
            elif key == 8:
                if search_term:
                    search_term = search_term[:-1]
                else:
                    display_help_page(stdscr)
            elif 32 <= key <= 126:
                search_term += chr(key)
        
        # Check for exit request.
        if exit_requested:
            stdscr.clear()
            stdscr.addstr(0, 0, "Do you want to stop all running Flatpak apps before exit? (y/N/c)")
            stdscr.refresh()
            while True:
                response = stdscr.getch()
                if response in (ord('y'), ord('n'), ord('c'), 10, 13):
                    if response in (10, 13):
                        response = ord('n')
                    break
            if response == ord('y'):
                running_apps = get_running_flatpaks()
                for instance in running_apps.values():
                    stop_flatpak(instance)
                break
            elif response == ord('n'):
                break
            elif response == ord('c'):
                exit_requested = False
                continue

    stdscr.clear()
    stdscr.refresh()

