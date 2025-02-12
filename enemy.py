import pygame as pg
from functional_file import count_files, play_sound
import sys
import os

G = 3
pg.font.init()
pg.mixer.init()
font_1 = pg.font.Font(None, 16)


def load_image(name, player=False):
    crop_rect = pg.Rect(18, 18, 34, 72 - 18)
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pg.image.load(fullname)
    return image if not player else (image, pg.Surface.subsurface(image, crop_rect))


enemy_animations = {
    'ademan': {
        'idle': [load_image(f'enemy_animation/ademan/idle/idle_ademan{i}.png', True)[1] for i in
                 range(count_files('data/enemy_animation/ademan/idle'))],
        'run': [load_image(f'enemy_animation/ademan/run/run_ademan{i}.png', True)[1] for i in
                range(count_files('data/enemy_animation/ademan/run'))],
        'death': [load_image(f'enemy_animation/ademan/death/death_ademan{i}.png', True)[0] for i in
                  range(count_files('data/enemy_animation/ademan/death'))]
    },
    'dark': {
        'idle': [load_image(f'enemy_animation/dark/idle/dark_idle{i}.png', True)[1] for i in
                 range(count_files('data/enemy_animation/dark/idle'))],
        'run': [load_image(f'enemy_animation/dark/run/dark_run{i}.png', True)[1] for i in
                range(count_files('data/enemy_animation/dark/run'))],
        'death': [load_image(f'enemy_animation/dark/death/dark_death{i}.png', True)[0] for i in
                  range(count_files('data/enemy_animation/dark/death'))]
    }

}


