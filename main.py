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


import argparse
parser = argparse.ArgumentParser()
parser.add_argument("mode", help="donne le numéro du niveau auquel tu veux jouer")
args = parser.parse_args()
LEVEL = int(args.mode)

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

        #Initialiser les listes de goos proches (et les liens associés)
        self.goos_proches= arcade.SpriteList()
        self.liens = arcade.SpriteList()
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

        self.est_plateforme = est_plateforme
        if self.est_plateforme:
            self.alpha = 0
            #enlever la gravité


    def update(self, delta_time):
        ax, ay = (self.force / self.masse)
        self.change_x += ax * delta_time
        self.change_x *= 0.95
        self.change_y += ay * delta_time
        self.change_y *= 0.95


    def ajouter_plateforme_proche(self): #distinction de cas si sur un coté ou un coin
        for plateforme in self.plateformes:
            if self.center_x<plateforme.center_x+plateforme.longueur/2 and self.center_x>plateforme.center_x-plateforme.longueur/2:
                    sens = math.copysign(1, self.center_y - plateforme.center_y)
                    dist=abs(self.center_y-(plateforme.center_y+plateforme.hauteur/2))
                    if dist<10:
                        goo=Goo(self.center_x, plateforme.center_y+sens*plateforme.hauteur/2, True)
                        self.goos.append(goo)
                        nouveau_lien = Lien([self, goo])
                        self.liens_tot.append(nouveau_lien)
                        self.liens.append(nouveau_lien)


            elif self.center_y<plateforme.center_y+plateforme.hauteur/2 and self.center_y>plateforme.center_y-plateforme.hauteur/2:
                    sens = math.copysign(1, self.center_x - plateforme.center_x)
                    dist=abs(self.center_x-(plateforme.center_x+plateforme.longueur/2))
                    if dist<10:
                        goo=Goo(plateforme.center_x+sens*plateforme.longueur/2, self.center_y, True)
                        self.goos.append(goo)
                        nouveau_lien = Lien([self, goo])
                        self.liens_tot.append(nouveau_lien)
                        self.liens.append(nouveau_lien)


            else :
                coins=[(plateforme.center_x+plateforme.longueur/2, plateforme.center_y+plateforme.hauteur/2),
                       (plateforme.center_x-plateforme.longueur/2, plateforme.center_y+plateforme.hauteur/2),
                       (plateforme.center_x+plateforme.longueur/2, plateforme.center_y-plateforme.hauteur/2),
                       (plateforme.center_x-plateforme.longueur/2, plateforme.center_y-plateforme.hauteur/2)]
                for coin in coins:
                    dist=((coin[0]-self.center_x)**2+(coin[1]-self.center_y)**2)**(1/2)
                    if dist<20:
                        goo=Goo(coin[0], coin[1], True)
                        self.goos.append(goo)
                        nouveau_lien = Lien([self, goo])
                        self.liens_tot.append(nouveau_lien)
                        self.liens.append(nouveau_lien)

    def reset_force(self):
        self.force = np.array([0.0, 0.0])

    def apply_force(self, force):
        self.force += force





class Plateforme(arcade.Sprite):
    def __init__(self, center_x, center_y, hauteur, longueur):
        self.center_x = center_x
        self.center_y = center_y
        self.hauteur = hauteur
        self.longueur = longueur
        super().__init__() #mettre le sprite ici




