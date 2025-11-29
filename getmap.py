import os
import time
import pygetwindow as gw

user_home = os.path.expanduser("~")
DIRECTORY_PATH = os.path.join(user_home, "AppData", "Local", "osu!", "Songs")

def get_active_map_name():
    """Get the current map name from the osu! window"""
    print("Getmap running")
    while True:
        active_window = gw.getActiveWindow()
        if active_window and len(active_window.title) > 4 and "osu!" in active_window.title:
            return active_window.title
        time.sleep(0.01)

def find_map_directory(map_name):
    """Find the map folder containing the given map name"""
    matching_folders = []
    try:
        # Clean up the map name for better matching
        search_terms = map_name.lower().split(" - ")
        
        for entry in os.scandir(DIRECTORY_PATH):
            if entry.is_dir():
                folder_name_lower = entry.name.lower()
                # Check if all search terms are in the folder name
                if all(term in folder_name_lower for term in search_terms):
                    matching_folders.append(entry.path)
                    print(f"Found matching folder: {entry.name}")
        
        return matching_folders[0] if matching_folders else None
    except Exception as e:
        print(f"Error searching directories: {e}")
        return None

def find_read_data(directory, diffname):
    """Find and read the .osu file matching the difficulty name"""
    try:
        # Scan the directory for .osu files
        with os.scandir(directory) as entries:
            for entry in entries:
                if entry.is_file() and entry.name.endswith(".osu") and diffname in entry.name:
                    file_path = os.path.join(directory, entry.name)
                    with open(file_path, 'r', encoding="utf8") as file:
                        file_content = file.read()
                        return file_content
        print("No matching .osu file found.")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None