import pygame as pg
from enemy import Enemy
import sys
import math
import os

game_parameters = {
    'resolution': (1920, 1080),
    'difficulty': 'normal'
}

images = {1: 'textures/blocks/mud0.png'}

### comments for effects
# 1 - any block is hitten by bullet
effects = {
    1: ['effects/hit_block/hit_block0.png', 'effects/hit_block/hit_block1.png', 'effects/hit_block/hit_block2.png',
        'effects/hit_block/hit_block3.png', 'effects/hit_block/hit_block4.png']}

level = [[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
         [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
         [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
         [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
         [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
         [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
         [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
         [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
         [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
         [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
         [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
         [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
         [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
         [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
         [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
         [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
         [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
         [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
         [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
         [1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
         [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
         [1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
         [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
         [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
         [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]]


def check_collision(bullet, block):
    bullet_center = bullet.center
    block_center = block.center

    dx = bullet_center[0] - block_center[0]
    dy = bullet_center[1] - block_center[1]
    if abs(dx) > abs(dy):
        if dx > 0:
            return 0
        else:
            return 1
    else:
        if dy > 0:
            return 0
        else:
            return 1


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
    def __init__(self, game_parameters):
        self.game_parameters = game_parameters
        self.WIDTH, self.HEIGHT = self.game_parameters.get('resolution')
        self.cell_size = 40 if self.HEIGHT >= 1600 else 30
        self.G = 5
        self.clock = pg.time.Clock()
        self.screen = pg.display.set_mode((self.WIDTH, self.HEIGHT))
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
            cropped_image = image.subsurface(pg.Rect(18, 18, 68 - 24, 72 - 20))
            # scaled_image = pg.transform.scale(cropped_image, (self.cell_size, self.cell_size * 2))
            return image, cropped_image
        else:
            return pg.transform.scale(image, (self.cell_size, self.cell_size))
        # return image if not player else (
        #     image, pg.transform.scale(image, (self.cell_size *2, self.cell_size * 2)))

    def set_blocks(self):
        rows = len(level)
        cols = len(level[0])
        for y in range(rows):
            for x in range(cols):
                if level[y][x] == 1:
                    block = Block(x * self.cell_size, y * self.cell_size, 1)
                    self.block_group.add(block)

    def handle_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT or event.type == pg.K_ESCAPE:
                self.running = False
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_w:
                    self.player.jump()
                if event.key == pg.K_ESCAPE:
                    self.running = False
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:  # ЛКМ для стрельбы
                mouse_x, mouse_y = pg.mouse.get_pos()
                angle = math.atan2(mouse_y - self.camera.apply(self.player).centery,
                                   mouse_x - self.camera.apply(self.player).centerx)
                bullet = Bullet(self.player.rect.centerx, self.player.rect.centery, angle)
                self.bullet_group.add(bullet)

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

        for effect in self.effect_group:
            effect.render()
        # Отрисовка блоков с учетом камеры
        for block in self.block_group:
            block.update()


        # Отрисовка пуль с учетом камеры
        for bullet in self.bullet_group:
            self.screen.blit(bullet.image, self.camera.apply(bullet))

        # Отрисовка игрока с учетом камеры
        self.player.draw_player(self.camera)
        self.enemy.draw_enemy(self.screen, self.camera)

        self.block_group.update()
        self.bullet_group.update()
        self.enemy_group.update(self.block_group)
        self.player.update()

    def run(self):
        pg.init()
        self.player = Player(self.WIDTH // 2, 100)

        # create and set enemies (must be re-worked)
        self.enemy = Enemy((self.WIDTH // 2 - 200, 300), 'ademan', 100, 1, (game.cell_size, game.cell_size * 2))
        self.enemy_group.add(self.enemy)
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
        self.v_x = 0
        self.v_y = 0
        self.d = 1
        self.m = 1.2
        self.on_ground = False
        self.width = game.cell_size
        self.height = game.cell_size * 2
        self.last_update = pg.time.get_ticks()
        self.cur_frame = 0
        self.cur_anim = 0
        self.animations = {
            'idle': [game.load_image(f'player_animation/idle/idle_{i}.png', True)[1] for i in range(4)],
            'run': [game.load_image(f'player_animation/run/run_{i}.png', True)[1] for i in range(10)]
        }
        self.animation_cd = 200

    def update_move(self, v, d):
        self.v_x = v
        self.d = d

    def update_animation(self):
        if self.v_x == 0:
            a_type = 'idle'
        else:
            a_type = 'run'

        if self.cur_anim != (0 if a_type == 'idle' else 1):
            self.cur_frame = 0
            self.cur_anim = 0 if a_type == 'idle' else 1

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
        # Отрисовка игрока с учетом камеры
        if self.d > 0:
            game.screen.blit(self.image, camera.apply(self))
        elif self.d < 0:
            game.screen.blit(pg.transform.flip(self.image, True, False), camera.apply(self))
        pg.draw.rect(game.screen, pg.color.Color('blue'), camera.apply(self), 1)
        pg.draw.rect(game.screen, pg.color.Color('red'), camera.apply(self.image_rect, True), 1)

    def update(self):
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
    def __init__(self, x, y, effect_type, shift_needed=0):
        super().__init__()
        self.names = effects.get(effect_type)
        self.images = [game.load_image(self.names[i]) for i in range(len(self.names))]
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y
        self.kill_flag = False
        self.frame_index = 0
        self.animation_speed = 0.1
        self.last_update = pg.time.get_ticks()  #
        self.shift = True if shift_needed == 1 else False

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
            game.screen.blit(self.image, game.camera.apply_dest((self.rect.x, self.rect.y) if not self.shift else (
                self.rect.x - game.cell_size, self.rect.y - game.cell_size)))


class Bullet(pg.sprite.Sprite):
    def __init__(self, x, y, angle):
        super().__init__()
        self.image = pg.Surface((5, 5))
        self.image.fill(pg.Color('red'))
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 20
        self.angle = angle

    def update(self):
        for block in game.block_group:
            if self.rect.colliderect(block.rect):
                collission = check_collision(self.rect, block.rect)
                effect = Effect(self.rect.x, self.rect.y, 1, collission)
                game.effect_group.add(effect)
                self.kill()
        for enemy in game.enemy_group:
            if self.rect.colliderect(enemy.rect):
                # collission = check_collision(self.rect, block.rect)
                # effect = Effect(self.rect.x, self.rect.y, 1, collission)
                # game.effect_group.add(effect)
                self.kill()
                print(game.enemy_group)
                if enemy.hp > 0:
                    enemy.hp -= 25
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


game = Game(game_parameters)
game.run()
