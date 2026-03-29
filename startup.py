"""
Auto-start module.
Manages adding/removing the application from Windows startup.
"""

import os
import sys
import shutil

from config import APP_NAME


def get_startup_folder() -> str:
    """Returns the Windows Startup folder path."""
    return os.path.join(
        os.getenv("APPDATA", ""),
        "Microsoft", "Windows", "Start Menu", "Programs", "Startup"
    )


def get_shortcut_path() -> str:
    """Returns the full path to the startup shortcut/script."""
    return os.path.join(get_startup_folder(), f"{APP_NAME}.bat")


def is_auto_start_enabled() -> bool:
    """Checks if the application is set to auto-start."""
    return os.path.exists(get_shortcut_path())


def enable_auto_start() -> bool:
    """
    Enables auto-start by creating a .bat launcher in the Windows Startup folder.

    If running as a .exe (frozen), copies the exe to startup.
    If running as .py, creates a batch file that launches the script with pythonw.

    Returns:
        True if successful, False otherwise.
    """
    try:
        startup_folder = get_startup_folder()
        if not os.path.exists(startup_folder):
            os.makedirs(startup_folder, exist_ok=True)

        if getattr(sys, 'frozen', False):
            # Running as compiled .exe
            exe_path = sys.executable
            shortcut_path = os.path.join(startup_folder, f"{APP_NAME}.exe")
            if os.path.abspath(exe_path) != os.path.abspath(shortcut_path):
                shutil.copy2(exe_path, shortcut_path)
        else:
            # Running as .py script — create a .bat file
            script_path = os.path.abspath(sys.argv[0])
            bat_path = get_shortcut_path()
            with open(bat_path, 'w') as f:
                f.write(f'@echo off\nstart "" pythonw "{script_path}"\n')

        return True
    except Exception as e:
        print(f"Failed to enable auto-start: {e}")
        return False


def disable_auto_start() -> bool:
    """
    Disables auto-start by removing the launcher from the Startup folder.

    Returns:
        True if successful or already disabled, False otherwise.
    """
    try:
        shortcut = get_shortcut_path()
        if os.path.exists(shortcut):
            os.remove(shortcut)

        # Also check for exe variant
        exe_shortcut = os.path.join(get_startup_folder(), f"{APP_NAME}.exe")
        if os.path.exists(exe_shortcut):
            os.remove(exe_shortcut)

        return True
    except Exception as e:
        print(f"Failed to disable auto-start: {e}")
        return False
