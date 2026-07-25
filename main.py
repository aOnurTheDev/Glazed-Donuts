from time import sleep
from random import randint
from pygame import *
import json

mixer.init()

win_width = 1050
win_height = 700
window = display.set_mode((win_width, win_height))
display.set_caption("Glazed Donuts")
logo = "logo.png"
logoresm = image.load(logo)
display.set_icon(logoresm)

font.init()
font1 = font.Font(None, 36)

finish = False
run = True
clock = time.Clock()
skor = 0

enemyres = "spike.png"
playres = "resim.png"
ikili = "2li.png"
uclu = "3lu.png"

eski_rekor = 0
level = 0

song = "onenon.mp3"
mixer.music.load(song)
mixer.music.play(-1)

try:
    with open('kayit.json', 'r') as file:
        data = json.load(file)
        eski_rekor = data.get("rekor", 0)
        level = data.get("level", 1)
except (FileNotFoundError, json.JSONDecodeError, KeyError):
    eski_rekor = 0
    level = 1
    with open('kayit.json', 'w') as file:
        json.dump({"rekor": 0, "level": 1}, file, indent=4)

class GameSprite(sprite.Sprite):
    def __init__(self, player_image, player_x, player_y, size_x, size_y, player_speed):
        super().__init__()
        self.speed = player_speed
        self.image = transform.scale(image.load(player_image), (size_x, size_y))
        self.rect = self.image.get_rect()
        self.rect.x = player_x
        self.rect.y = player_y

    def reset(self):
        window.blit(self.image, (self.rect.x, self.rect.y))

class Platform(sprite.Sprite):
    def __init__(self, x, y, width, height, color=(0, 255, 0)):
        super().__init__()
        self.image = Surface((width, height))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def reset(self):
        window.blit(self.image, (self.rect.x, self.rect.y))

class Player(GameSprite):
    def __init__(self, player_image, player_x, player_y, size_x, size_y, player_speed):
        super().__init__(player_image, player_x, player_y, size_x, size_y, player_speed)
        self.y_vel = 0
        self.is_jump = True
        self.gravity = 1
        self.jump_power = -15

    def update(self, platforms):
        keys = key.get_pressed()
        self.y_vel += self.gravity
        self.rect.y += self.y_vel
        hit_platforms = sprite.spritecollide(self, platforms, False)
        for plat in hit_platforms:
            if self.y_vel > 0:
                self.rect.bottom = plat.rect.top
                self.y_vel = 0
                self.is_jump = False
        if not self.is_jump:
            if keys[K_SPACE]:
                self.y_vel = self.jump_power
                self.is_jump = True

    def reset_position(self):
        self.rect.x = 170
        self.rect.y = 450
        self.y_vel = 0
        self.is_jump = True

class Enemy(GameSprite):
    def __init__(self, player_image, player_x, player_y, size_x, size_y, player_speed):
        super().__init__(player_image, player_x, player_y, size_x, size_y, player_speed)
        kacli = randint(1, 3)
        if kacli == 2:
            self.image = transform.scale(image.load(ikili), (100, 50))
        elif kacli == 3:
            self.image = transform.scale(image.load(uclu), (150, 50))
        elif kacli == 1:
            self.image = transform.scale(image.load(enemyres), (50, 50))
        self.rect = self.image.get_rect()
        self.rect.x = player_x
        self.rect.y = 500 - self.rect.height

    def update(self):
        global skor
        self.rect.x -= self.speed
        if self.rect.right <= 0:
            skor += 1
            self.kill()

player = Player(playres, 170, 450, 50, 50, 7)

platforms = sprite.Group()
platforms.add(Platform(0, 500, win_width, 400, "#023047"))

enemies = sprite.Group()

SPAWN_ENEMY = USEREVENT + 1
time.set_timer(SPAWN_ENEMY, 1200)

while run:
    for e in event.get():
        if e.type == QUIT:
            run = False
        elif e.type == SPAWN_ENEMY and not finish:
            enemhiz = 10 + (2 * level)
            new_enemy = Enemy(enemyres, win_width, 450, 50, 50, enemhiz)
            enemies.add(new_enemy)
        elif e.type == KEYDOWN:
            if e.key == K_r:
                finish = False
                enemies.empty()
                player.reset_position()
                skor = 0
                mixer.music.play(-1)
            elif e.key == K_p:
                skor += 999

    if not finish:
        window.fill((30, 30, 50))
        if skor >= 25:
            level += 1
            with open('kayit.json', 'w') as file:
                json.dump({"level": level}, file, indent=4)
            finish = False
            enemies.empty()
            player.reset_position()
            skor = 0
            mixer.music.stop()
            buyuk_font = font.Font(None, 72)
            seviyetext = buyuk_font.render(f"New Level: {level}", True, (255, 0, 0))
            text_rect = seviyetext.get_rect(center=(win_width / 2, win_height / 2))
            window.blit(seviyetext, text_rect)
            display.update()
            sleep(2)
            mixer.music.play(-1)

        if sprite.spritecollide(player, enemies, False):
            finish = True
            mixer.music.stop()


        if skor > eski_rekor:
            eski_rekor = skor
            with open('kayit.json', 'w') as file:
                json.dump({"rekor": eski_rekor}, file, indent=4)

        lost_text = font1.render(f"Skor: {skor}", True, (255, 255, 255))
        window.blit(lost_text, (10, 10))
        rekor_text = font1.render(f"Level: {level}", True, (255, 255, 255))
        window.blit(rekor_text, (10, 32))

        skor_rect = lost_text.get_rect(topleft=(10, 10))
        rekor_rect = rekor_text.get_rect(topleft=(10, 32))
        box_left = skor_rect.left - 5
        box_top = skor_rect.top - 5
        box_right = max(skor_rect.right, rekor_rect.right) + 5
        box_bottom = rekor_rect.bottom + 5
        box_width = box_right - box_left
        box_height = box_bottom - box_top
        draw.rect(window, (255, 255, 255), (box_left, box_top, box_width, box_height), 2)

        platforms.draw(window)
        player.update(platforms)
        player.reset()
        enemies.update()
        enemies.draw(window)

    display.update()
    clock.tick(60)