import random
import time
import pygame as pg
import sys
import os
import math

import functional_file
from enemy import Enemy
from functional_file import count_files, play_sound

pg.font.init()

font_3 = pg.font.Font(None, 32)

game_parameters = {
    'resolution': (1920, 1080),
    'difficulty': 'extreme'
}

images = {1: 'textures/blocks/mud0.png',
          2: 'textures/blocks/box.png',
          3: 'textures/blocks/brick.png',
          4: 'textures/blocks/mossy_brick.jpg',
          5: 'textures/blocks/old_bricks.jpg',
          100: 'textures/entities/medkit.png',
          101: 'textures/entities/bullet_box.png',
          102: 'textures/entities/armor.png'}

shoot_sounds = {'pistol': 'data/weapon/pistol_shoot.wav',
                'carabine': 'data/weapon/carabine_shoot.wav',
                'rifle': 'data/weapon/rifle_shoot.wav',
                'shotgun': 'data/weapon/shotgun_shoot.wav'}

guns_icons = {1: pg.image.load('data/textures/weapons/pistol_icon.png'),
              2: pg.image.load('data/textures/weapons/carabine_icon.png'),
              3: pg.image.load('data/textures/weapons/rifle_icon.png'),
              4: pg.image.load('data/textures/weapons/shotgun_icon.png')}

### comments for effects
# 1 - any block is hitten by bullet
# 2 - any sprite is hitetn by bullet (blood)
effects = {
    1: ['effects/hit_block/hit_block0.png', 'effects/hit_block/hit_block1.png', 'effects/hit_block/hit_block2.png',
        'effects/hit_block/hit_block3.png', 'effects/hit_block/hit_block4.png'],
    2: ['effects/hit_sprite/hit_bloody_sprite0.png', 'effects/hit_sprite/hit_bloody_sprite1.png',
        'effects/hit_sprite/hit_bloody_sprite2.png', 'effects/hit_sprite/hit_bloody_sprite3.png',
        'effects/hit_sprite/hit_bloody_sprite4.png', 'effects/hit_sprite/hit_bloody_sprite5.png'

        ]}
# delay for zombie, max zombie count, supplies spawn delay
difficulties = {'peace': (0, 0, 10000), 'easy': (10, 10, 20), 'normal': (8, 15, 20), 'hard': (5, 20, 25),
                'extreme': (3, 30, 25)}


def read_level_file(filename):
    level_array = []

    with open(filename, 'r') as file:
        for line in file:
            line = line.strip().strip(',')
            if line:
                row = list(map(int, line.strip('[]').split(', ')))
                level_array.append(row)

    return level_array


level = read_level_file('data/level.txt')


def get_spawn_points(level, block_size):
    spawn_points = []
    for row_index, row in enumerate(level):
        for col_index, block in enumerate(row):
            if block != 0:
                # check if can spawn(2 blocks above is empty)
                if (row_index > 1 and
                        level[row_index - 1][col_index] == 0 and
                        level[row_index - 2][col_index] == 0):
                    x = col_index * block_size
                    y = (row_index - 2) * block_size  # два блока над блоком
                    spawn_points.append((x, y))
    return spawn_points


def check_collision(bullet, object):
    bullet_center = bullet.center
    object_center = object.center

    dx = bullet_center[0] - object_center[0]
    dy = bullet_center[1] - object_center[1]

    res = [0, 0]

    if abs(dx) > abs(dy):
        if dx > 0:
            return False, res
        else:
            res[0] = 1
            return True, res
    else:
        if dy > 0:
            return False, res
        else:  # Сверху
            res[1] = 1
            return True, res


