import arcade
import numpy as np

delta_time = 1/60

def dist(a,b):
    return ((a[0] - b[0])**2 + (a[0] - b[0])**2)**0.5

#world of goos en python
class Goo(arcade.Sprite):
    def __init__(self, x, y, goos, liens, plateformes):
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


    def ajouter_plateforme_proche(self):
        for plateforme in self.plateformes_proches:
            if self.center_x<plateforme.center_x+plateforme.longueur/2 and self.center_x>plateforme.center_x-plateforme.longueur/2:
                    sens = math.copysign(1, self.center_y - plateforme.center_y)
                    dist=abs(self.center_y-(plateforme.center_y+plateforme.hauteur/2))
                    if dist<20:
                        goo=Goo(self.center_x, plateforme.center_y+sens*plateforme.hauteur/2, True)
                        self.goos.append(goo)
                        self.ajouter_lien(self, goo)


            elif self.center_y<plateforme.center_y+plateforme.hauteur/2 and self.center_y>plateforme.center_y-plateforme.hauteur/2:
                    sens = math.copysign(1, self.center_x - plateforme.center_x)
                    dist=abs(self.center_x-(plateforme.center_x+plateforme.longueur/2))
                    if dist<20:
                        goo=Goo(plateforme.center_x+sens*plateforme.longueur/2, self.center_y, True)
                        self.goos.append(goo)
                        self.ajouter_lien(self, goo)


            else :
                coins=[(plateforme.center_x+plateforme.longueur/2, plateforme.center_y+plateforme.hauteur/2),
                       (plateforme.center_x-plateforme.longueur/2, plateforme.center_y+plateforme.hauteur/2),
                       (plateforme.center_x+plateforme.longueur/2, plateforme.center_y-hauteur/2),
                       (plateforme.center_x-plateforme.longueur/2, plateforme.center_y-hauteur/2)]
                for coin in coins:
                    dist=((coin[0]-self.center_x)**2+(coin[1]-self.center_y)**2)**(1/2)
                    if dist<20:
                        goo=Goo(coin[0], coin[1], True)
                        self.goos.append(goo)
                        self.ajouter_lien(self, goo)

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
        self.x = center_x
        self.y = center_y
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
