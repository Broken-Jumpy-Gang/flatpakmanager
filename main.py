#!/usr/bin/env python3
import sys
import argparse
import curses
from ui import main_loop

man_page_text = """
FLATPAK MANAGER(1)                             User Commands                            FLATPAK MANAGER(1)

NAME
       flatpak-manager - curses based Flatpak management tool

SYNOPSIS
       flatpak-manager [--manpage]

DESCRIPTION
       flatpak-manager is an interactive terminal application for managing Flatpak applications.
       It provides an interface to list, run, stop, install and uninstall Flatpak apps.

KEY BINDINGS
       Up/Down Arrows     : Navigate the list.
       Left/Right Arrows  : Switch between Installed and Running apps.
       Enter              : Launch an app (or stop it if already running).
       Ctrl+I             : Enter package installation mode.
       Ctrl+U             : Enter package uninstallation mode.
       Ctrl+H             : Display this help page.
       ESC                : Exit the application.

PACKAGE INSTALLATION MODE
       In this mode, users can search for and install new Flatpak packages.
       Type the search term, use the arrow keys to select a package,
       and press Enter to confirm installation.

PACKAGE UNINSTALLATION MODE
       In this mode, users can search for and uninstall installed Flatpak packages.
       Type the search term, use the arrow keys to select a package,
       and press Enter to confirm uninstallation.

AUTHOR
       Written by your team.

REPORTING BUGS
       Report bugs to <your-support@example.com>.
"""

def main_cli():
    parser = argparse.ArgumentParser(
        description="Flatpak Manager - a curses based Flatpak management tool."
    )
    parser.add_argument('--manpage', action='store_true', help="Display the man page/help page and exit")
    args = parser.parse_args()
    if args.manpage:
        print(man_page_text)
        sys.exit(0)
    curses.wrapper(main_loop)

if __name__ == "__main__":
    main_cli()
