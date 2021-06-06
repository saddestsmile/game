import pygame
import random
from os import path


# Директории, в которых хранятся изображения и звуки, используемые в игре
img_dir = path.join(path.dirname(__file__), 'img')
snd_dir = path.join(path.dirname(__file__), 'snd')

WIDTH = 480
HEIGHT = 600
FPS = 60
POWERUP_TIME = 3000
HS_FILE = "high_score.txt"

# Задаем цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# Создаем игру и окно
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Asteroids!")
clock = pygame.time.Clock()

font_name = pygame.font.match_font('arial')


# class Data:

#    def __init__(self):
#        self.load_data()
# Загрузка таблицы рекордов

#   def load_data(self):
#       self.dir = path.dirname(__file__)
#       with open(path.join(self.dir, HS_FILE), 'w') as f:
#           try:
#               self.high_score = int(f.read())
#           except:
#               self.high_score = 0


# Рендеринг текста
def draw_text(surf, text, size, x, y):
    # Выбор кроссплатформенного шрифта для отображения счета
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, WHITE)
    # True обозначает шрифт, который нужно сглаживать.
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)


def newmob():
    m = Mob()
    all_sprites.add(m)
    mobs.add(m)


# Здоровье
def draw_shield_bar(surf, x, y, pct):
    if pct < 0:
        pct = 0
    bar_length = 100
    bar_height = 10
    fill = (pct / 100) * bar_length
    outline_rect = pygame.Rect(x, y, bar_length, bar_height)
    fill_rect = pygame.Rect(x, y, fill, bar_height)
    pygame.draw.rect(surf, GREEN, fill_rect)
    pygame.draw.rect(surf, WHITE, outline_rect, 2)


# Жизни
def draw_lives(surf, x, y, lives, img):
    for i in range(lives):
        img_rect = img.get_rect()
        img_rect.x = x + 30 * i
        img_rect.y = y
        surf.blit(img, img_rect)


# Стартовый экран
def show_go_screen():
    screen.blit(background, background_rect)
    draw_text(screen, "ASTEROIDS!", 64, WIDTH / 2, HEIGHT / 4)
    draw_text(screen, "Arrow keys move, Space to fire", 22,
              WIDTH / 2, HEIGHT / 2)
    draw_text(screen, "Press any key to begin", 18, WIDTH / 2, HEIGHT * 2 / 3)
    draw_text(screen, "Press escape to exit", 17, WIDTH / 2, HEIGHT * 3 / 4)
    draw_text(screen, "Press backspace to pause", 17, WIDTH / 2, HEIGHT * 4 / 5)
    pygame.display.flip()
    waiting = True
    while waiting:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYUP:
                waiting = False


# Экран при проигрыше
def game_over_screen():
    screen.blit(background, background_rect)
    draw_text(screen, "Game over!", 64, WIDTH / 2, HEIGHT / 4)
    message = 'Your score: %d' % score
    draw_text(screen, message, 22, WIDTH / 2, HEIGHT / 2)
    draw_text(screen, "Press any key to begin new game", 18, WIDTH / 2, HEIGHT * 3 / 4)
    pygame.display.flip()
    waiting = True
    while waiting:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYUP:
                waiting = False


# Экран паузы
def pause_screen():
    screen.blit(background, background_rect)
    draw_text(screen, "Paused", 64, WIDTH / 2, HEIGHT / 4)
    message = 'Your score: %d' % score
    draw_text(screen, message, 22,
              WIDTH / 2, HEIGHT / 2)
    draw_text(screen, "Press SHIFT to continue", 18, WIDTH / 2, HEIGHT * 3 / 4)
    pygame.display.flip()
    waiting = True
    while waiting:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYUP:
                waiting = False


# Пауза
def pause():
    paused = True
    while paused:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        pause_screen()

        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_LSHIFT]:
            paused = False

        pygame.display.update()
        clock.tick(FPS)


