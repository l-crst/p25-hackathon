import arcade

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