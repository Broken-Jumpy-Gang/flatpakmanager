import curses
import time
import pexpect
from .utils import strip_ansi_codes, confirm_action
from .commands import search_flatpak_packages

def run_install_command(stdscr, app_id: str, package_name: str) -> None:
    """
    Run the 'flatpak install' command interactively, displaying the output in the curses interface.
    
    :param stdscr: The curses window.
    :param app_id: The package ID.
    :param package_name: The package name.
    """
    command = f"flatpak install flathub {app_id}"
    child = pexpect.spawn(command, encoding='utf-8', echo=False)
    child.delaybeforesend = 0.1

    output_lines = []
    max_y, max_x = stdscr.getmaxyx()
    list_start_line = 3
    available_rows = max_y - list_start_line

    stdscr.nodelay(True)  # Enable non-blocking input.

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
        stdscr.addstr(0, 0, f"Installing {package_name} ({app_id})")
        stdscr.addstr(1, 0, "Installation output (type responses if prompted, 'q' to quit after finish)")
        
        # Clean and display output.
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
    stdscr.addstr(0, 0, f"Installation of {package_name} ({app_id}) completed.")
    stdscr.addstr(1, 0, "Full installation output below. Press 'q' to return.")
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

def install_package_mode(stdscr) -> None:
    """
    Enter the interactive installation mode.
    Users can search for packages, view package details, and confirm installation.
    
    :param stdscr: The curses window.
    """
    curses.curs_set(1)
    search_term = ""
    selected_index = 0
    scroll_offset = 0
    results = []
    last_search_term = ""
    last_results = []
    debounce_delay = 0.5  # Delay (in seconds) for debouncing keystrokes.
    last_input_time = time.time()
    
    stdscr.nodelay(True)
    
    while True:
        stdscr.clear()
        header = "Install Package - Enter name (ESC to cancel): " + search_term
        stdscr.addstr(0, 0, header)
        
        list_start_line = 2
        max_y, max_x = stdscr.getmaxyx()
        available_rows = max_y - list_start_line
        
        # Update search results after a debounce delay.
        current_time = time.time()
        if search_term and (current_time - last_input_time >= debounce_delay) and (search_term != last_search_term):
            last_results = search_flatpak_packages(search_term)
            last_results = sorted(
                last_results,
                key=lambda pkg: (
                    pkg[1].lower().find(search_term.lower()) if search_term.lower() in pkg[1].lower() else 999,
                    pkg[1].lower()
                )
            )
            last_search_term = search_term
            selected_index = 0
            scroll_offset = 0
        
        if search_term:
            results = last_results
        else:
            results = []
            selected_index = 0
            scroll_offset = 0
        
        results = results[:150]
        
        if selected_index < scroll_offset:
            scroll_offset = selected_index
        elif selected_index >= scroll_offset + available_rows:
            scroll_offset = selected_index - available_rows + 1
        
        visible_results = results[scroll_offset:scroll_offset + available_rows]
        for idx, (app_id, name, _) in enumerate(visible_results):
            display_str = f"{name} ({app_id})"
            display_str = display_str[:max_x // 2 - 1]
            if scroll_offset + idx == selected_index:
                stdscr.addstr(list_start_line + idx, 0, display_str, curses.A_REVERSE)
            else:
                stdscr.addstr(list_start_line + idx, 0, display_str)
        
        # Show package details in the right panel.
        detail_col = max_x // 2
        if results and selected_index < len(results):
            sel_app_id, sel_name, _ = results[selected_index]
            details = [
                "Package Details:",
                f"Name: {sel_name}",
                f"Package Code: {sel_app_id}"
            ]
            for j, line in enumerate(details):
                truncated_line = line[:max_x - detail_col - 1]
                if list_start_line + j < max_y:
                    stdscr.addstr(list_start_line + j, detail_col, truncated_line)
        
        stdscr.refresh()
        key = stdscr.getch()
        
        if key == -1:
            time.sleep(0.05)
            continue
        
        if key in (10, 13):  # Enter key
            if results:
                selected_app = results[selected_index]
                confirm_msg = f"Install package {selected_app[1]} ({selected_app[0]})?"
                if confirm_action(stdscr, confirm_msg):
                    run_install_command(stdscr, selected_app[0], selected_app[1])
                    break
        elif key == 27:  # ESC key cancels installation mode.
            break
        elif key == curses.KEY_UP:
            if selected_index > 0:
                selected_index -= 1
        elif key == curses.KEY_DOWN:
            if selected_index < len(results) - 1:
                selected_index += 1
        elif key in (curses.KEY_BACKSPACE, 127, 8):
            if search_term:
                search_term = search_term[:-1]
                selected_index = 0
                scroll_offset = 0
                last_search_term = ""
                last_input_time = time.time()
        elif 32 <= key <= 126:
            search_term += chr(key)
            selected_index = 0
            scroll_offset = 0
            last_input_time = time.time()
    
    stdscr.nodelay(False)
    curses.curs_set(0)