class Explosion(pygame.sprite.Sprite):
    def __init__(self, center, size):
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.image = explosion_anim[self.size][0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 50

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(explosion_anim[self.size]):
                self.kill()
            else:
                center = self.rect.center
                self.image = explosion_anim[self.size][self.frame]
                self.rect = self.image.get_rect()
                self.rect.center = center


# определяет спрайты игрока
class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(player_img, (50, 38))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.radius = 20
        # pygame.draw.circle(self.image, RED, self.rect.center, self.radius)
        self.rect.centerx = WIDTH / 2
        self.rect.bottom = HEIGHT - 10
        self.speedx = 0
        self.shield = 100
        self.shoot_delay = 250
        self.last_shot = pygame.time.get_ticks()
        self.lives = 3
        self.hidden = False
        self.hide_timer = pygame.time.get_ticks()
        self.power = 1
        self.power_time = pygame.time.get_ticks()

# Сохранения
        # self.save_data = Save()
        # self.high_scores = HighScore(self.save_data.get('hs'))
        # self.save_data.add('hs', {})
        # print(self.save_data.get('hs'))

    def update(self):
        # тайм-аут для бонусов
        if self.power >= 2 and pygame.time.get_ticks() - self.power_time > POWERUP_TIME:
            self.power -= 1
            self.power_time = pygame.time.get_ticks()

        # показать
        if self.hidden and pygame.time.get_ticks() - self.hide_timer > 1000:
            self.hidden = False
            self.rect.centerx = WIDTH / 2
            self.rect.bottom = HEIGHT - 10
        # Управление игроком
        self.speedx = 0
        # по умолчанию делает игрока статичным на экране,
        # тогда мы должны проверить, выполняется ли обработка событий для клавиш со стрелками

        # вернет список клавиш, которые были нажаты в этот момент
        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_LEFT]:
            self.speedx = -5
        if keystate[pygame.K_RIGHT]:
            self.speedx = 5

        # выпускает лазеры по нажатию пробела
        if keystate[pygame.K_SPACE]:
            self.shoot()
        self.rect.x += self.speedx

        # проверяет границы слева и справа
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0

        # Пауза по нажатию backspace
        # keystate = pygame.key.get_pressed()
        if keystate[pygame.K_BACKSPACE]:
            pause()

    def shoot(self):
        # чтобы указать пуле, где появиться
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            if self.power == 1:
                bullet = Bullet(self.rect.centerx, self.rect.top)
                all_sprites.add(bullet)
                bullets.add(bullet)
                shoot_sound.play()
            if self.power == 2:
                bullet1 = Bullet(self.rect.left, self.rect.centery)
                bullet2 = Bullet(self.rect.right, self.rect.centery)
                all_sprites.add(bullet1)
                all_sprites.add(bullet2)
                bullets.add(bullet1)
                bullets.add(bullet2)
                shoot_sound.play()

            if self.power >= 3:
                bullet1 = Bullet(self.rect.left, self.rect.centery)
                bullet2 = Bullet(self.rect.right, self.rect.centery)
                missile1 = Missile(self.rect.centerx, self.rect.top)  # ракета стреляет по центру от игрока
                all_sprites.add(bullet1)
                all_sprites.add(bullet2)
                all_sprites.add(missile1)
                bullets.add(bullet1)
                bullets.add(bullet2)
                bullets.add(missile1)
                shoot_sound.play()
                missile_sound.play()

    def powerup(self):
        self.power += 1
        self.power_time = pygame.time.get_ticks()

    def hide(self):
        self.hidden = True
        self.hide_timer = pygame.time.get_ticks()
        self.rect.center = (WIDTH / 2, HEIGHT + 200)


