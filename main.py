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
GRAVITY = 1.0
PLAYER_SCALE = 0.1



def dist(a,b):
    return ((a[0] - b[0])**2 + (a[0] - b[0])**2)**0.5

#world of goos en python
class Goo(arcade.Sprite):
    def __init__(self, x, y, goos, liens, plateformes, est_plateforme=False):
        self.center_x = x
        self.center_y = y
        #Liste de tous les goos, tous les liens, toutes les plateformes
        self.goos = goos
        self.liens_tot = liens
        self.plateformes = plateformes
        self.vx = 0
        self.vy = 0
        self.masse = 400e-3 #kg
        self.rayon = 1e-2 #cm

        #Initialiser les listes de goos proches (et les liens associés)
        self.goos_proches= arcade.SpriteList()
        self.liens = arcade.SpriteList()
        for goo in self.goos:
            d = dist((self.center_x, self.center_y), (goo.center_x, goo.center_y))
            if goo == self:
                continue
            if d < 20e-2:
                self.goos_proches.append(goo)
                nouveau_lien = Lien([self, goo])
                self.liens_tot.append(nouveau_lien)
                self.liens.append(nouveau_lien)

        self.est_plateforme = est_plateforme
        if self.est_plateforme:
            self.alpha = 0
            #enlever la gravité
        super().__init__() #mettre le sprite ici


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


    #Force elastique exercée par les liens
    def force_elastique(self):
        for lien in self.liens:
            AB = lien.goos_pos()[1] - lien.goos_pos()[0]
            ab = AB / np.linalg.norm(AB)
            dgoo = lien.k*(lien.l-lien.l0)*ab*delta_time/self.masse
            self.center_x += dgoo[0]
            self.center_y += dgoo[1]


class Plateforme(arcade.Sprite):
    def __init__(self, center_x, center_y, hauteur, longueur):
        self.center_x = center_x
        self.center_y = center_y
        self.hauteur = hauteur
        self.longueur = longueur
        super().__init__() #mettre le sprite ici




class Lien(arcade.Sprite):
    def __init__(self, goos):
        self.goos = goos
        self.l0 = dist((self.goos[0].center_x, self.goos[0].center_y), (self.goos[0].center_x, self.goos[1].center_y))
        self.k = 100
        self.l = self.l0

    def goos_pos(self):
        return [np.array([goo.center_x, goo.center_y]) for goo in self.goos]

    def update(self):
        pos = self.goos_pos()

        self.l = dist(pos[0], pos[1])
        self.image_width = self.l
        self.center_x, self.center_y = (pos[0]+pos[1])/2
        self.angle = np.degrees(np.arctan2(pos[1][1]-pos[0][1], pos[1][0]-pos[0][0]))

# Constants
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE = "Platformer - Mode Vol (Sans Gravité Joueur)"

# Constants used to scale our sprites from their original size
TILE_SCALING = 0.5

# Movement speed of player, in pixels per frame
PLAYER_MOVEMENT_SPEED = 5
GRAVITY = 1.0
PLAYER_SCALE = 0.1

class GameView(arcade.Window):
    """
    Main application class.
    """
    def __init__(self):

        # Call the parent class and set up the window
        super().__init__(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE)

        self.player_sprite = arcade.Sprite("boule.png", scale=PLAYER_SCALE)

        self.player_sprite.center_x = 64
        self.player_sprite.center_y = 128

        # SpriteList for our player
        self.player_list = arcade.SpriteList()
        self.player_list.append(self.player_sprite)

        self.wall_list = arcade.SpriteList(use_spatial_hash=True)

        self.player_list = arcade.SpriteList()
        self.player_list.append(self.player_sprite)

        self.wall_list = arcade.SpriteList(use_spatial_hash=True)


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

        # mettre une crate au centre"
        crate = arcade.Sprite(":resources:images/tiles/boxCrate_double.png", scale=TILE_SCALING)
        crate.position = [WINDOW_WIDTH // 2, 96] # Au centre
        self.wall_list.append(crate)


        # On utilise PhysicsEngineSimple pour le joueur.
        # Ce moteur gère les collisions murs/joueur MAIS n'applique pas de gravité.
        self.physics_engine = arcade.PhysicsEngineSimple(
            self.player_sprite,
            walls=self.wall_list
        )

        self.background_color = arcade.csscolor.CORNFLOWER_BLUE

        # Liste des boules dynamiques
        self.ball_list = arcade.SpriteList()

        # Liste des moteurs physiques (un engine par boule)
        self.ball_physics_engines = []


    def setup(self):
        """Set up the game here. Call this function to restart the game."""
        pass

    def on_draw(self):
        """Render the screen."""
        self.clear()
        self.player_list.draw()
        self.wall_list.draw()
        self.ball_list.draw()


    def on_update(self, delta_time):
        """Movement and Game Logic"""

        # Move the player using our simple physics engine (pas de gravité)
        self.physics_engine.update()

        # Mettre à jour toutes les boules (elles ont la gravité)
        for engine in self.ball_physics_engines:
            engine.update()

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed."""

        if key == arcade.key.UP or key == arcade.key.Z:
            self.player_sprite.change_y = PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.player_sprite.change_y = -PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.LEFT or key == arcade.key.Q:
            self.player_sprite.change_x = -PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED

        if key == arcade.key.ENTER:
            # Créer la boule
            try:
                ball = arcade.Sprite("boule.png", scale=PLAYER_SCALE)
            except:
                ball = arcade.Sprite(":resources:images/items/gold_1.png", scale=PLAYER_SCALE)

            # Position : sur le joueur
            ball.center_x = self.player_sprite.center_x
            ball.center_y = self.player_sprite.center_y

            # Ajouter à la liste d'affichage
            self.ball_list.append(ball)

            # --- MODIFICATION ICI ---
            # SUPPRIMEZ ou COMMENTEZ cette ligne :
            # self.wall_list.append(ball)  <-- C'est elle la coupable !
            # ------------------------

            # Créer un engine physique pour cette boule
            # Elle va tomber et s'arrêter sur les murs (sol/caisses) définis dans self.wall_list
            # Mais elle ne s'arrêtera pas sur les autres boules car elles ne sont pas dans la liste.
            ball_engine = arcade.PhysicsEnginePlatformer(
                ball,
                walls=self.wall_list,
                gravity_constant=GRAVITY
            )

            self.ball_physics_engines.append(ball_engine)

    def on_key_release(self, key, modifiers):
        """Called whenever a key is released."""

        # Avec PhysicsEngineSimple, il faut arrêter le mouvement Y manuellement
        # quand on relâche la touche, sinon le joueur continue de glisser.

        if key == arcade.key.UP or key == arcade.key.Z:
            self.player_sprite.change_y = 0
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.player_sprite.change_y = 0

        if key == arcade.key.LEFT or key == arcade.key.Q or key == arcade.key.A:
            self.player_sprite.change_x = 0
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.player_sprite.change_x = 0


def main():
    """Main function"""
    window = GameView()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()