import pygame as pg
import sys, os

G = 3
## the animation isnt implemented yet but im working on it. right now im simply removing the image

def load_image(name, player=False, colorkey=None):
    crop_rect = pg.Rect(18, 18, 64 - 24, 72 - 20)
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pg.image.load(fullname)
    return image if not player else (image, pg.Surface.subsurface(image, crop_rect))


enemy_animations = {
    'ademan': {'idle': [load_image(f'enemy_animation/idle/idle_ademan{i}.png', True)[1] for i in range(5)],
               'run': [load_image(f'enemy_animation/run/run_ademan{i}.png', True)[1] for i in range(7)]}
}


class Enemy(pg.sprite.Sprite):
    def __init__(self, pos, image_type, hp, speed, size):
        super().__init__()
        self.x, self.y = pos
        self.width, self.height = size
        self.rect = pg.Rect(self.x, self.y, self.width, self.height)
        # this block for physic and movement
        self.v_x = 0
        self.v_y = 0
        self.d = 1

        self.animations = enemy_animations.get(image_type)
        self.image = load_image(f'enemy_animation/idle/idle_ademan0.png', True)[1]
        self.image_rect = self.image.get_rect()
        self.last_update = pg.time.get_ticks()
        self.cur_frame = 0
        self.cur_anim = 0

        self.animation_cd = 200

        self.hp = hp
        self.speed = speed

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

    def draw_enemy(self, screen, camera):
        if self.hp > 0:
            # self.update(colliding_group)
            if self.d > 0:
                screen.blit(self.image, camera.apply(self))
            elif self.d < 0:
                screen.blit(pg.transform.flip(self.image, True, False), camera.apply(self))
            pg.draw.rect(screen, pg.color.Color('blue'), camera.apply(self), 1)
            pg.draw.rect(screen, pg.color.Color('red'), camera.apply(self.image_rect, True), 1)

    def update(self, block_group):
        if self.hp <= 0:
            self.kill()
            return
        self.image_rect.centerx = self.rect.centerx
        self.image_rect.bottom = self.rect.bottom
        self.v_y += G
        dx = self.v_x * self.d

        if self.v_y > 20:
            self.v_y = 20

        for obj in block_group:
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
        self.on_ground = False
        self.update_animation()
