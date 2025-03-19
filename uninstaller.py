import curses
import pexpect
from utils import strip_ansi_codes, confirm_action
from commands import get_installed_flatpaks

def run_uninstall_command(stdscr, app_id: str, package_name: str) -> None:
    """
    Run the 'flatpak uninstall' command interactively, displaying its output.
    
    :param stdscr: The curses window.
    :param app_id: The package ID.
    :param package_name: The package name.
    """
    command = f"flatpak uninstall {app_id}"
    child = pexpect.spawn(command, encoding='utf-8', echo=False)
    child.delaybeforesend = 0.1

    output_lines = []
    max_y, max_x = stdscr.getmaxyx()
    list_start_line = 3
    available_rows = max_y - list_start_line

    stdscr.nodelay(True)
    
    while True:
        try:
            new_output = child.read_nonblocking(size=1024, timeout=0.1)
            if new_output:
                output_lines.append(new_output)
        except pexpect.TIMEOUT:
            pass
        except pexpect.EOF:
            remaining = child.before or ""
            output_lines.append(remaining)
            break

        stdscr.clear()
        stdscr.addstr(0, 0, f"Uninstalling {package_name} ({app_id})")
        stdscr.addstr(1, 0, "Uninstallation output (type responses if prompted, 'q' to quit after finish)")
        
        all_output = "".join(output_lines)
        clean_output = strip_ansi_codes(all_output)
        lines = clean_output.splitlines()
        display_lines = lines[-available_rows:]
        for idx, line in enumerate(display_lines):
            try:
                stdscr.addstr(list_start_line + idx, 0, line[:max_x - 1])
            except curses.error:
                pass
        stdscr.refresh()

        try:
            key = stdscr.getch()
            if key != -1:
                if key == ord('q') and child.eof():
                    break
                if key in (10, 13):
                    child.sendline("")
                else:
                    child.send(chr(key))
        except Exception:
            pass

    stdscr.nodelay(False)
    stdscr.clear()
    stdscr.addstr(0, 0, f"Uninstallation of {package_name} ({app_id}) completed.")
    stdscr.addstr(1, 0, "Full uninstallation output below. Press 'q' to return.")
    all_output = "".join(output_lines)
    clean_output = strip_ansi_codes(all_output)
    lines = clean_output.splitlines()
    display_lines = lines[-(max_y - 3):]
    for idx, line in enumerate(display_lines):
        try:
            stdscr.addstr(3 + idx, 0, line[:max_x - 1])
        except curses.error:
            pass
    stdscr.refresh()
    while stdscr.getch() != ord('q'):
        pass

def uninstall_package_mode(stdscr) -> None:
    """
    Enter the interactive uninstallation mode.
    Allows users to search through installed packages and confirm removal.
    
    :param stdscr: The curses window.
    """
    curses.curs_set(1)
    search_term = ""
    selected_index = 0
    scroll_offset = 0
    
    while True:
        stdscr.clear()
        header = "Uninstall Package - Enter search term (ESC to cancel): " + search_term
        stdscr.addstr(0, 0, header)
        
        list_start_line = 2
        max_y, max_x = stdscr.getmaxyx()
        available_rows = max_y - list_start_line
        
        installed_apps = get_installed_flatpaks()
        filtered_apps = [app for app in installed_apps if search_term.lower() in app[1].lower()] if search_term else installed_apps

        if selected_index < 0:
            selected_index = 0
        if filtered_apps:
            if selected_index >= len(filtered_apps):
                selected_index = len(filtered_apps) - 1
        
        if selected_index < scroll_offset:
            scroll_offset = selected_index
        elif selected_index >= scroll_offset + available_rows:
            scroll_offset = selected_index - available_rows + 1

        visible_apps = filtered_apps[scroll_offset:scroll_offset + available_rows]
        for idx, (app_id, name) in enumerate(visible_apps):
            if scroll_offset + idx == selected_index:
                stdscr.addstr(list_start_line + idx, 0, name, curses.A_REVERSE)
            else:
                stdscr.addstr(list_start_line + idx, 0, name)
        
        stdscr.refresh()
        key = stdscr.getch()
        if key in (10, 13):  # Enter key
            if filtered_apps:
                selected_app = filtered_apps[selected_index]
                confirm_msg = f"Uninstall package {selected_app[1]} ({selected_app[0]})? Press Enter to confirm, any other key to cancel."
                if confirm_action(stdscr, confirm_msg):
                    run_uninstall_command(stdscr, selected_app[0], selected_app[1])
                    break
        elif key == 27:  # ESC cancels uninstallation mode.
            break
        elif key == curses.KEY_UP:
            if selected_index > 0:
                selected_index -= 1
        elif key == curses.KEY_DOWN:
            if selected_index < len(filtered_apps) - 1:
                selected_index += 1
        elif key in (curses.KEY_BACKSPACE, 127, 8):
            if search_term:
                search_term = search_term[:-1]
                selected_index = 0
                scroll_offset = 0
        elif 32 <= key <= 126:
            search_term += chr(key)
            selected_index = 0
            scroll_offset = 0

    curses.curs_set(0)
