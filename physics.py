import random, time
import pygame as pg
import sys, os
import math

from enemy import Enemy
from functional_file import count_files

pg.font.init()

font_3 = pg.font.Font(None, 32)

game_parameters = {
    'resolution': (1920, 1080),
    'difficulty': 'extreme'
}

images = {1: 'textures/blocks/mud0.png',
          2: 'textures/blocks/box.png',
          3: 'textures/blocks/brick.png',
          100: 'textures/entities/medkit.png'}

shoot_sounds = {'pistol': 'data/weapon/pistol_shoot.wav',
                'carabine': 'data/weapon/carabine_shoot.wav',
                'rifle': 'data/weapon/rifle_shoot.wav',
                'shotgun': 'data/weapon/shotgun_shoot.wav'}

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

difficulties = {'easy': 20, 'normal': 15, 'hard': 10, 'peace': 0, 'extreme': 5}


def read_level_file(filename):
    level_array = []

    with open(filename, 'r') as file:
        for line in file:
            line = line.strip().strip(',')
            if line:
                row = list(map(int, line.strip('[]').split(', ')))
                level_array.append(row)

    return level_array


# Пример использования
level = read_level_file('data/level.txt')


def get_spawn_points(level, block_size):
    spawn_points = []
    for row_index, row in enumerate(level):
        for col_index, block in enumerate(row):
            if block == 1:  # Если это блок
                # Проверяем, есть ли 2 блока над ним свободными
                if (row_index > 1 and
                        level[row_index - 1][col_index] == 0 and
                        level[row_index - 2][col_index] == 0):
                    x = col_index * block_size
                    y = (row_index - 2) * block_size  # Два блока над блоком
                    spawn_points.append((x, y))
    return spawn_points


def check_collision(bullet, object):
    if not hasattr(bullet, 'center') or not hasattr(object, 'center'):
        raise ValueError("bullet и object должны иметь атрибут center")

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


