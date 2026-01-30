import arcade
import numpy as np
import math as math

delta_time = 1/60
# Constants
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE = "Platformer - Mode Vol (Sans Gravité Joueur)"

# Constants used to scale our sprites from their original size
TILE_SCALING = 0.5

# Movement speed of player, in pixels per frame
PLAYER_MOVEMENT_SPEED = 5
GRAVITY = 1/15
PLAYER_SCALE = 0.05



def dist(a,b):
    return ((a[0] - b[0])**2 + (a[1] - b[1])**2)**0.5

#world of goos en python
class Goo(arcade.Sprite):
    def __init__(self, x, y, goos, liens, plateformes, est_plateforme=False):
        super().__init__('media/boule.png', scale=PLAYER_SCALE)  # mettre le sprite ici
        self.center_x = x
        self.center_y = y
        #Liste de tous les goos, tous les liens, toutes les plateformes
        self.goos = goos
        self.liens_tot = liens
        self.plateformes = plateformes
        self.vx = 0
        self.vy = 0
        self.masse = 400e-3 #kg
        self.rayon = 20 #cm
        self.force = np.array([0.0, 0.0])

        # Initialiser les listes de goos proches (et les liens associés)
        self.goos_proches = arcade.SpriteList()
        self.liens = arcade.SpriteList()

        if est_plateforme:
            self.alpha = 0
        else:
            for goo in self.goos:
                d = dist((self.center_x, self.center_y), (goo.center_x, goo.center_y))
                if goo == self:
                    continue
                if d < 100:
                    self.goos_proches.append(goo)
                    goo.goos_proches.append(self)
                    nouveau_lien = Lien([self, goo])
                    self.liens_tot.append(nouveau_lien)
                    self.liens.append(nouveau_lien)

            goo_plateforme_distmin = np.inf
            goo_plateforme_proche = None
            for plateforme in self.plateformes:
                d = dist((self.center_x, self.center_y), (plateforme.center_x, plateforme.center_y))
                if d < goo_plateforme_distmin:
                    goo_plateforme_distmin = d
                    goo_plateforme_proche = plateforme
            if goo_plateforme_distmin < 50:
                self.goos_proches.append(goo_plateforme_proche)
                goo_plateforme_proche.goos_proches.append(self)
                nouveau_lien = Lien([self, goo_plateforme_proche])
                self.liens_tot.append(nouveau_lien)
                self.liens.append(nouveau_lien)


    def update(self, delta_time):
        ax, ay = (self.force / self.masse)
        self.change_x += ax * delta_time
        self.change_x *= 0.95
        self.change_y += ay * delta_time
        self.change_y *= 0.95

    def reset_force(self):
        self.force = np.array([0.0, 0.0])

    def apply_force(self, force):
        self.force += force



class Plateforme(arcade.Sprite):
    def __init__(self, x, y, goos, liens_tot, plateformes):
        self.goos_plateforme = arcade.SpriteList()
        for i in range(x-32, x+33, 5):
            goo_plateforme = Goo(i, y+25, goos, liens_tot, plateformes, est_plateforme=True)
            self.goos_plateforme.append(goo_plateforme)
        for i in range(y-32, y+33, 5):
            goo_plateforme = Goo(x+25, i, goos, liens_tot, plateformes, est_plateforme=True)
            self.goos_plateforme.append(goo_plateforme)
            goo_plateforme = Goo(x - 25, i, goos, liens_tot, plateformes, est_plateforme=True)
            self.goos_plateforme.append(goo_plateforme)
        self.wall = arcade.Sprite(":resources:images/tiles/grassMid.png", scale=TILE_SCALING)
        self.wall.center_x = x
        self.wall.center_y = y

    def add_to_plateformes(self, plateformes, walls):
        for goo_plateforme in self.goos_plateforme:
            plateformes.append(goo_plateforme)
        walls.append(self.wall)



class Lien(arcade.Sprite):
    def __init__(self, goos):
        super().__init__("media/barre.png")  # mettre le sprite ici
        self.goos = goos
        self.l0 = dist((self.goos[0].center_x, self.goos[0].center_y), (self.goos[1].center_x, self.goos[1].center_y))
        self.k = 6
        self.l = self.l0
        self.c = 1
        self.scale_y = 0.1

    def goos_pos(self):
        return [np.array([goo.center_x, goo.center_y]) for goo in self.goos]

    def update(self, delta_time):
        pos = self.goos_pos()

        self.l = dist(pos[0], pos[1])
        self.image_width = self.l
        self.center_x, self.center_y = (pos[0]+pos[1])/2
        self.angle = np.degrees(np.arctan2(pos[1][1]-pos[0][1], -pos[1][0]+pos[0][0]))
        self.force_elastique()
        self.scale_x = self.l / self.texture.width

    def force_elastique(self):
        a, b = self.goos[0], self.goos[1]

        pa = np.array([a.center_x, a.center_y])
        pb = np.array([b.center_x, b.center_y])

        d = pb - pa
        L = np.linalg.norm(d)


        if L < 1e-6:
            return

        n = d / L
        x = L - self.l0

        va = np.array([a.change_x, a.change_y])
        vb = np.array([b.change_x, b.change_y])

        rel_v = np.dot(vb - va, n)

        Fs = self.k * x * n
        Fd = self.c * rel_v * n
        F = Fs + Fd

        a.apply_force(+F)
        b.apply_force(-F)

