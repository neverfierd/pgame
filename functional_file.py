import os
import pygame as pg


def count_files(directory):
    try:
        return sum(1 for item in os.listdir(directory) if os.path.isfile(os.path.join(directory, item)))
    except (FileNotFoundError, NotADirectoryError, PermissionError, Exception):
        return -1

def get_statistic(filename):
    res = {}
    with open(filename, 'r') as file:
        stat = file.read().split('\n')
        for element in stat:
            try:
                k, v = element.split(':')
                res[k.strip()] = int(v)
            except Exception:
                print(f'ошибка загрузки статистки {k}')
    return res

def play_sound(sound_path):
    try:
        sound = pg.mixer.Sound(sound_path)
        sound.play()
        return True
    except Exception:
        print(f"путь к аудиофайлу {sound_path} не найден")
        return False
