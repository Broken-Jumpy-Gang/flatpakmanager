import subprocess
import os

def get_installed_flatpaks() -> list:
    """
    Retrieve a list of installed Flatpak applications.
    
    :return: A list of tuples (app_id, name).
    """
    try:
        result = subprocess.run(
            ["flatpak", "list", "--app", "--columns=application,name"],
            capture_output=True, text=True, check=True
        )
        apps = []
        for line in result.stdout.strip().splitlines():
            if line:
                parts = line.split("\t")
                if len(parts) == 2:
                    apps.append((parts[0], parts[1]))
        return apps
    except subprocess.CalledProcessError:
        return []

def get_running_flatpaks() -> dict:
    """
    Retrieve a dictionary of running Flatpak applications.
    
    :return: A mapping from app_id to instance_id.
    """
    try:
        result = subprocess.run(
            ["flatpak", "ps", "--columns=instance,application"],
            capture_output=True, text=True, check=True
        )
        running_apps = {}
        for line in result.stdout.strip().splitlines():
            if line:
                parts = line.split("\t")
                if len(parts) == 2:
                    running_apps[parts[1]] = parts[0]
        return running_apps
    except subprocess.CalledProcessError:
        return {}

def run_flatpak(app_id: str) -> None:
    """
    Launch a Flatpak application in its own process group so that it does not receive signals 
    from the parent process.
    
    :param app_id: The Flatpak application ID.
    """
    subprocess.Popen(
        ["flatpak", "run", app_id],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        preexec_fn=os.setpgrp
    )

def stop_flatpak(instance_id: str) -> None:
    """
    Stop a running Flatpak application.
    
    :param instance_id: The instance ID of the running application.
    """
    subprocess.run(
        ["flatpak", "kill", instance_id],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

def get_flatpak_description(app_id: str) -> str:
    """
    Retrieve the description of a Flatpak application.
    
    :param app_id: The application ID.
    :return: A string description, or a default message if unavailable.
    """
    try:
        result = subprocess.run(
            ["flatpak", "info", "--show-description", app_id],
            capture_output=True, text=True, check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return "No description available."

def search_flatpak_packages(term: str) -> list:
    """
    Search for Flatpak packages matching the provided term.
    
    :param term: The search term.
    :return: A list of tuples (app_id, name, description), limited to the first 150 entries.
    """
    if not term:
        return []
    try:
        result = subprocess.run(
            ["flatpak", "search", "--columns=application,name,description", term],
            capture_output=True, text=True, check=True
        )
        lines = result.stdout.strip().splitlines()
        # Skip a header line if present.
        if lines and ("Application" in lines[0] or "Name" in lines[0]):
            lines = lines[1:]
        packages = []
        for line in lines:
            if line:
                parts = line.split("\t")
                if len(parts) >= 2:
                    app_id = parts[0].strip()
                    name = parts[1].strip()
                    description = parts[2].strip() if len(parts) > 2 else ""
                    packages.append((app_id, name, description))
        return packages[:150]
    except subprocess.CalledProcessError:
        return []