class Camera:
    def __init__(self, width, height):
        self.camera = pg.Rect(0, 0, width, height)
        self.width = width
        self.height = height
        self.scroll_x = 0
        self.scroll_y = 0
        self.smoothness = 10  # Плавность скролла

    def apply(self, entity, rect=False):
        if rect: return entity.move(self.camera.topleft)
        return entity.rect.move(self.camera.topleft)

    def apply_dest(self, pos):
        x, y = pos
        return (x - self.scroll_x, y - self.scroll_y)

    def update(self, target):
        # Обновление позиции камеры в зависимости от позиции цели
        self.scroll_x += (target.rect.centerx - self.width // 2 - self.scroll_x) // 10
        self.scroll_y += (target.rect.centery - self.height // 2 - self.scroll_y) // 10
        self.camera = pg.Rect(-self.scroll_x, -self.scroll_y, self.width, self.height)


class Game:
    def __init__(self, game_parameters, fullsceen=False):
        self.game_parameters = game_parameters
        self.WIDTH, self.HEIGHT = self.game_parameters.get('resolution') if not fullsceen else (1920, 1080)
        self.cell_size = 30 if self.HEIGHT <= 1600 else 40
        self.map_size = ()
        self.difficulty = self.game_parameters.get('difficulty', 15)
        self.spawnpoints = get_spawn_points(level, self.cell_size)
        self.last_spawn = time.time()
        self.G = 5
        self.clock = pg.time.Clock()
        self.screen = pg.display.set_mode((self.WIDTH, self.HEIGHT)) if not fullsceen else pg.display.set_mode(
            (self.WIDTH, self.HEIGHT), pg.FULLSCREEN)
        self.player = None
        self.block_group = pg.sprite.Group()
        self.bullet_group = pg.sprite.Group()
        self.effect_group = pg.sprite.Group()
        self.enemy_group = pg.sprite.Group()
        self.running = True
        self.camera = Camera(self.WIDTH, self.HEIGHT)

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
        # return image if not player else (
        #     image, pg.transform.scale(image, (self.cell_size *2, self.cell_size * 2)))

    def spawn_enemies(self):
        if self.spawnpoints:
            delay = difficulties.get(self.difficulty, 0)
            if self.last_spawn + delay <= time.time():
                enemy = Enemy(random.choice(self.spawnpoints), 'ademan', 100, 1, (self.cell_size, self.cell_size * 2))
                self.enemy_group.add(enemy)
                self.last_spawn = time.time()

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
                if event.key == pg.K_w:
                    self.player.jump()
                if event.key == pg.K_ESCAPE:
                    self.running = False
                if event.key == pg.K_r:
                    self.player.reload()
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:  # ЛКМ для стрельбы
                mouse_x, mouse_y = pg.mouse.get_pos()
                angle = math.atan2(mouse_y - self.camera.apply(self.player).centery,
                                   mouse_x - self.camera.apply(self.player).centerx)
                self.player.shoot(angle)

    def update(self):
        keys = pg.key.get_pressed()
        if keys[pg.K_d]:
            self.player.update_move(5, 1)
        if keys[pg.K_a]:
            self.player.update_move(5, -1)

        if not any(keys):
            self.player.update_move(0, self.player.d)

        self.screen.fill((33, 31, 32))
        self.camera.update(self.player)

        self.spawn_enemies()

        for effect in self.effect_group:
            effect.render()
        # Отрисовка блоков с учетом камеры
        for block in self.block_group:
            block.update()

        # Отрисовка пуль с учетом камеры
        for bullet in self.bullet_group:
            self.screen.blit(bullet.image, self.camera.apply(bullet))

        for enemy in self.enemy_group:
            enemy.update(self.block_group, self.player)
            enemy.draw_enemy(self.screen, self.camera)
        # Отрисовка игрока с учетом камеры
        self.player.draw_player(self.camera)
        # self.enemy.draw_enemy(self.screen, self.camera)

        self.block_group.update()
        self.bullet_group.update()
        self.enemy_group.update(self.block_group, self.player)
        self.player.update()
        self.player.show_info()

    def run(self):
        pg.init()
        pg.mixer.init()
        self.player = Player(self.WIDTH // 2, 100)

        # create and set enemies (must be re-worked)
        # self.enemy = Enemy((self.WIDTH // 2 - 200, 300), 'ademan', 500, 1, (game.cell_size, game.cell_size * 2))
        # self.enemy_group.add(
        #     Enemy((self.WIDTH // 2 - 200 - 100 * i, 300), 'ademan', 500, 1, (game.cell_size, game.cell_size * 2)) for i
        #     in range(5))
        self.set_blocks()

        while self.running:
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
        self.hp = 34
        self.v_x = 0
        self.v_y = 0
        self.d = 1
        self.on_ground = False
        self.width = game.cell_size
        self.height = game.cell_size * 2

        self.last_update = pg.time.get_ticks()
        self.cur_frame = 0
        self.cur_anim = 0
        self.animations = {
            'idle': [game.load_image(f'player_animation/idle/idle_{i}.png', True)[1] for i in
                     range(count_files('data/player_animation/idle'))],
            'run': [game.load_image(f'player_animation/run/run_{i}.png', True)[1] for i in
                    range(count_files('data/player_animation/run'))]
        }

        self.guns = {1: Weapon(40, 20, 14, 5000, 350, 'pistol', None, 1),
                     2: Weapon(85, 30, 30, 5000, 200, 'carabine', None, 2),
                     3: Weapon(320, 30, 10, 6500, 4000, 'rifle', None, 3),
                     4: Weapon(30, 25, 8, 6500, 1500, 'shotgun', None, 4)
                     }

        self.animation_cd = 200
        self.bullets = 50
        self.can_shoot = True
        self.last_shoot_time = 0

        self.weapon = self.guns[2]

    def show_info(self):
        hp_surf = pg.surface.Surface((210, 40))
        hp_surf.fill(pg.color.Color('white'))
        red_sub = pg.Surface((200, 30))
        red_sub.fill(pg.color.Color('red'))
        hp_rect = pg.Surface(((self.hp * 2), 30))
        hp_rect.fill((pg.color.Color('green')))
        hp_surf.blit(red_sub, (5, 5))
        hp_surf.blit(hp_rect, (5, 5))

        game.screen.blit(hp_surf, (30, 30))

        bullet_counter = font_3.render(f"{self.weapon.bullets} / {self.bullets}", True, pg.color.Color('white'))
        game.screen.blit(bullet_counter, (game.WIDTH - 100, 50))

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
        ##shoot block

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
    def __init__(self, x, y, effect_type, shift_needed):
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
    def __init__(self, x, y, angle, speed, shift=0):
        super().__init__()
        self.image = pg.transform.scale(game.load_image('weapon/images/bullet.png'), (4, 4))
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = speed
        angle_degrees = math.degrees(angle)
        # 2. Добавляем смещение в градусах
        shifted_angle_degrees = angle_degrees + shift
        # 3. Преобразуем обратно в радианы
        self.angle = math.radians(shifted_angle_degrees)

    def update(self):
        for block in game.block_group:
            if self.rect.colliderect(block.rect):
                collision, shift = check_collision(self.rect, block.rect)

                effect = Effect(self.rect.x, self.rect.y, 1, (collision, shift))
                game.effect_group.add(effect)
                play_sound('data/weapon/block_hit.wav')
                self.kill()

        for enemy in game.enemy_group:
            if self.rect.colliderect(enemy.rect):
                collision, shift = check_collision(self.rect, enemy.rect)

                effect = Effect(self.rect.x, self.rect.y, 2, (collision, shift))
                play_sound('data/weapon/bullet_sprite_hit.wav')
                game.effect_group.add(effect)

                self.kill()
                if enemy.hp > 0:
                    enemy.hp -= game.player.weapon.damage

        # Движение пули
        self.rect.x += self.speed * math.cos(self.angle)
        self.rect.y += self.speed * math.sin(self.angle)


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
class Entity(pg.sprite.Sprite):
    def __init__(self, x, y, image_type, functional):
        super().__init__()
        self.image = game.load_image(images.get(image_type, 0))  ###pg.Surface((game.cell_size, game.cell_size))
        self.functional = functional
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y

    def update(self):
        game.screen.blit(self.image, game.camera.apply_dest((self.rect.x, self.rect.y)))
        pg.draw.rect(game.screen, (0, 0, 0), game.camera.apply(self), 1)


game = Game(game_parameters, False)
game.run()