class Enemy(pg.sprite.Sprite):
    def __init__(self, pos, image_type, hp, speed, size, agro_distance=(200, 60), combat_specs=(20, 2000)):
        super().__init__()
        self.x, self.y = pos
        self.width, self.height = size
        self.rect = pg.Rect(*pos, *size)

        self.kill_flag = False
        self.on_ground = False
        self.death_animation_played = False
        self.last_jump = 0
        self.last_attack = 0
        self.damage, self.attack_cd = combat_specs
        self.agro_width, self.agro_height = agro_distance

        self.v_x = 0
        self.v_y = 0
        self.d = 1

        self.animations = enemy_animations.get(image_type)
        self.a_types = {"idle": 0, "run": 1, "death": 2}
        self.image = self.animations.get('idle')[0]
        self.image_rect = self.image.get_rect()
        self.last_update = pg.time.get_ticks()
        self.cur_frame = 0
        self.cur_anim = 0

        self.animation_cd = 200

        self.hp = hp
        self.max_hp = hp
        self.speed = speed

        self.agressive = False
        self.agressive_timer = 0

    def update_move(self, v, d):
        self.v_x = v
        self.d = d

    def jump(self):
        if pg.time.get_ticks() - 500 >= self.last_jump:
            if self.on_ground:
                self.v_y = -15 if self.width <= 40 else -30
                self.on_ground = False
                self.last_jump = pg.time.get_ticks()

    def update_animation(self):
        if self.hp <= 0:
            a_type = 'death'
        elif self.v_x == 0:
            a_type = 'idle'
        elif self.v_x != 0:
            a_type = 'run'

        anim_index = self.a_types[a_type]
        if self.cur_anim != anim_index:
            self.cur_frame = 0
            self.cur_anim = anim_index

        length = len(self.animations[a_type])
        current_time = pg.time.get_ticks()
        if current_time - self.last_update >= self.animation_cd:
            if a_type == 'death' and self.cur_frame + 1 >= length:
                self.death_animation_played = True  # Анимация смерти завершена
            else:
                self.cur_frame = (self.cur_frame + 1) % length
                self.image = self.animations[a_type][self.cur_frame]
            self.last_update = current_time

    def show_info(self, screen, camera):
        red_hp = pg.Surface((self.width, 5))
        if self.hp > 0:
            red_hp.fill(pg.color.Color(153, 40, 8))
            green_hp = pg.Surface((abs((self.hp / self.max_hp)) * self.width, 5))
            green_hp.fill((0, 154, 23))
            red_hp.blit(green_hp, (0, 0))
        else:
            red_hp.fill(pg.color.Color(153, 40, 8))
        screen.blit(red_hp, camera.apply_dest((self.rect.x, self.rect.y - 10)))

    def draw_enemy(self, screen, camera):
        if not self.kill_flag or not self.death_animation_played:
            # screen.blit(font_1.render(f"{self.hp}", True, (3, 255, 4)),
            #             camera.apply_dest((self.rect.x, self.rect.y - 10)))
            self.show_info(screen, camera)
            if self.d > 0:
                screen.blit(pg.transform.scale(self.image, (self.rect.width, self.rect.height)), camera.apply(self))
            elif self.d < 0:
                screen.blit(pg.transform.flip(pg.transform.scale(self.image, (self.rect.width, self.rect.height)), True, False), camera.apply(self))
            pg.draw.rect(screen, pg.color.Color('blue'), camera.apply(self), 1)
            pg.draw.rect(screen, pg.color.Color('red'), camera.apply(self.image_rect, True), 1)

    def attack(self, player):
        if player.hp > 0:
            if self.last_attack + self.attack_cd <= pg.time.get_ticks():

                if player.armor > 0:
                    player.armor -= self.damage
                    player.hp -= self.damage * 0.1
                else:
                    player.hp -= self.damage
                play_sound('data/weapon/player_hit.mp3')
                self.last_attack = pg.time.get_ticks()

    def ai_logic(self, player):
        distance_x = abs(self.rect.centerx - player.rect.centerx)
        distance_y = abs(self.rect.centery - player.rect.centery)

        print(distance_x, distance_y)

        if distance_x <= self.agro_width and distance_y <= self.agro_height:
            self.agressive = True
            self.agressive_timer = pg.time.get_ticks()
        if self.agressive_timer + 10000 <= pg.time.get_ticks():
            self.agressive = False

        if self.agressive:
            if distance_x >= self.agro_width + 50 or distance_y >= self.agro_height + 20:
                self.agressive = False
            if distance_x <= 150:
                self.v_x = 1
                if player.rect.centerx < self.rect.centerx:
                    self.d = -1
                else:
                    self.d = 1

        if distance_x <= 30 and distance_y <= 50:
            self.attack(player)

    def update(self, block_group, player):
        if self.hp <= 0:
            self.kill_flag = True
            self.update_animation()
            if self.death_animation_played:
                self.kill()
            return

        self.image_rect.centerx = self.rect.centerx
        self.image_rect.bottom = self.rect.bottom

        self.v_y += G
        if self.v_y > 20:
            self.v_y = 20

        self.ai_logic(player)

        dx = self.v_x * self.d
        self.rect.x += dx

        collision = False
        for obj in block_group:
            if obj.rect.colliderect(self.rect.x, self.rect.y, self.width, self.height):
                collision = True
                if dx > 0:  # Движение вправо
                    self.rect.right = obj.rect.left
                elif dx < 0:  # Движение влево
                    self.rect.left = obj.rect.right
                self.d *= -1  # Меняем направление
                break

        if self.agressive and collision and self.on_ground:
            if pg.time.get_ticks() - self.last_jump >= 1000:
                self.jump()
                self.last_jump = pg.time.get_ticks()

        self.rect.y += self.v_y

        self.on_ground = False
        for obj in block_group:
            if obj.rect.colliderect(self.rect.x, self.rect.y, self.width, self.height):
                if self.v_y < 0:  # Движение вверх
                    self.v_y = 0
                    self.rect.top = obj.rect.bottom
                elif self.v_y >= 0:  # Движение вниз
                    self.v_y = 0
                    self.rect.bottom = obj.rect.top
                    self.on_ground = True
                break

        self.update_animation()