class Lien(arcade.Sprite):
    def __init__(self, goos):
        super().__init__("media/barre.png", scale=0.1)  # mettre le sprite ici
        self.goos = goos
        self.l0 = dist((self.goos[0].center_x, self.goos[0].center_y), (self.goos[1].center_x, self.goos[1].center_y))
        self.k = 6
        self.l = self.l0
        self.c = 1

    def goos_pos(self):
        return [np.array([goo.center_x, goo.center_y]) for goo in self.goos]

    def update(self, delta_time):
        pos = self.goos_pos()

        self.l = dist(pos[0], pos[1])
        self.image_width = self.l
        self.center_x, self.center_y = (pos[0]+pos[1])/2
        self.angle = np.degrees(np.arctan2(pos[1][1]-pos[0][1], -pos[1][0]+pos[0][0]))
        self.force_elastique()

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

        self.level = LEVEL

        # mettre une crate au centre"
        crate = arcade.Sprite(":resources:images/tiles/boxCrate_double.png", scale=TILE_SCALING)
        crate.position = [WINDOW_WIDTH // 2, 96] # Au centre
        self.wall_list.append(crate)


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


        if self.level == 1 : 

            # mettre une crate au centre"
            crate = arcade.Sprite(":resources:images/tiles/boxCrate_double.png", scale=TILE_SCALING)
            crate.position = [WINDOW_WIDTH // 2, 96] # Au centre
            self.wall_list.append(crate)


            # Plateforme Gauche
            for x in range(0, 256, 64):
                wall = arcade.Sprite(":resources:images/tiles/grassMid.png", scale=TILE_SCALING)
                wall.center_x = x
                wall.center_y = 32
                self.wall_list.append(wall)

            # Plateforme Droite
            for x in range(1000, 1280, 64):
                wall = arcade.Sprite(":resources:images/tiles/grassMid.png", scale=TILE_SCALING)
                wall.center_x = x
                wall.center_y = 32
                self.wall_list.append(wall)
            
        elif self.level == 2 :


            # mettre une crate au centre"
            crate = arcade.Sprite(":resources:images/tiles/snow.png", scale=TILE_SCALING)
            crate.position = [WINDOW_WIDTH // 2, 500] # Au centre
            self.wall_list.append(crate)


            # Plateforme Gauche
            for x in range(0, 128, 64):
                wall = arcade.Sprite(":resources:images/tiles/sand.png", scale=TILE_SCALING)
                wall.center_x = x
                wall.center_y = 128
                self.wall_list.append(wall)

            # Plateforme Droite
            for x in range(1200, 1280, 64):
                wall = arcade.Sprite(":resources:images/tiles/sand.png", scale=TILE_SCALING)
                wall.center_x = x
                wall.center_y = 32
                self.wall_list.append(wall)


        elif self.level == 3:

            # Grande statue/rocher au centre
            crate = arcade.Sprite(":resources:images/tiles/stoneCenter.png", scale=TILE_SCALING)
            crate.position = [WINDOW_WIDTH // 2, 250]
            self.wall_list.append(crate)

            # Plateforme gauche — sable
            for x in range(0, 320, 64):
                wall = arcade.Sprite(":resources:images/tiles/sandMid.png", scale=TILE_SCALING)
                wall.center_x = x
                wall.center_y = 64
                self.wall_list.append(wall)

            # Plateforme droite — roche désertique
            for x in range(960, 1280, 64):
                wall = arcade.Sprite(":resources:images/tiles/stoneMid.png", scale=TILE_SCALING)
                wall.center_x = x
                wall.center_y = 64
                self.wall_list.append(wall)



        elif self.level == 4:


            # Grosse pierre flottante
            rock = arcade.Sprite(":resources:images/tiles/stoneCenter.png", scale=TILE_SCALING)
            rock.center_x = WINDOW_WIDTH // 2
            rock.center_y = 350
            self.wall_list.append(rock)

            # Plateformes flottantes en diagonale
            for i in range(5):
                p = arcade.Sprite(":resources:images/tiles/stoneMid.png", scale=TILE_SCALING)
                p.center_x = 200 + i * 150
                p.center_y = 150 + i * 50
                self.wall_list.append(p)

            # Gemmes lumineuses comme décor
            for i in range(4):
                gem = arcade.Sprite(":resources:images/items/gemBlue.png", scale=0.5)
                gem.center_x = 300 + i * 200
                gem.center_y = 600
                self.wall_list.append(gem)

        
        elif self.level == 5:
            for x in range(0, 1280, 64):
                s = arcade.Sprite(":resources:images/tiles/stoneCenter.png", TILE_SCALING)
                s.center_x = x
                s.center_y = 32
                self.wall_list.append(s)

            for i in range(6):
                p = arcade.Sprite(":resources:images/tiles/stoneMid.png", TILE_SCALING)
                p.center_x = 180 + i * 180
                p.center_y = 200 + (i % 2) * 100
                self.wall_list.append(p)

            deco = arcade.Sprite(":resources:images/items/gemBlue.png", 0.5)
            deco.center_x = 1000
            deco.center_y = 400
            self.wall_list.append(deco)




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
            goo_x = int(self.cursor.center_x)
            goo_y = int(self.cursor.center_y)
            goo = Goo(goo_x, goo_y, self.goos, self.liens_tot, self.plateformes)

            # Ajouter à la liste d'affichage
            self.goos.append(goo)


            # Créer un engine physique pour cette boule
            # Elle va tomber et s'arrêter sur les murs (sol/caisses) définis dans self.wall_list
            # Mais elle ne s'arrêtera pas sur les autres boules car elles ne sont pas dans la liste.
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