class GameView(arcade.Window):
    """
    Main application class.
    """
    def __init__(self):

        # Call the parent class and set up the window
        super().__init__(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE)

        self.cursor = arcade.Sprite("media/cursor.png", scale=0)
        self.cursor.center_x = 64
        self.cursor.center_y = 128

        # SpriteList for our player
        self.player_list = arcade.SpriteList()
        self.player_list.append(self.cursor)

        self.wall_list = arcade.SpriteList(use_spatial_hash=True)

        self.player_list = arcade.SpriteList()
        self.player_list.append(self.cursor)

        self.wall_list = arcade.SpriteList(use_spatial_hash=True)

        self.goos = arcade.SpriteList()
        self.liens_tot = arcade.SpriteList()
        self.plateformes = arcade.SpriteList()

        # Plateforme Gauche
        for x in range(0, 256, 64):
            plateforme = Plateforme(x, 32, self.goos, self.liens_tot, self.plateformes)
            plateforme.add_to_plateformes(self.plateformes,self.wall_list)

        # Plateforme Droite
        for x in range(1000, 1280, 64):
            plateforme = Plateforme(x, 32, self.goos, self.liens_tot, self.plateformes)
            plateforme.add_to_plateformes(self.plateformes, self.wall_list)

        # mettre une crate au centre"
        crate = arcade.Sprite(":resources:images/tiles/boxCrate_double.png", scale=TILE_SCALING)
        crate.position = [WINDOW_WIDTH // 2, 96] # Au centre
        self.wall_list.append(crate)

        self.goos.append(Goo(100, 64, self.goos, self.liens_tot, self.plateformes))

        # On utilise PhysicsEngineSimple pour le joueur.
        # Ce moteur gère les collisions murs/joueur MAIS n'applique pas de gravité.
        self.physics_engine = arcade.PhysicsEngineSimple(
            self.cursor,
            walls=self.wall_list
        )

        self.background_color = arcade.csscolor.CORNFLOWER_BLUE

        # Liste des boules dynamiques
        self.ball_list = arcade.SpriteList()

        # Liste des moteurs physiques (un engine par boule)
        self.goo_physics_engines = []


    def setup(self):
        """Set up the game here. Call this function to restart the game."""
        pass

    def on_draw(self):
        """Render the screen."""
        self.clear()
        self.player_list.draw()
        self.wall_list.draw()
        self.liens_tot.draw()
        self.goos.draw()
        self.plateformes.draw()


    def on_update(self, delta_time):
        """Movement and Game Logic"""
        # Move the player using our simple physics engine (pas de gravité)
        self.physics_engine.update()
        for goo in self.goos:
            goo.reset_force()
        for lien in self.liens_tot:
            lien.update(delta_time)
        for goo in self.goos:
            goo.update(delta_time)

        # Mettre à jour toutes les boules (elles ont la gravité)
        for engine in self.goo_physics_engines:
            engine.update()

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed."""
        if key == arcade.key.ENTER:
            near_goo_count = 0
            for goo in self.goos:
                d = dist((self.cursor.center_x, self.cursor.center_y), (goo.center_x, goo.center_y))
                if goo == self:
                    continue
                if d < 100:
                    near_goo_count += 1

            if near_goo_count >= 1:

                goo_x = int(self.cursor.center_x)
                goo_y = int(self.cursor.center_y)
                goo = Goo(goo_x, goo_y, self.goos, self.liens_tot, self.plateformes)

                # Ajouter à la liste d'affichage
                self.goos.append(goo)

                goo_engine = arcade.PhysicsEnginePlatformer(
                    goo,
                    walls=self.wall_list,
                    gravity_constant=GRAVITY
                )

                self.goo_physics_engines.append(goo_engine)

    def on_mouse_motion(self, x, y, dx, dy):
        """ Called to update our mouse pointer sprite. """
        self.cursor.center_x = x
        self.cursor.center_y = y


def main():
    """Main function"""
    window = GameView()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()