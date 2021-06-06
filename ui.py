from tkinter import *
import pygame
import random
from os import path


def click_button1():
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

    class Data:

        def __init__(self):
            self.load_data()

        # Загрузка таблицы рекордов

        def load_data(self):
            self.dir = path.dirname(__file__)
            with open(path.join(self.dir, HS_FILE), 'w') as f:
                try:
                    self.high_score = int(f.read())
                except:
                    self.high_score = 0

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

    # определяет спрайты для пуль (лазеров)
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


def click_button2():
    import random
    import math
    import arcade
    import os

    from typing import cast

    STARTING_ASTEROID_COUNT = 3
    SCALE = 0.5
    OFFSCREEN_SPACE = 300
    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 600
    SCREEN_TITLE = "Asteroid Smasher"
    LEFT_LIMIT = -OFFSCREEN_SPACE
    RIGHT_LIMIT = SCREEN_WIDTH + OFFSCREEN_SPACE
    BOTTOM_LIMIT = -OFFSCREEN_SPACE
    TOP_LIMIT = SCREEN_HEIGHT + OFFSCREEN_SPACE

    # Спрайт, который задает угол наклона к направлению своего движения
    class TurningSprite(arcade.Sprite):
        def update(self):
            # Перемещает спрайт
            super().update()
            self.angle = math.degrees(math.atan2(self.change_y, self.change_x))

    # Спрайт, отвечающий за космический корабль
    # Унаследовано от arcade.Sprite
    class ShipSprite(arcade.Sprite):
        def __init__(self, filename, scale):
            # Устанавливает космический корабль

            # Вызывает конструктор родительского спрайта
            super().__init__(filename, scale)

            # Информация о том, куда мы движемся
            # Угол автоматический из родиительского спрайта
            self.thrust = 0
            self.speed = 0
            self.max_speed = 4
            self.drag = 0.05
            self.respawning = 0

            # Отметка о том что мы респавнимся
            self.respawn()

        def respawn(self):
            # Вызывается когда мы умираем и необходимо создать новый корабль
            # 'respawning' - это таймер неуязвимости

            # Если мы находимся в середине возрождения, это не ноль.
            self.respawning = 1
            self.center_x = SCREEN_WIDTH / 2
            self.center_y = SCREEN_HEIGHT / 2
            self.angle = 0

        def update(self):
            # Обновляет нашу позицию и другие сведения.

            if self.respawning:
                self.respawning += 1
                self.alpha = self.respawning
                if self.respawning > 250:
                    self.respawning = 0
                    self.alpha = 255
            if self.speed > 0:
                self.speed -= self.drag
                if self.speed < 0:
                    self.speed = 0

            if self.speed < 0:
                self.speed += self.drag
                if self.speed > 0:
                    self.speed = 0

            self.speed += self.thrust
            if self.speed > self.max_speed:
                self.speed = self.max_speed
            if self.speed < -self.max_speed:
                self.speed = -self.max_speed

            self.change_x = -math.sin(math.radians(self.angle)) * self.speed
            self.change_y = math.cos(math.radians(self.angle)) * self.speed

            self.center_x += self.change_x
            self.center_y += self.change_y

            # If the ship goes off-screen, move it to the other side of the window
            if self.right < 0:
                self.left = SCREEN_WIDTH

            if self.left > SCREEN_WIDTH:
                self.right = 0

            if self.bottom < 0:
                self.top = SCREEN_HEIGHT

            if self.top > SCREEN_HEIGHT:
                self.bottom = 0

            # Вызывает родительский класс
            super().update()

    # Спрайт отвечающий за астероиды
    class AsteroidSprite(arcade.Sprite):

        def __init__(self, image_file_name, scale):
            super().__init__(image_file_name, scale=scale)
            self.size = 0

        def update(self):
            # Двигает астероиды
            super().update()
            if self.center_x < LEFT_LIMIT:
                self.center_x = RIGHT_LIMIT
            if self.center_x > RIGHT_LIMIT:
                self.center_x = LEFT_LIMIT
            if self.center_y > TOP_LIMIT:
                self.center_y = BOTTOM_LIMIT
            if self.center_y < BOTTOM_LIMIT:
                self.center_y = TOP_LIMIT

    # Основной класс приложения
    class MyGame(arcade.Window):

        def __init__(self):
            super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

            file_path = os.path.dirname(os.path.abspath(__file__))
            os.chdir(file_path)

            self.frame_count = 0

            self.game_over = False

            # Список спрайтов
            self.player_sprite_list = arcade.SpriteList()
            self.asteroid_list = arcade.SpriteList()
            self.bullet_list = arcade.SpriteList()
            self.ship_life_list = arcade.SpriteList()

            # Настройки игрока
            self.score = 0
            self.player_sprite = None
            self.lives = 3

            # Звуки
            self.laser_sound = arcade.load_sound(":resources:sounds/hurt5.wav")
            self.hit_sound1 = arcade.load_sound(":resources:sounds/explosion1.wav")
            self.hit_sound2 = arcade.load_sound(":resources:sounds/explosion2.wav")
            self.hit_sound3 = arcade.load_sound(":resources:sounds/hit1.wav")
            self.hit_sound4 = arcade.load_sound(":resources:sounds/hit2.wav")

        # Настраивает игру и инициализирует переменные
        def start_new_game(self):
            self.frame_count = 0
            self.game_over = False

            # Список спрайтов
            self.player_sprite_list = arcade.SpriteList()
            self.asteroid_list = arcade.SpriteList()
            self.bullet_list = arcade.SpriteList()
            self.ship_life_list = arcade.SpriteList()

            # Настройки игрока
            self.score = 0
            self.player_sprite = ShipSprite(":resources:images/space_shooter/playerShip1_orange.png", SCALE)
            self.player_sprite_list.append(self.player_sprite)
            self.lives = 3

            # Настройки жизней игрока
            cur_pos = 10
            for i in range(self.lives):
                life = arcade.Sprite(":resources:images/space_shooter/playerLife1_orange.png", SCALE)
                life.center_x = cur_pos + life.width
                life.center_y = life.height
                cur_pos += life.width
                self.ship_life_list.append(life)

            # Делает астероиды
            image_list = (":resources:images/space_shooter/meteorGrey_big1.png",
                          ":resources:images/space_shooter/meteorGrey_big2.png",
                          ":resources:images/space_shooter/meteorGrey_big3.png",
                          ":resources:images/space_shooter/meteorGrey_big4.png")
            for i in range(STARTING_ASTEROID_COUNT):
                image_no = random.randrange(4)
                enemy_sprite = AsteroidSprite(image_list[image_no], SCALE)
                enemy_sprite.guid = "Asteroid"

                enemy_sprite.center_y = random.randrange(BOTTOM_LIMIT, TOP_LIMIT)
                enemy_sprite.center_x = random.randrange(LEFT_LIMIT, RIGHT_LIMIT)

                enemy_sprite.change_x = random.random() * 2 - 1
                enemy_sprite.change_y = random.random() * 2 - 1

                enemy_sprite.change_angle = (random.random() - 0.5) * 2
                enemy_sprite.size = 4
                self.asteroid_list.append(enemy_sprite)

        # Рендеринг
        def on_draw(self):

            # Эта команда должна произойти до того, как мы начнем рисовать
            arcade.start_render()

            # Отрисовка всех спрайтов
            self.asteroid_list.draw()
            self.ship_life_list.draw()
            self.bullet_list.draw()
            self.player_sprite_list.draw()

            # Помещаем текст на экран
            output = f"Score: {self.score}"
            arcade.draw_text(output, 10, 70, arcade.color.WHITE, 13)

            output = f"Asteroid Count: {len(self.asteroid_list)}"
            arcade.draw_text(output, 10, 50, arcade.color.WHITE, 13)

        # События по нажатию клавиш
        def on_key_press(self, symbol, modifiers):

            # Вызывается всякий раз, когда нажимается клавиша.
            # Стреляет, если игрок нажмет пробел, и мы не респавнимся.
            if not self.player_sprite.respawning and symbol == arcade.key.SPACE:
                bullet_sprite = TurningSprite(":resources:images/space_shooter/laserBlue01.png", SCALE)
                bullet_sprite.guid = "Bullet"

                bullet_speed = 13
                bullet_sprite.change_y = \
                    math.cos(math.radians(self.player_sprite.angle)) * bullet_speed
                bullet_sprite.change_x = \
                    -math.sin(math.radians(self.player_sprite.angle)) \
                    * bullet_speed

                bullet_sprite.center_x = self.player_sprite.center_x
                bullet_sprite.center_y = self.player_sprite.center_y
                bullet_sprite.update()

                self.bullet_list.append(bullet_sprite)

                arcade.play_sound(self.laser_sound)

            if symbol == arcade.key.LEFT:
                self.player_sprite.change_angle = 3
            elif symbol == arcade.key.RIGHT:
                self.player_sprite.change_angle = -3
            elif symbol == arcade.key.UP:
                self.player_sprite.thrust = 0.15
            elif symbol == arcade.key.DOWN:
                self.player_sprite.thrust = -.2

        def on_key_release(self, symbol, modifiers):
            # Вызывается при отпускании клавиш
            if symbol == arcade.key.LEFT:
                self.player_sprite.change_angle = 0
            elif symbol == arcade.key.RIGHT:
                self.player_sprite.change_angle = 0
            elif symbol == arcade.key.UP:
                self.player_sprite.thrust = 0
            elif symbol == arcade.key.DOWN:
                self.player_sprite.thrust = 0

        # Разделяет астероид на обломки
        def split_asteroid(self, asteroid: AsteroidSprite):
            x = asteroid.center_x
            y = asteroid.center_y
            self.score += 1

            if asteroid.size == 4:
                for i in range(3):
                    image_no = random.randrange(2)
                    image_list = [":resources:images/space_shooter/meteorGrey_med1.png",
                                  ":resources:images/space_shooter/meteorGrey_med2.png"]

                    enemy_sprite = AsteroidSprite(image_list[image_no],
                                                  SCALE * 1.5)

                    enemy_sprite.center_y = y
                    enemy_sprite.center_x = x
                    enemy_sprite.change_x = random.random() * 2.5 - 1.25
                    enemy_sprite.change_y = random.random() * 2.5 - 1.25

                    enemy_sprite.change_angle = (random.random() - 0.5) * 2
                    enemy_sprite.size = 3

                    self.asteroid_list.append(enemy_sprite)
                    self.hit_sound1.play()

            elif asteroid.size == 3:
                for i in range(3):
                    image_no = random.randrange(2)
                    image_list = [":resources:images/space_shooter/meteorGrey_small1.png",
                                  ":resources:images/space_shooter/meteorGrey_small2.png"]

                    enemy_sprite = AsteroidSprite(image_list[image_no],
                                                  SCALE * 1.5)

                    enemy_sprite.center_y = y
                    enemy_sprite.center_x = x

                    enemy_sprite.change_x = random.random() * 3 - 1.5
                    enemy_sprite.change_y = random.random() * 3 - 1.5

                    enemy_sprite.change_angle = (random.random() - 0.5) * 2
                    enemy_sprite.size = 2

                    self.asteroid_list.append(enemy_sprite)
                    self.hit_sound2.play()

            elif asteroid.size == 2:
                for i in range(3):
                    image_no = random.randrange(2)
                    image_list = [":resources:images/space_shooter/meteorGrey_tiny1.png",
                                  ":resources:images/space_shooter/meteorGrey_tiny2.png"]

                    enemy_sprite = AsteroidSprite(image_list[image_no],
                                                  SCALE * 1.5)

                    enemy_sprite.center_y = y
                    enemy_sprite.center_x = x

                    enemy_sprite.change_x = random.random() * 3.5 - 1.75
                    enemy_sprite.change_y = random.random() * 3.5 - 1.75

                    enemy_sprite.change_angle = (random.random() - 0.5) * 2
                    enemy_sprite.size = 1

                    self.asteroid_list.append(enemy_sprite)
                    self.hit_sound3.play()

            elif asteroid.size == 1:
                self.hit_sound4.play()

        def on_update(self, x):
            # Перемещает все

            self.frame_count += 1

            if not self.game_over:
                self.asteroid_list.update()
                self.bullet_list.update()
                self.player_sprite_list.update()

                for bullet in self.bullet_list:

                    # Функция check_for_collision_with_list позволяет увидеть,
                    # если спрайт наталкивается на другой спрайт из списка.

                    asteroids = arcade.check_for_collision_with_list(bullet, self.asteroid_list)

                    for asteroid in asteroids:
                        self.split_asteroid(
                            cast(AsteroidSprite, asteroid))  # expected AsteroidSprite, got Sprite instead
                        asteroid.remove_from_sprite_lists()
                        bullet.remove_from_sprite_lists()

                    # Удаляет пулю, если она выходит за пределы экрана
                    size = max(bullet.width, bullet.height)
                    if bullet.center_x < 0 - size:
                        bullet.remove_from_sprite_lists()
                    if bullet.center_x > SCREEN_WIDTH + size:
                        bullet.remove_from_sprite_lists()
                    if bullet.center_y < 0 - size:
                        bullet.remove_from_sprite_lists()
                    if bullet.center_y > SCREEN_HEIGHT + size:
                        bullet.remove_from_sprite_lists()

                if not self.player_sprite.respawning:

                    # Функция check_for_collision_with_list позволяет увидеть,
                    # если спрайт наталкивается на другой спрайт из списка.

                    asteroids = arcade.check_for_collision_with_list(self.player_sprite, self.asteroid_list)
                    if len(asteroids) > 0:
                        if self.lives > 0:
                            self.lives -= 1
                            self.player_sprite.respawn()
                            self.split_asteroid(cast(AsteroidSprite, asteroids[0]))
                            asteroids[0].remove_from_sprite_lists()
                            self.ship_life_list.pop().remove_from_sprite_lists()
                            print("Crash")
                        else:
                            self.game_over = True
                            print("Game over")

    def main():

        # Старт игры
        window = MyGame()
        window.start_new_game()
        arcade.run()

    if __name__ == "__main__":
        main()


root = Tk()
root.title("Games")
root.geometry("300x250")

btn1 = Button(text="Game 1", background="#555", foreground="#ccc",
             padx="20", pady="8", font="16", command=click_button1)
btn1.pack()

btn2 = Button(text="Game 2", background="#555", foreground="#ccc",
             padx="20", pady="8", font="16", command=click_button2)
btn2.pack()


root.mainloop()