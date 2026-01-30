import arcade
import numpy as np
import math as math

#world of goos en python
class Goo(arcade.Sprite):
    def __init__(self, x, y, est_plateforme):
        self.center_x = x
        self.center_y = y
        self.vx = 0
        self.vy = 0
        self.masse = 400 #g
        self.rayon = 1 #cm
        self.liens = []
        self.est_plateforme = est_plateforme
        if self.est_plateforme:
            self.alpha = 0
            #enlever la gravité
        self.goos=arcade.SpriteList()
        self.plateformes_proches = arcade.SpriteList()
        super().__init__() #mettre le sprite ici
        self.ajouter_plateforme_proche(self)
        self.ajouter_goo_proche(self)
        #attention, faudra faire au moins un lien à la création





    def  ajouter_lien(self, goo):
        self.liens.append((Lien(goo, self)))
    
    

    def ajouter_goo_proche(self):
        for goo in self.goos:
            dist=((goo.x-self.x)**2+(goo.y-self.y)**2)**(1/2)
            if dist<20:
                self.ajouter_lien(goo) #à modifier quand on aura les classes liens
    
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







class Plateforme(arcade.Sprite):
    def __init__(self, center_x, center_y, hauteur, longueur):
        self.x = center_x
        self.y = center_y
        self.hauteur = hauteur
        self.longueur = longueur
        super().__init__() #mettre le sprite ici
    

