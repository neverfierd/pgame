import os

def count_files(directory):
    try:
        return sum(1 for item in os.listdir(directory) if os.path.isfile(os.path.join(directory, item)))
    except (FileNotFoundError, NotADirectoryError, PermissionError, Exception):
        return -1

