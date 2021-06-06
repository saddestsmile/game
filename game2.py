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
                    self.split_asteroid(cast(AsteroidSprite, asteroid))  # expected AsteroidSprite, got Sprite instead
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
