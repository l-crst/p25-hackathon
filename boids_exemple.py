"""
simplest possible starting code with one motionless boid
display a single object, inert, at (100, 100)
with arcade-3.x this is the starter step, and
Window has a self.boids instead of a single self.boid
"""

import random
import math
import itertools
import numpy as np

import arcade

BACKGROUND = arcade.color.ALMOND
IMAGE = "media/arrow-resized.png"
OBSTACLE = "media/obstacle-resized.png"
WINDOW_WIDTH, WINDOW_HEIGHT = 800, 800

DEBUG = False
# DEBUG = True


class Obstacle(arcade.Sprite):

    def __init__(self, x, y):
        super().__init__(OBSTACLE)
        self.center_x = x
        self.center_y = y


class Boid(arcade.Sprite):

    def __init__(self, obstacles, boids, x0=100, y0=100):
        super().__init__(IMAGE)
        self.center_x = x0
        self.center_y = y0
        self.steer = 0  # rotation imposée par le clavier
        self.speed = 1
        self.obstacles = obstacles
        self.boids = boids

    def update(self, delta_time):

        # Sauvegarde de l'ancienne position (pour recalculer l'orientation)
        old_x = self.center_x
        old_y = self.center_y

        #self.manage_obstacles()

        # Bruit aléatoire + contrôle clavier sur l'angle
        self.angle += random.uniform(-2, 2)
        self.angle += self.steer
        # Déplacement selon l'angle et la vitesse
        self.center_x += self.speed * math.cos(math.radians(-self.angle))
        self.center_y += self.speed * math.sin(math.radians(-self.angle))

        # Appliquer les règles de cohésion et de séparation
        delta_x, delta_y = self.compute_separation(itertools.chain(self.boids, self.obstacles))
        cohesion = self.compute_cohesion()
        if cohesion is not None:
            delta_x += 0.005 * cohesion[0]
            delta_y += 0.005 * cohesion[1]

        # Mise à jour de la position avec les contributions des règles
        self.center_x += delta_x
        self.center_y += delta_y

        #
        self.center_x %= WINDOW_WIDTH
        self.center_y %= WINDOW_HEIGHT

        #Ajustement fluide de l'orientation selon le déplacement réel
        dx = self.center_x - old_x
        dy = self.center_y - old_y
        if dx != 0 or dy != 0:
            target_angle = -math.degrees(math.atan2(dy, dx))
            diff = (target_angle - self.angle + 180) % 360 - 180
            self.angle += 0.05 * diff

        #Règle d'alignement
        alignment_angle = self.compute_alignment()
        if alignment_angle is not None:
            diff = (alignment_angle - self.angle + 180) % 360 - 180
            self.angle += 0.05 * diff


        if DEBUG:
            print(f"Boid at ({self.center_x}, {self.center_y})" )

    def compute_separation(self, sprites):
        # Calcule un vecteur de répulsion vis-à-vis des objets proches
        delta_x, delta_y = 0, 0
        for sprite in sprites:
            if sprite is self:
                continue
            d = math.sqrt((self.center_x - sprite.center_x) ** 2
                 + (self.center_y - sprite.center_y) ** 2)
            if (d >= 30):
                continue
            # ce boid est dans le voisinage
            delta_x = (- sprite.center_x + self.center_x) * (1 - d/30)/2
            delta_y = (- sprite.center_y + self.center_y) * (1 - d/30)/2
        return delta_x, delta_y

    def compute_cohesion(self):
        # Calcule un vecteur vers le "centre de masse" des boids voisins
        sum_x, sum_y = 0,0
        count = 0

        for boid in self.boids:
            if boid is self:
                continue

            d = math.sqrt((self.center_x - boid.center_x) ** 2
                          + (self.center_y - boid.center_y) ** 2)

            if d >= 50:
                continue

            sum_x += boid.center_x
            sum_y += boid.center_y
            count += 1

        if count == 0:
            return None

        center_x = sum_x / count
        center_y = sum_y / count

        delta_x = center_x - self.center_x
        delta_y = center_y - self.center_y

        return delta_x, delta_y

    def compute_alignment(self):
        # Calcule la direction moyenne des boids voisins
        sum_x ,sum_y = 0,0
        count = 0

        for boid in self.boids:
            if boid is self:
                continue

            d = math.sqrt((self.center_x - boid.center_x) ** 2
                 + (self.center_y - boid.center_y) ** 2)

            if d >= 30:
                continue

            # Conversion angle -> vecteur unitaire pour pouvoir faire la moyenne
            angle = math.radians(-boid.angle)
            sum_x += math.cos(angle)
            sum_y += math.sin(angle)
            count += 1

        if count == 0:
            return None

        avg_x = sum_x / count
        avg_y = sum_y / count

        return -math.degrees(math.atan2(avg_y, avg_x))

    def manage_obstacles(self):
        # Rend le boid semi-transparent lorsqu'il est proche d'un obstacle
        for obstacle in self.obstacles:
            if (
                (self.center_x - obstacle.center_x) ** 2
                 + (self.center_y - obstacle.center_y) ** 2) <= 20**2:
                self.alpha = 50
                break
            else:
                self.alpha = 255



    def turn_right(self):
        self.steer = +3
    def turn_left(self):
        self.steer = -3
    def turn_neutral(self):
        self.steer = 0
    def speed_up(self):
        self.speed *= 1.2
    def speed_down(self):
        self.speed /= 1.2
    def speed_neutral(self):
        self.speed = 1


class Window(arcade.Window):

    def __init__(self):
        super().__init__(WINDOW_WIDTH, WINDOW_HEIGHT, "My first boid")
        arcade.set_background_color(BACKGROUND)
        self.set_location(1000, 100)
        self.boids = None
        self.obstacles = None

    def setup(self):
        self.obstacles = arcade.SpriteList()
        for i in np.linspace(0,2*math.pi,10):
            self.obstacles.append(Obstacle(400 + 150*math.cos(i), 400 + 150*math.sin(i)))
        self.boids = arcade.SpriteList()
        for i in range(100,350,50):
            for j in range(100,350,50):
                self.boids.append(Boid(self.obstacles, self.boids, x0=i, y0=j))


    def on_draw(self):
        self.clear()
        self.boids.draw()
        self.obstacles.draw()

    def on_update(self, delta_time):
        self.boids.update()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.RIGHT:
            for boid in self.boids:
                boid.turn_right()
        elif key == arcade.key.LEFT:
            for boid in self.boids:
                boid.turn_left()
        elif key == arcade.key.UP:
            for boid in self.boids:
                boid.speed_up()
        elif key == arcade.key.DOWN:
            for boid in self.boids:
                boid.speed_down()
        elif key == arcade.key.SPACE:
            for boid in self.boids:
                boid.speed_neutral()

    def on_key_release(self, key, modifiers):
        if key == arcade.key.RIGHT or key == arcade.key.LEFT:
            for boid in self.boids:
                boid.turn_neutral()


window = Window()
window.setup()
if DEBUG:
    window.set_update_rate(1/2)  # slow motion for debug
arcade.run()