class Camera:
    def __init__(self, width, height):
        self.camera = pg.Rect(0, 0, width, height)
        self.width = width
        self.height = height
        self.scroll_x = 0
        self.scroll_y = 0
        self.smoothness = 10

    def apply(self, entity, rect=False):  # camera apply for rects
        if rect: return entity.move(self.camera.topleft)
        return entity.rect.move(self.camera.topleft)

    def apply_dest(self, pos):  # camera apply for coords
        x, y = pos
        return (x - self.scroll_x, y - self.scroll_y)

    def update(self, target):
        self.scroll_x += (target.rect.centerx - self.width // 2 - self.scroll_x) // 10
        self.scroll_y += (target.rect.centery - self.height // 2 - self.scroll_y) // 10
        self.camera = pg.Rect(-self.scroll_x, -self.scroll_y, self.width, self.height)


class Game:
    def __init__(self, game_parameters, fullsceen=False):
        self.game_parameters = game_parameters
        self.G = 5
        self.WIDTH, self.HEIGHT = self.game_parameters.get('resolution') if not fullsceen else (1920, 1080)
        self.cell_size = 30 if self.HEIGHT <= 1600 else 40
        self.map_size = ()
        self.difficulty = self.game_parameters.get('difficulty', 10)
        self.max_zombies = difficulties.get(self.difficulty, (10000, 10, 20))[1]

        self.spawnpoints = get_spawn_points(level, self.cell_size)
        self.templist_spawns = []
        self.last_spawn = time.time()
        self.last_supplies_spawm = time.time()
        self.spawn_flag = True
        self.written_flag = False

        self.clock = pg.time.Clock()
        self.screen = pg.display.set_mode((self.WIDTH, self.HEIGHT)) if not fullsceen else pg.display.set_mode(
            (self.WIDTH, self.HEIGHT), pg.FULLSCREEN)

        self.camera = Camera(self.WIDTH, self.HEIGHT)

        self.player = None
        self.block_group = pg.sprite.Group()
        self.bullet_group = pg.sprite.Group()
        self.effect_group = pg.sprite.Group()
        self.entity_group = pg.sprite.Group()
        self.enemy_group = pg.sprite.Group()

        self.running = True
        self.game_over = False
        self.cur_stat = functional_file.get_statistic('data/stats.txt')

    def reset_game(self):
        self.block_group.empty()
        self.bullet_group.empty()
        self.effect_group.empty()
        self.entity_group.empty()
        self.enemy_group.empty()

        self.spawnpoints = get_spawn_points(level, self.cell_size)
        self.templist_spawns = []
        self.last_spawn = time.time()
        self.last_supplies_spawm = time.time()
        self.spawn_flag = True

        self.player = Player(self.WIDTH // 2, 100)

        self.set_blocks()

        self.game_over = False

    def handle_game_over(self):
        if not self.written_flag:
            if self.cur_stat[self.difficulty] < self.player.kill_count:
                self.cur_stat[self.difficulty] = self.player.kill_count

            self.cur_stat['total'] += self.player.kill_count

            self.write_stats()
            self.written_flag = True

        for event in pg.event.get():
            if event.type == pg.QUIT or event.type == pg.K_ESCAPE:
                self.running = False
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_r:
                    self.reset_game()
                if event.key == pg.K_ESCAPE:
                    self.running = False

        font = pg.font.Font(None, 74)
        text = font.render(f'ты умер. убийств: {self.player.kill_count}', True, (255, 0, 0))
        text_rect = text.get_rect(center=(self.WIDTH // 2, self.HEIGHT // 2))
        self.screen.blit(text, text_rect)

        font = pg.font.Font(None, 50)
        text = font.render('нажми R  для рестарта', True, (255, 255, 255))
        text_rect = text.get_rect(center=(self.WIDTH // 2, self.HEIGHT // 2 + 50))
        self.screen.blit(text, text_rect)

        pg.display.flip()

    def load_image(self, name, player=False, colorkey=None):
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
        if player:
            cropped_image = image.subsurface(pg.Rect(18, 18, 68 - 34, 72 - 20))
            # scaled_image = pg.transform.scale(cropped_image, (self.cell_size, self.cell_size * 2))
            return image, cropped_image
        else:
            return pg.transform.scale(image, (self.cell_size, self.cell_size))

    def write_stats(self):
        saved_stat = self.cur_stat.copy()
        try:
            with open('data/stats.txt', 'w') as file:
                for key, value in self.cur_stat.items():
                    file.write(f'{key}: {value}\n')
        except Exception:
            print('error writing file')
            self.cur_stat = saved_stat


    def spawn_enemies(self):
        if self.spawnpoints and self.spawn_flag:
            delay = difficulties.get(self.difficulty, (10000, 15, 20))[0]
            supplies_delay = difficulties.get(self.difficulty, (10000, 15, 20))[2]
            if self.last_spawn + delay <= time.time():

                suitable_spawnpoints = []
                for coords in self.spawnpoints:
                    is_suitable = True
                    for prev_coords in self.templist_spawns:
                        # calculate differendce between coordinates
                        x_diff = abs(coords[0] - prev_coords[0])
                        y_diff = abs(coords[1] - prev_coords[1])

                        # check difference between old coords
                        if x_diff < 3 and y_diff < 5 and (coords[1] != prev_coords[1] or x_diff < 3):
                            is_suitable = False
                            break

                    if is_suitable:
                        suitable_spawnpoints.append(coords)

                if suitable_spawnpoints:
                    bosspawn_chance = random.random()
                    if time.time() - self.last_supplies_spawm >= supplies_delay:
                        self.spawm_supplies(suitable_spawnpoints)
                    coords = random.choice(suitable_spawnpoints)
                    if bosspawn_chance > 0.90:
                        enemy = Enemy(coords, 'dark', random.randint(350, 500), 1,
                                      (self.cell_size * 2, self.cell_size * 4), (random.randint(400, 500), 60),
                                      (150, 15000))
                    elif bosspawn_chance <= 0.9:
                        enemy = Enemy(coords, 'ademan', random.randint(80, 120), random.randint(1, 2),
                                      (self.cell_size, self.cell_size * 2), (random.randint(180, 230), 60),
                                      (random.randint(15, 25), random.randint(8000, 12000)))
                    self.enemy_group.add(enemy)
                    self.templist_spawns.append(coords)
                    self.last_spawn = time.time()
                # delete positions if they get old
                if len(self.templist_spawns) > 30:
                    self.templist_spawns.pop(0)

    def spawm_supplies(self, coords):
        x, y = random.choice(coords)
        chance = random.random()
        if chance < 0.51:
            medkit = Entity(x, y + self.cell_size, 100, 1)
            self.entity_group.add(medkit)
        elif chance > 0.5:
            if chance >=0.75:
                armor = Entity(x, y + self.cell_size, 102, 3)
                self.entity_group.add(armor)
            else:
                bullet_box = Entity(x, y + self.cell_size, 101, 2)
                self.entity_group.add(bullet_box)
        self.last_supplies_spawm = time.time()

    def set_blocks(self):
        rows = len(level)
        cols = len(level[0])
        self.map_size = (cols, rows)
        for y in range(rows):
            for x in range(cols):
                try:
                    block = Block(x * self.cell_size, y * self.cell_size, level[y][x])
                    self.block_group.add(block)
                except Exception:
                    f"Текстура {level[y][x]} - {images.get(level[y][x], 0)} не найдена или введена с ошибкой"

    def handle_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT or event.type == pg.K_ESCAPE:
                self.running = False
            if event.type == pg.KEYDOWN:
                self.player.change_gun(event)
                if event.key == pg.K_w:
                    self.player.jump()
                if event.key == pg.K_ESCAPE:
                    self.running = False
                if event.key == pg.K_r:
                    self.player.reload()
            if event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_x, mouse_y = pg.mouse.get_pos()
                    angle = math.atan2(mouse_y - self.camera.apply(self.player).centery,
                                       mouse_x - self.camera.apply(self.player).centerx)
                    self.player.shoot(angle)
                elif event.button == 3:
                    mouse_x, mouse_y = pg.mouse.get_pos()
                    angle = math.atan2(mouse_y - self.camera.apply(self.player).centery,
                                       mouse_x - self.camera.apply(self.player).centerx)
                    self.player.throw_grenade(angle)

    def death_scene(self, duration_ms):
        alpha_surface = pg.Surface(self.screen.get_size(), pg.SRCALPHA)
        start_time = pg.time.get_ticks()
        clock = pg.time.Clock()
        while pg.time.get_ticks() - start_time < duration_ms:
            alpha = int(255 * (pg.time.get_ticks() - start_time) / duration_ms)
            if alpha > 255:
                alpha = 255

            alpha_surface.fill((0, 0, 0, alpha))
            self.screen.blit(self.screen, (0, 0))
            self.screen.blit(alpha_surface, (0, 0))

            pg.display.flip()
            clock.tick(50)

        self.game_over = True

    def update(self):
        if len(self.enemy_group) >= self.max_zombies:
            self.spawn_flag = False
        elif len(self.enemy_group) < self.max_zombies:
            self.spawn_flag = True

        keys = pg.key.get_pressed()
        if keys[pg.K_d]:
            self.player.update_move(5, 1)
        if keys[pg.K_a]:
            self.player.update_move(5, -1)

        if not any(keys):
            self.player.update_move(0, self.player.d)
        ##screenfill
        self.screen.fill((33, 31, 32))  # self.screen.fill((255,255,255))
        self.camera.update(self.player)

        self.spawn_enemies()

        for effect in self.effect_group:
            effect.render()

        for entity in self.entity_group:
            entity.update()

        for block in self.block_group:
            block.update()

        for bullet in self.bullet_group:
            self.screen.blit(bullet.image, self.camera.apply(bullet))

        for enemy in self.enemy_group:
            enemy.update(self.block_group, self.player)
            enemy.draw_enemy(self.screen, self.camera)

        self.player.draw_player(self.camera)

        self.block_group.update()
        self.bullet_group.update()
        self.enemy_group.update(self.block_group, self.player)
        self.player.update()
        self.player.show_info()

    def run(self):
        pg.init()
        pg.mixer.init()
        self.reset_game()
        self.set_blocks()

        while self.running:
            if self.game_over:
                self.handle_game_over()
            else:
                self.handle_events()
                self.update()
                pg.display.flip()
                self.clock.tick(50)
        pg.quit()


class Player(pg.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = game.load_image('player_animation/idle/idle_1.png', True)[1]
        self.image_rect = self.image.get_rect()
        self.rect = pg.Rect(x, y, game.cell_size, game.cell_size * 2)

        self.hp = 100
        self.armor = 150
        self.grenades = 2
        self.kill_count = 0

        self.max_hp = 100
        self.max_armor = 150
        self.max_grenades = 5

        self.v_x = 0
        self.v_y = 0
        self.d = 1
        self.on_ground = False

        self.width = game.cell_size
        self.height = game.cell_size * 2

        self.last_update = pg.time.get_ticks()
        self.cur_frame = 0
        self.cur_anim = 0
        self.animation_cd = 200
        self.animations = {
            'idle': [game.load_image(f'player_animation/idle/idle_{i}.png', True)[1] for i in
                     range(count_files('data/player_animation/idle'))],
            'run': [game.load_image(f'player_animation/run/run_{i}.png', True)[1] for i in
                    range(count_files('data/player_animation/run'))]
        }

        self.guns = {1: Weapon(40, 20, 14, 5000, 350, 'pistol', None, 1),
                     2: Weapon(85, 25, 30, 5000, 200, 'carabine', None, 2),
                     3: Weapon(320, 30, 10, 6500, 4000, 'rifle', None, 3),
                     4: Weapon(20, 25, 8, 6500, 1500, 'shotgun', None, 4)
                     }

        self.bullets = 50
        self.can_shoot = True
        self.last_shoot_time = 0
        self.weapon = self.guns[1]

    def show_info(self):
        if not game.game_over:
            if self.hp <= 0: self.hp = 0
            if self.armor <= 0: self.armor = 0
            if self.hp >= self.max_hp: self.hp = self.max_hp
            if self.armor >= self.max_armor: self.armor = self.max_armor
            if self.grenades >= self.max_grenades: self.grenades = self.max_grenades

            hp_surf = pg.surface.Surface((210, 40))
            hp_surf.fill(pg.color.Color('white'))
            red_sub = pg.Surface((200, 30))
            red_sub.fill(pg.color.Color(153, 40, 8))
            hp_surf.blit(red_sub, (5, 5))
            if self.hp > 0:
                hp_rect = pg.Surface(((self.hp * 2), 30))
                hp_rect.fill((pg.color.Color((0, 154, 23))))
                hp_surf.blit(hp_rect, (5, 5))
            if self.armor > 0:
                armor_surf = pg.Surface((abs(self.armor / self.max_armor) * 200, 10))
                armor_surf.fill((pg.color.Color(101, 113, 194)))
                hp_surf.blit(armor_surf, (5, 5))

            game.screen.blit(hp_surf, (30, 30))

            kill_cnt = font_3.render(f"убийства: {self.kill_count}", True, pg.color.Color('white'))
            game.screen.blit(kill_cnt, (50, hp_surf.get_rect().bottom + 30))

            bullet_counter = font_3.render(f"{self.weapon.bullets} / {self.bullets}", True, pg.color.Color('white'))
            game.screen.blit(bullet_counter, (game.WIDTH - 150, 50))
            game.screen.blit(guns_icons.get(self.weapon.type, 1), (game.WIDTH - 190, 80))
            for i in range(self.grenades):
                game.screen.blit(pg.transform.scale(game.load_image('weapon/images/grenade.png'),
                                                    (game.cell_size * 2, game.cell_size * 2)),
                                 (game.WIDTH - 190 + game.cell_size * i, 130))

    def shoot(self, angle):
        if pg.time.get_ticks() - self.weapon.shoot_cd >= self.last_shoot_time:
            self.can_shoot = True

        if self.weapon.bullets > 0 and self.can_shoot:
            if self.weapon.type == 4:
                [game.bullet_group.add(
                    Bullet(self.rect.centerx, self.rect.centery - 10, angle, self.weapon.speed + random.randint(-5, 5),
                           3 * i)) for i in range(-4, 5)]
                play_sound(shoot_sounds.get(self.weapon.name))
                self.weapon.bullets -= 1
                self.last_shoot_time = pg.time.get_ticks()
                self.can_shoot = False
            else:
                bullet = Bullet(self.rect.centerx, self.rect.centery - 10, angle,
                                self.weapon.speed + random.randint(-5, 5), random.randint(-1, 1))
                play_sound(shoot_sounds.get(self.weapon.name))
                game.bullet_group.add(bullet)
                self.weapon.bullets -= 1
                self.last_shoot_time = pg.time.get_ticks()
                self.can_shoot = False
        if self.weapon.bullets <= 0:
            play_sound('data/weapon/shackle.mp3')

    def reload(self):
        if self.bullets > 0:
            self.can_shoot = False
            need_to_reload = self.weapon.capacity - self.weapon.bullets
            if self.bullets >= need_to_reload:
                self.bullets -= need_to_reload
                self.weapon.bullets += need_to_reload
                play_sound('data/weapon/reload_carabine.wav')  ## make it like a shoot sound (this WIP)
                self.last_shoot_time += self.weapon.reload_time
            elif self.bullets <= need_to_reload:
                self.weapon.bullets += self.bullets
                self.bullets = 0
                play_sound('data/weapon/reload_carabine.wav')
                self.last_shoot_time += self.weapon.reload_time
            else:
                return

    def throw_grenade(self, angle):
        if self.grenades > 0:
            grenade = Grenade(self.rect.centerx, self.rect.centery - 10, angle, 10, 5000, pg.time.get_ticks())
            game.bullet_group.add(grenade)
            self.grenades -= 1

    def change_gun(self, event=None):
        if event:
            if event.key == pg.K_1:
                weapon = self.guns.get(1)
                if weapon:
                    self.weapon = weapon

            elif event.key == pg.K_2:
                weapon = self.guns.get(2)
                if weapon:
                    self.weapon = weapon

            elif event.key == pg.K_3:
                weapon = self.guns.get(3)
                if weapon:
                    self.weapon = weapon

            elif event.key == pg.K_4:
                weapon = self.guns.get(4)
                if weapon:
                    self.weapon = weapon

    def update_move(self, v, d):
        self.v_x = v
        self.d = d

    def update_animation(self):
        if self.v_x == 0:
            a_type = 'idle'
        else:
            a_type = 'run'

        anim_index = self.animations[a_type]
        if self.cur_anim != anim_index:
            self.cur_frame = 0
            self.cur_anim = anim_index

        length = len(self.animations[a_type])
        current_time = pg.time.get_ticks()
        if current_time - self.last_update >= self.animation_cd:
            self.cur_frame = (self.cur_frame + 1) % length
            self.image = self.animations[a_type][self.cur_frame]
            self.last_update = current_time

    def jump(self):
        if self.on_ground:
            self.v_y = -40
            self.on_ground = False

    def draw_player(self, camera):
        if self.d > 0:
            game.screen.blit(self.image, camera.apply(self))
        elif self.d < 0:
            game.screen.blit(pg.transform.flip(self.image, True, False), camera.apply(self))
        pg.draw.rect(game.screen, pg.color.Color('blue'), camera.apply(self), 1)
        pg.draw.rect(game.screen, pg.color.Color('red'), camera.apply(self.image_rect, True), 1)

    def update(self):
        if self.hp <= 0:
            game.death_scene(3000)
            return

        self.image_rect.centerx = self.rect.centerx
        self.image_rect.bottom = self.rect.bottom
        self.v_y += game.G
        dx = self.v_x * self.d

        if self.v_y > 20:
            self.v_y = 20

        for obj in game.block_group:
            if obj.rect.colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                dx = 0
            if obj.rect.colliderect(self.rect.x, self.rect.y + self.v_y, self.width, self.height):
                if self.v_y < 0:
                    self.v_y = 0
                    self.v_y = obj.rect.bottom - self.rect.top
                elif self.v_y >= 0:
                    self.v_y = 0
                    self.on_ground = True

        self.rect.x += dx
        self.rect.y += self.v_y
        self.update_animation()


class Effect(pg.sprite.Sprite):
    def __init__(self, x, y, effect_type, shift_needed=(0, 0)):
        super().__init__()
        self.names = effects.get(effect_type)
        self.images = [game.load_image(self.names[i]) for i in range(len(self.names))]
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y
        self.kill_flag = False
        self.frame_index = 0
        self.animation_speed = 0.1
        self.last_update = pg.time.get_ticks()
        self.shift_need = shift_needed[0]
        self.shift = shift_needed[1]

    def update(self):
        if not self.kill_flag:
            now = pg.time.get_ticks()
            if now - self.last_update > self.animation_speed * 1000:
                self.last_update = now
                self.frame_index += 1
                if self.frame_index >= len(self.images):
                    self.frame_index = 0
                    self.kill_flag = True
                self.image = self.images[self.frame_index]

    def render(self):
        self.update()
        if not self.kill_flag:
            if not self.shift_need:
                game.screen.blit(self.image, game.camera.apply_dest((self.rect.x - game.cell_size // 2, self.rect.y)))
            elif self.shift_need:
                game.screen.blit(self.image, game.camera.apply_dest(
                    (self.rect.x - game.cell_size // 2 * self.shift[0], self.rect.y - game.cell_size * self.shift[1])
                ))


class Bullet(pg.sprite.Sprite):
    def __init__(self, x, y, angle, speed, shift=0, damage=0):
        super().__init__()
        self.image = pg.transform.scale(game.load_image('weapon/images/bullet.png'), (4, 4))
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = speed
        angle_degrees = math.degrees(angle)
        self.damage = damage
        shifted_angle_degrees = angle_degrees + shift
        self.angle = math.radians(shifted_angle_degrees)

    def update(self):
        for block in game.block_group:
            if self.rect.colliderect(block.rect):
                collision, shift = check_collision(self.rect, block.rect)

                effect = Effect(self.rect.x, self.rect.y, 1, (collision, shift))
                game.effect_group.add(effect)
                play_sound(f'data/weapon/block_hit{random.choice(range(0, 5))}.mp3')
                self.kill()

        for enemy in game.enemy_group:
            if self.rect.colliderect(enemy.rect):
                if enemy.hp > 0:
                    collision, shift = check_collision(self.rect, enemy.rect)

                    effect = Effect(self.rect.x, self.rect.y, 2, (collision, shift))
                    play_sound('data/weapon/bullet_sprite_hit.wav')
                    game.effect_group.add(effect)

                    if enemy.hp > 0 and self.damage == 0:
                        enemy.hp -= game.player.weapon.damage
                    else:
                        enemy.hp -= self.damage
                    self.kill()

        self.rect.x += self.speed * math.cos(self.angle)
        self.rect.y += self.speed * math.sin(self.angle)


class Grenade(pg.sprite.Sprite):
    def __init__(self, x, y, angle, speed, delay, shoot_time):
        super().__init__()
        self.image = pg.transform.scale(
            pg.transform.scale(game.load_image('weapon/images/grenade.png'), (game.cell_size, game.cell_size)),
            (20, 20))
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = speed
        self.angle = angle
        self.shoot_time = shoot_time
        self.delay = delay
        self.gravity = 0.5
        self.v_x = speed * math.cos(angle)
        self.v_y = speed * math.sin(angle)
        self.on_ground = False
        self.bounce_factor = 0.7
        self.bounce_count = 0
        self.min_velocity = 0.1

    def update(self):
        self.v_y += self.gravity

        if self.bounce_count < 5:
            self.rect.x += self.v_x
            self.rect.y += self.v_y

        for obj in game.block_group:
            if obj.rect.colliderect(self.rect):
                if self.bounce_count >= 5 or abs(self.v_x) < self.min_velocity and abs(self.v_y) < self.min_velocity:
                    self.v_x = 0
                    self.v_y = 0
                    while obj.rect.colliderect(self.rect):
                        self.rect.y -= 1
                    self.rect.y += 1
                    break

                overlap_x = min(self.rect.right - obj.rect.left, obj.rect.right - self.rect.left)
                overlap_y = min(self.rect.bottom - obj.rect.top, obj.rect.bottom - self.rect.top)

                if overlap_x < overlap_y:
                    if self.v_x > 0:
                        self.rect.right = obj.rect.left
                    elif self.v_x < 0:
                        self.rect.left = obj.rect.right
                    self.v_x = -self.v_x * self.bounce_factor
                    self.v_y *= 0.5
                else:
                    if self.v_y > 0:
                        self.rect.bottom = obj.rect.top
                        self.v_y = -self.v_y * self.bounce_factor
                        self.rect.x += math.copysign(1, self.v_x)
                    elif self.v_y < 0:
                        self.rect.top = obj.rect.bottom
                        self.v_y = -self.v_y * self.bounce_factor

                self.bounce_count += 1

        if self.shoot_time + self.delay <= pg.time.get_ticks():
            self.explode()

    def explode(self):
        for _ in range(25):
            shrapnel_angle = random.uniform(0, 2 * math.pi)  # random angle
            shrapnel_speed = random.uniform(15, 25)
            bullet = Bullet(self.rect.centerx, self.rect.centery, shrapnel_angle, shrapnel_speed, 0, 50)
            game.bullet_group.add(bullet)

        play_sound('data/weapon/grenade_explode.wav')
        self.kill()


class Block(pg.sprite.Sprite):
    def __init__(self, x, y, image_type):
        super().__init__()
        self.image = game.load_image(images.get(image_type, 0))  ###pg.Surface((game.cell_size, game.cell_size))

        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y

    def update(self):
        game.screen.blit(self.image, game.camera.apply_dest((self.rect.x, self.rect.y)))
        pg.draw.rect(game.screen, (0, 0, 0), game.camera.apply(self), 1)


class Weapon:
    def __init__(self, damage, bullet_speed, capacity, reload_time, shoot_cd, name, image, type):
        self.damage = damage
        self.speed = bullet_speed
        self.bullets = capacity
        self.capacity = capacity
        self.reload_time = reload_time
        self.shoot_cd = shoot_cd
        self.name = name
        self.image = image
        self.type = type
        # self.rect = self.image.get_rect()


# class for items that can be interacted
# entity 1-medkit
# entity 2-bullet box
class Entity(pg.sprite.Sprite):
    def __init__(self, x, y, image_type, functional):
        super().__init__()
        self.image = pg.transform.scale(game.load_image(images.get(image_type, 0)), (
            game.cell_size, game.cell_size))  ###pg.Surface((game.cell_size, game.cell_size))

        self.functional = functional
        self.rect = pg.rect.Rect(x, y, game.cell_size, game.cell_size)  # self.image.get_rect()
        self.rect.x, self.rect.y = x, y

    # update medkit and check if player collides self.rect
    def update(self):
        if self.rect.colliderect(game.player.rect):
            if self.functional == 1:
                game.player.hp = min(game.player.hp + 50, 100)

            if self.functional == 2:
                game.player.bullets += 50
                game.player.grenades += random.randint(1, 2)

            if self.functional == 3:
                game.player.armor += 50
            self.kill()

        game.screen.blit(self.image, game.camera.apply_dest((self.rect.x, self.rect.y)))
        # pg.draw.rect(game.screen, (0, 0, 0), game.camera.apply(self), 1)


game = Game(game_parameters, True)

guns = {1: Weapon(40, 20, 14, 5000, 350, 'pistol', None, 1),
        2: Weapon(85, 25, 30, 5000, 200, 'carabine', None, 2),
        3: Weapon(320, 30, 10, 6500, 4000, 'rifle', None, 3),
        4: Weapon(20, 25, 8, 6500, 1500, 'shotgun', None, 4)
        }