# определяет врагов
class Mob(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image_orig = random.choice(meteor_images)
        self.image_orig.set_colorkey(BLACK)
        self.image = self.image_orig.copy()
        self.rect = self.image.get_rect()
        self.radius = int(self.rect.width * .85 / 2)
        # pygame.draw.circle(self.image, RED, self.rect.center, self.radius)
        self.rect.x = random.randrange(WIDTH - self.rect.width)
        self.rect.y = random.randrange(-150, -100)

        # рандомизируем скорость астероидов
        self.speedy = random.randrange(1, 8)
        self.speedx = random.randrange(-3, 3)

        # добавляем вращения астероидам
        self.rot = 0
        self.rot_speed = random.randrange(-8, 8)
        self.last_update = pygame.time.get_ticks()
        # время, когда должно произойти вращение

    def rotate(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > 50:  # в милисекундах
            self.last_update = now
            self.rot = (self.rot + self.rot_speed) % 360
            new_image = pygame.transform.rotate(self.image_orig, self.rot)
            old_center = self.rect.center
            self.image = new_image
            self.rect = self.image.get_rect()
            self.rect.center = old_center

    def update(self):
        self.rotate()
        self.rect.x += self.speedx
        self.rect.y += self.speedy
        if self.rect.top > HEIGHT + 10 or self.rect.left < -25 or self.rect.right > WIDTH + 20:
            self.rect.x = random.randrange(0, WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speedy = random.randrange(1, 8)
            # для рандомизации скорости моба


# определяет спрайты для бонусов
class Pow(pygame.sprite.Sprite):
    def __init__(self, center):
        pygame.sprite.Sprite.__init__(self)
        self.type = random.choice(['shield', 'gun'])
        self.image = powerup_images[self.type]
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        # помещает лазер в соответствии с текущей позицией игрока
        self.rect.center = center
        self.speedy = 2

    def update(self):
        # должен появиться прямо перед игроком
        self.rect.y += self.speedy
        # убивает спрайт после того, как он переместится за верхнюю границу
        if self.rect.top > HEIGHT:
            self.kill()


# определяет спрайты для пуль игрока
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = bullet_img
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        # помещает пулю в соответствии с текущей позицией игрока
        self.rect.bottom = y
        self.rect.centerx = x
        self.speedy = -10

    def update(self):
        # должен появиться прямо перед игроком
        self.rect.y += self.speedy
        # убивает спрайт после того, как он переместится за верхнюю границу
        if self.rect.bottom < 0:
            self.kill()


# определяет спрайты для ракет
class Missile(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = missile_img
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speedy = -10

    def update(self):
        # должны появиться прямо перед игроком
        self.rect.y += self.speedy
        if self.rect.bottom < 0:
            self.kill()


# Загрузка всей игровой графики
background = pygame.image.load(path.join(img_dir, "background1.png")).convert()
background_rect = background.get_rect()
player_img = pygame.image.load(path.join(img_dir, "spiked ship 3. small.blue_.PNG"))
player_mini_img = pygame.transform.scale(player_img, (25, 19))
player_mini_img.set_colorkey(BLACK)
bullet_img = pygame.image.load(path.join(img_dir, "laserRed16.png")).convert()
missile_img = pygame.image.load(path.join(img_dir, 'missile.png')).convert_alpha()
meteor_images = []
meteor_list = ['Asteroid2.png', 'asteroid-big.png', 'asteroid-small.png']

for img in meteor_list:
    meteor_images.append(pygame.image.load(path.join(img_dir, img)).convert())

# взрыв метеора
explosion_anim = {}
explosion_anim['lg'] = []
explosion_anim['sm'] = []
explosion_anim['player'] = []
for i in range(9):
    filename = 'regularExplosion0{}.png'.format(i)
    img = pygame.image.load(path.join(img_dir, filename)).convert()
    img.set_colorkey(BLACK)
    # изменить размер взрыва
    img_lg = pygame.transform.scale(img, (75, 75))
    explosion_anim['lg'].append(img_lg)
    img_sm = pygame.transform.scale(img, (32, 32))
    explosion_anim['sm'].append(img_sm)
    # взрыв игрока
    filename = 'sonicExplosion0{}.png'.format(i)
    img = pygame.image.load(path.join(img_dir, filename)).convert()
    img.set_colorkey(BLACK)
    explosion_anim['player'].append(img)

# изображения бонусов
powerup_images = {}
powerup_images['shield'] = pygame.image.load(path.join(img_dir, 'shield_gold.png'))
powerup_images['gun'] = pygame.image.load(path.join(img_dir, 'bolt_gold.png'))


# Загрузка мелодий игры
shoot_sound = pygame.mixer.Sound(path.join(snd_dir, 'pew.wav'))
missile_sound = pygame.mixer.Sound(path.join(snd_dir, 'rocket.ogg'))
shield_sound = pygame.mixer.Sound(path.join(snd_dir, 'pow5.wav'))
power_sound = pygame.mixer.Sound(path.join(snd_dir, 'pow4.wav'))
expl_sounds = []
for snd in ['expl3.wav', 'expl6.wav']:
    expl_sounds.append(pygame.mixer.Sound(path.join(snd_dir, snd)))
# основная фоновая музыка
pygame.mixer.music.load(path.join(snd_dir, 'techno_stargazev2.1loop.ogg'))
pygame.mixer.music.set_volume(0.4)
player_die_sound = pygame.mixer.Sound(path.join(snd_dir, 'rumble1.ogg'))
pygame.mixer.music.play(loops=-1)


# Цикл игры
menu_display = True
running = True
while running:
    if menu_display:
        show_go_screen()
        pygame.time.wait(300)

        # останавливает музыку меню
        pygame.mixer.music.stop()
        # включают музыку геймплея
        pygame.mixer.music.load(path.join(snd_dir, 'tgfcoder-FrozenJam-SeamlessLoop.ogg'))
        # бесконечный цикл музыки геймплея
        pygame.mixer.music.play(-1)

        menu_display = False

        # группирует все спрайты вместе для простоты обновления
        all_sprites = pygame.sprite.Group()
        player = Player()
        all_sprites.add(player)

        # создает группу мобов
        mobs = pygame.sprite.Group()
        for i in range(8):
            newmob()

        # группа для пуль
        bullets = pygame.sprite.Group()
        powerups = pygame.sprite.Group()

        # Переменная для счета
        score = 0

    # Держим цикл на правильной скорости
    clock.tick(FPS)
    # Ввод процесса (события)
    for event in pygame.event.get():
        # следит за закрытием окна
        if event.type == pygame.QUIT:
            running = False

            # ESC для выхода из игры
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

    # Обновление
    all_sprites.update()

    # Проверка попала ли пуля в моб
    hits = pygame.sprite.groupcollide(mobs, bullets, True, True)
    for hit in hits:
        # начисляет разное кол-во очков за попадание в большой и маленький меторы
        score += 50 - hit.radius
        random.choice(expl_sounds).play()
        # m = Mob()
        # all_sprites.add(m)
        # mobs.add(m)
        expl = Explosion(hit.rect.center, 'lg')
        all_sprites.add(expl)
        if random.random() > 0.9:
            pow = Pow(hit.rect.center)
            all_sprites.add(pow)
            powerups.add(pow)
        newmob()
    # указанный выше цикл снова создаст количество убитых мобов

    #  Проверка не ударил ли моб игрока
    hits = pygame.sprite.spritecollide(player, mobs, True, pygame.sprite.collide_circle)
    # возвращает список, True заставляет элемент моба исчезнуть
    for hit in hits:
        player.shield -= hit.radius * 2
        expl = Explosion(hit.rect.center, 'sm')
        all_sprites.add(expl)
        newmob()
        if player.shield <= 0:
            player_die_sound.play()
            death_explosion = Explosion(player.rect.center, 'player')
            all_sprites.add(death_explosion)
            player.hide()
            player.lives -= 1
            player.shield = 100

# Проверка получения бонуса игроком
    hits = pygame.sprite.spritecollide(player, powerups, True)
    for hit in hits:
        if hit.type == 'shield':
            player.shield += random.randrange(10, 30)
            if player.shield >= 100:
                player.shield = 100
                shield_sound.play()
        if hit.type == 'gun':
            player.powerup()
            power_sound.play()

    # Если игрок умер, игра окончена
    if player.lives == 0 and not death_explosion.alive():
        running = False
        # menu_display = True
        game_over_screen()

    # Рендеринг
    screen.fill(BLACK)
    screen.blit(background, background_rect)

    all_sprites.draw(screen)
    draw_text(screen, str(score), 18, WIDTH / 2, 10)  # 10px вниз от экрана
    draw_shield_bar(screen, 5, 5, player.shield)
    # Рисуем жизни
    draw_lives(screen, WIDTH - 100, 5, player.lives, player_mini_img)
    # После отрисовки всего переворачиваем экран
    pygame.display.flip()

    # Esc для выхода из игры
    keys = pygame.key.get_pressed()
    if keys[pygame.K_ESCAPE]:
        pygame.quit()

pygame.quit()
