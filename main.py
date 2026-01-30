import arcade
import numpy as numpy

#world of goos en python
class Goo(arcade.Sprite):
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.masse = 400 #g
        self.rayon = 1 #cm
        self.liens = []
        self.goos_proches = arcade.SpriteList()
        self.plateformes_proches = arcade.SpriteList()
        super().__init__() #mettre le sprite ici

    def  ajouter_lien_goo(self, goo):
        self.liens.append((Lien(goo, self))

    def ajouter_lien_plateforme(self, point):
        self.liens.append((Lien(self, point))

    def ajouter_goo_proche(self):
        for goo in self.goos_proches:
            dist=((goo.x-self.x)**2+(goo.y-self.y)**2)**(1/2)
            if dist<20:
                self.ajouter_lien(goo) #à modifier quand on aura les classes liens

    def ajouter_plateforme_proche(self):
        for plateforme in self.plateforme:
            if self.x<plateforme.x+plateforme.longueur/2 and self.x>plateforme.x-plateforme.longueur/2:
                    dist=abs(self.y-(plateforme.center_y+plateforme.hauteur/2))
                    if dist<20:
                    point=(self.x, plateforme.center_y+plateforme.hauteur/2)
                        self.ajouter_lien_plateforme(self, point)








class Plateforme(arcade.Sprite):
    def __init__(self, centre_x, centre_y, hauteur, longueur):
        self.x = centre_x
        self.y = centre_y
        self.hauteur = hauteur
        self.longueur = longueur
        super().__init__() #mettre le sprite ici


import arcade
import numpy as np

def dist(a,b):
    return ((a[0] - b[0])**2 + (a[0] - b[0])**2)**0.5

class Spring(arcade.Sprite):
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
