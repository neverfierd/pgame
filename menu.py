import pygame as pg
import sys, os

import physics

pg.init()

WIDTH, HEIGHT = 800, 600
CELL_SIZE = 25
screen = pg.display.set_mode((WIDTH, HEIGHT))
pg.display.set_caption("Простое приложение Pygame")
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
font_1 = pg.font.Font(None, 36)
font_2 = pg.font.Font(None, 48)
font_3 = pg.font.Font(None, 16)
clock = pg.time.Clock()

###for Button functional
# 0 - 9 - menu_main_buttons
# 10 - 19 - settings_main_buttons

resolutions = {10: (1600, 1200), 11: (1280, 960), 12: (1280, 720), 13: (1920, 1080), 14: 'fullscreen'}

game_start_params = {'resolution': (1280, 720), 'difficulty': 'normal'}


def change_resolution(res):
    game_start_params['resolution'] = res


def load_image(name, player=False, colorkey=None):
    crop_rect = pg.Rect(10, 15, 30, 56)
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pg.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image if not player else (image, pg.Surface.subsurface(image, crop_rect))


class Menu:
    def __init__(self, width, height):
        self.width, self.height = (width, height)
        self.menu = pg.Surface((self.width, self.height))
        self.menu.fill(pg.color.Color('white'))
        self.settings_opened = False
        self.menu_oppened = True

    def render(self):
        if self.settings_opened:
            self.open_settigns()
        elif self.menu_oppened:
            self.open_menu()
        screen.blit(self.menu, (0, 0))

    def open_menu(self):
        self.menu.fill(pg.color.Color('white'))
        button_container.clear()
        play_button = Button((50, 150), 150, 50, 'ИГРАТЬ', 1)
        settings_button = Button((50, 250), 220, 50, 'НАСТРОЙКИ', 2)
        level_current = pg.font.Font(None, 22).render(f'ТЕКУЩИЙ УРОВЕНЬ {game_start_params['difficulty']}', True,
                                                      pg.color.Color('red'))

        level_peace = Button((WIDTH - 350, HEIGHT * 0.8 - 250), 300, 50, 'МИРНЫЙ', 31, 22)
        level_easy = Button((WIDTH - 350, HEIGHT * 0.8 - 200), 300, 50, 'ЛЕГКИЙ', 32, 22)
        level_normal = Button((WIDTH - 350, HEIGHT * 0.8 - 150), 300, 50, 'СРЕДНИЙ', 33, 22)
        level_hard = Button((WIDTH - 350, HEIGHT * 0.8 - 100), 300, 50, 'СЛОЖНЫЙ', 34, 22)
        level_extreme = Button((WIDTH - 350, HEIGHT * 0.8 - 50), 300, 50, 'ЭКСТРИМАЛЬНЫЙ', 35, 22)

        button_container.append(level_peace)
        button_container.append(level_easy)
        button_container.append(level_normal)
        button_container.append(level_hard)
        button_container.append(level_extreme)

        button_container.append(play_button)
        button_container.append(settings_button)

        # blits
        self.menu.blit(level_current, (WIDTH - 300, HEIGHT - HEIGHT * 0.8))
        screen.blit(self.menu, (0, 0))

    def open_settigns(self):
        self.menu.fill(pg.color.Color('white'))
        button_container.clear()
        screen_size_text = font_1.render('РАЗРЕШЕНИЕ', True, pg.color.Color('black'))
        screen_size_text_rect = screen_size_text.get_rect()
        screen_size_text_rect.x, screen_size_text_rect.y = (50, 50)
        screen_size_current = font_3.render('текущее разрешение: '
                                            + str(game_start_params.get('resolution')), True, pg.color.Color('black'))

        res_button_1 = Button((50, 150), 300, 40, '1600 x 1200 (4:3)', 10)
        res_button_2 = Button((50, 200), 300, 40, '1280 x 960 (4:3)', 11)
        res_button_3 = Button((50, 250), 300, 40, '1280 x 720(16:9)', 12)
        res_button_4 = Button((50, 300), 300, 40, '1920 x 1080(16:9)', 13)
        fullscreen_button = Button((50, 450), 300, 40, 'Полноэкранный', 14)
        confirm_button = Button((400, 400), 150, 50, 'СОХРАНИТЬ', 19)

        res_buttons = [res_button_1, res_button_2, res_button_3, res_button_4, fullscreen_button, confirm_button]

        button_container.extend(res_buttons, )
        # button container append
        self.menu.blit(screen_size_text, screen_size_text_rect)
        self.menu.blit(screen_size_current, (screen_size_text_rect.x, screen_size_text_rect.bottom + 20))


