import os
import pygame as pg

def count_files(directory):
    try:
        return sum(1 for item in os.listdir(directory) if os.path.isfile(os.path.join(directory, item)))
    except (FileNotFoundError, NotADirectoryError, PermissionError, Exception):
        return -1

def play_sound(sound_path):
    try:
        sound = pg.mixer.Sound(sound_path)
        sound.play()
        return True
    except pg.error:
        return False
    except FileNotFoundError:
        return False
    except Exception:
        return False
