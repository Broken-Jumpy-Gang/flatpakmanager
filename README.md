# Flatpak Manager

**Flatpak Manager** is a curses-based terminal application designed to provide an interactive interface for managing Flatpak applications on your system. It allows you to list installed and running Flatpak applications, as well as install and uninstall packages through a user-friendly command line interface.

## Features

- **Interactive Terminal Interface**: Navigate through installed and running applications using intuitive keyboard shortcuts.
- **Installation Mode**: Search for and install new Flatpak packages interactively.
- **Uninstallation Mode**: Search for and uninstall installed Flatpak packages interactively.
- **Real-Time Updates**: The interface periodically refreshes to show up-to-date information on your Flatpak applications.
- **Built-in Help**: Access an in-application help screen that details key bindings and usage instructions.

## Requirements

- **Operating System**: Linux or any Unix-like system that supports Flatpak and curses.
- **Python 3**: The application is developed in Python 3.
- **Dependencies**:
  - [pexpect](https://pypi.org/project/pexpect/)

## Installation

### Using the Pre-Built Debian Package

1. **Download the Release**:  
   Navigate to the [GitHub Releases page](https://github.com/<yourusername>/flatpak-manager/releases) and download the latest `.deb` file (e.g. `flatpak-manager_0.1.0-1_all.deb`).

2. **Install the Package**:  
   Open your terminal, navigate to the directory where you downloaded the file, and run:
   ```bash
   sudo dpkg -i flatpak-manager_0.1.0-1_all.deb
   ```
   If you encounter any dependency issues, run:
   ```bash
   sudo apt-get install -f
   ```

3. **Run the Application**:  
   Once installed, you can launch the application by simply running:
   ```bash
   flatpak-manager
   ```
   or by calling:
   ```bash
   python3 /usr/bin/flatpak-manager
   ```
   depending on how your environment is set up.

### Installing from Source

1. **Clone the Repository**:  
   Open your terminal and run:
   ```bash
   git clone https://github.com/<yourusername>/flatpak-manager.git
   cd flatpak-manager
   ```

2. **Create a Virtual Environment** (optional but recommended):  
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies**:  
   If you have a `requirements.txt` file, run:
   ```bash
   pip install -r requirements.txt
   ```
   Otherwise, install `pexpect` manually:
   ```bash
   pip install pexpect
   ```

4. **Run the Application**:  
   Launch the application by executing:
   ```bash
   ./main.py
   ```
   or:
   ```bash
   python3 main.py
   ```

## Command Line Options

- `--manpage`: Display the man page (help documentation) and exit.
  ```bash
  ./main.py --manpage
  ```

## Key Bindings

Within the application, the following key bindings are available:

- **Navigation**:
  - **Up/Down Arrows**: Move through the list of applications.
  - **Left/Right Arrows**: Switch between the list of installed and running applications.
  - **Enter**: Launch an application, or stop a running application.

- **Installation Mode**:
  - **Ctrl+I**: Enter installation mode.
  - **Typing**: Enter a search term to filter available packages.
  - **Enter**: Confirm the installation of the selected package.
  - **ESC**: Cancel installation mode.

- **Uninstallation Mode**:
  - **Ctrl+U**: Enter uninstallation mode.
  - **Typing**: Enter a search term to filter installed packages.
  - **Enter**: Confirm the uninstallation of the selected package.
  - **ESC**: Cancel uninstallation mode.

- **Help**:
  - **Ctrl+H**: Display the in-application help screen with key bindings and instructions.

- **Exit**:
  - **ESC**: Initiate the exit process. You will be prompted to stop all running Flatpak applications before exiting.

## Project Structure

The project comprises the following main files:

- **main.py**: Entry point of the application. Handles command line arguments and initialises the curses interface.
- **ui.py**: Contains the main user interface logic and key bindings.
- **commands.py**: Provides functions for interacting with Flatpak (listing, running, stopping, searching, etc.).
- **installer.py**: Implements the interactive installation mode for adding new Flatpak packages.
- **uninstaller.py**: Implements the interactive uninstallation mode for removing installed Flatpak packages.
- **utils.py**: Contains helper functions, such as stripping ANSI escape sequences and displaying confirmation prompts.

## Contributing

Contributions are welcome! If you have suggestions, bug reports, or feature requests, please open an issue or submit a pull request on GitHub.

### How to Contribute

1. **Fork the Repository** on GitHub.
2. **Create a New Branch** for your feature or bug fix:
   ```bash
   git checkout -b my-feature-branch
   ```
3. **Commit Your Changes** with a descriptive commit message:
   ```bash
   git commit -m "Describe your changes here"
   ```
4. **Push Your Branch** to your fork:
   ```bash
   git push origin my-feature-branch
   ```
5. **Open a Pull Request** on the main repository.

## Licence

This project is licensed under the [MIT Licence](LICENSE). See the `LICENSE` file for further details.

## Acknowledgements

- Many thanks to the developers behind Flatpak and the Python community for the tools and libraries that made this project possible.
- Special acknowledgement to [pexpect](https://pypi.org/project/pexpect/) for providing robust interactive process handling.

---

Happy managing your Flatpak applications!