class Button:
    def __init__(self, pos, width, height, text, functional, size=1):
        self.width, self.height = (width, height)
        self.x, self.y = pos
        self.text = text
        self.f = functional
        self.size = size

        self.surface = pg.Surface((self.width, self.height))
        self.surface.fill(pg.color.Color('white'))

        self.text_surface = font_1.render(self.text, True, pg.color.Color('red'))
        self.text_rect = self.text_surface.get_rect()

        self.rect = pg.Rect(self.x, self.y, self.width, self.height)

    def update(self, pos, event=None):
        if self.rect.collidepoint(pos):
            if self.size == 1:
                self.text_surface = font_2.render(self.text, True, pg.color.Color('red'))
            else:
                self.text_surface = pg.font.Font(None, self.size + 10).render(self.text, True, pg.color.Color('red'))
            # here you can add buttons and change their functions
            if event and self.f == 1:
                physics.game_parameters = game_start_params
                try:
                    if game_start_params['resolution'] == 'fullscreen':
                        physics.game = physics.Game(game_start_params, True)
                        # pg.display.set_mode((0, 0), pg.FULLSCREEN)
                    else:
                        physics.game = physics.Game(game_start_params, False)
                        # pg.display.set_mode(game_start_params['resolution'])
                    # physics.game = physics.Game(game_start_params)
                    physics.game.run()
                    pg.quit()
                except Exception as e:
                    print(f"Error starting game: {e}")

            if event and self.f == 2:
                menu.menu_oppened = False
                menu.settings_opened = True
            if event and self.f in (10, 11, 12, 13, 14):
                change_resolution(resolutions.get(self.f))
            if event and self.f == 19:
                menu.settings_opened = False
                menu.menu_oppened = True
            if event and self.f == 31:
                game_start_params['difficulty'] = 'peace'
            if event and self.f == 32:
                game_start_params['difficulty'] = 'easy'
            if event and self.f == 33:
                game_start_params['difficulty'] = 'normal'
            if event and self.f == 34:
                game_start_params['difficulty'] = 'hard'
            if event and self.f == 35:
                game_start_params['difficulty'] = 'extreme'
        else:
            if self.size != 1:
                self.text_surface = pg.font.Font(None, self.size).render(self.text, True, pg.color.Color('red'))
            else:
                self.text_surface = font_1.render(self.text, True, pg.color.Color('red'))

        self.surface.fill(pg.color.Color('white'))
        self.surface.blit(self.text_surface, self.text_rect)

    def render(self):
        screen.blit(self.surface, (self.x, self.y))
        # pg.draw.rect(screen, pg.color.Color('blue'), self.rect, 1)  # Рисуем рамку кнопки


menu = Menu(WIDTH, HEIGHT)
button_container = []

running = True
while running:
    mouse_pos = pg.mouse.get_pos()
    cur_time = pg.time.get_ticks()
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
            pass
        if event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 1:
                for button in button_container:
                    if button.rect.collidepoint(mouse_pos):
                        button.update(mouse_pos, event)

    keys = pg.key.get_pressed()
    # update block
    menu.render()
    for button in button_container:
        button.update(mouse_pos)
        button.render()

    pg.display.flip()

    clock.tick(30)

pg.quit()
sys.exit()
