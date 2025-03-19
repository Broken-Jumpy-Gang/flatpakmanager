import re

# Compile a regular expression for matching ANSI escape sequences.
ANSI_ESCAPE = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')

def strip_ansi_codes(text: str) -> str:
    """
    Remove ANSI escape sequences from the provided text.
    
    :param text: The text possibly containing ANSI codes.
    :return: Cleaned text without ANSI codes.
    """
    return ANSI_ESCAPE.sub('', text)

def confirm_action(stdscr, message: str) -> bool:
    """
    Display a confirmation prompt using the curses screen and wait for the user to press Enter.
    
    :param stdscr: The curses window.
    :param message: The confirmation message to display.
    :return: True if the user confirms (by pressing Enter), False otherwise.
    """
    stdscr.timeout(-1)
    stdscr.clear()
    stdscr.addstr(0, 0, message)
    stdscr.addstr(1, 0, "Press Enter to confirm, any other key to cancel.")
    stdscr.refresh()
    key = stdscr.getch()
    result = key in (10, 13)  # Enter key codes.
    stdscr.timeout(200)
    return result
