import pygame
import time

from pygame.locals import*
from time import sleep


class Sprite():
    def __init__(self, x, y, type):
        self.x = x
        self.y = y
        self.type = type
        self.image = None
        self.width = 0
        self.height = 0

    def update(self):
        return

    def draw(self, screen, offset):
        self.rect = (self.x - offset + 50, self.y, self.width, self.height)
        screen.blit(self.image, self.rect)


class Mario(Sprite):
    def __init__(self):
        self.x = 50
        self.y = 300
        self.type = 0
        self.images = []
        for i in range(1, 6):
            self.images.append(pygame.image.load(
                "./assets/mario" + str(i) + ".png"))
        self.image = self.images[0]
        self.imageIndex = 0
        self.velocity = 0.0
        self.framesSinceSolidGround = 0
        self.px = 0
        self.py = 0
        self.width = 60
        self.height = 95

    def update(self):
        self.velocity += 1.2
        self.y += self.velocity
        self.framesSinceSolidGround += 1
        self.image = self.images[int((self.imageIndex/5) % 5)]
        if self.y >= 300:
            self.velocity = 0.0
            self.y = 300
            self.framesSinceSolidGround = 0

    def draw(self, screen, offset):
        self.rect = (50, self.y, self.width, self.height)
        screen.blit(self.image, self.rect)


class Tube(Sprite):
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.type = 1
        self.image = pygame.image.load("./assets/tube.png")
        self.width = 55
        self.height = 400
        self.rect = (self.x, self.y, self.width, self.height)


class Goomba(Sprite):
    def __init__(self, x):
        self.images = []
        self.images.append(pygame.image.load("./assets/goomba.png"))
        self.images.append(pygame.image.load("./assets/goomba_fire.png"))
        self.image = self.images[0]
        self.width = 99
        self.height = 118
        self.x = x
        self.y = 400 - self.height
        self.type = 2
        self.movingRight = True
        self.onFire = False
        self.framesSinceOnFire = 0

    def update(self):
        if self.movingRight:
            self.x += 1
        else:
            self.x -= 1

        if self.onFire:
            self.framesSinceOnFire += 1

    def draw(self, screen, offset):
        self.rect = (self.x - offset + 50, self.y, self.width, self.height)
        if self.onFire:
            screen.blit(self.images[1], self.rect)
        else:
            screen.blit(self.images[0], self.rect)


class Fireball(Sprite):
    def __init__(self, x, y):
        self.image = pygame.image.load("./assets/fireball.png")
        self.width = 47
        self.height = 47
        self.x = x
        self.y = y
        self.type = 3
        self.velocity = 0

    def update(self):
        self.x += 2
        self.velocity += 1.05
        self.y += self.velocity
        if self.y >= 400 - self.height:
            self.velocity = -10.0
            self.y = 400 - self.height

    def draw(self, screen, offset):
        self.rect = (self.x - offset + 100, self.y, self.width, self.height)
        screen.blit(self.image, self.rect)


class Model():
    def __init__(self):
        self.sprites = []
        self.mario = Mario()
        self.sprites.append(self.mario)
        self.sprites.append(Tube(276, 347))
        self.sprites.append(Tube(553, 331))
        self.sprites.append(Tube(897, 257))
        self.sprites.append(Tube(1291, 164))
        size = len(self.sprites)
        for i in range(1, size - 1):
            t = self.sprites[i]
            self.sprites.append(Goomba(t.x + t.width))

    def update(self):
        for s in self.sprites:
            s.update()

        self.colliding = False
        for s in self.sprites:
            if self.isColliding(self.mario, s) and s.type == 1:
                self.colliding = True

                if self.mario.py + self.mario.height < s.y:
                    self.mario.y = s.y - self.mario.height
                    self.mario.velocity = 0
                    self.mario.framesSinceSolodGround = 0

                elif self.mario.py > s.y + s.height:
                    self.mario.y = s.y + s.height
                    self.mario.velocity = 0

                elif self.mario.px + self.mario.width < s.x:
                    self.mario.x = s.x - self.mario.width

                elif self.mario.px > s.x + s.width:
                    self.mario.x = s.x + s.width

                self.mario.framesSinceSolodGround = 0

        if not self.colliding:
            self.mario.px = self.mario.x
            self.mario.py = self.mario.y

        for s1 in self.sprites:
            for s2 in self.sprites:
                if (self.isColliding(s1, s2)):
                    if s1.type == 2 and s2.type == 1:
                        s1.movingRight = not s1.movingRight
                    if s1.type == 3 and s2.type == 2:
                        s2.onFire = True

        for s in self.sprites:
            if s.type == 2:
                if s.framesSinceOnFire > 40:
                    self.sprites.remove(s)
                    break

    def isColliding(self, s1, s2):
        if s1 == s2:
            return False
        if s1.x + s1.width < s2.x:
            return False
        if s1.x > s2.x + s2.width:
            return False
        if s1.y + s1.height < s2.y:
            return False
        if s1.y > s2.y + s2.height:
            return False
        return True


class View():
    def __init__(self, model):
        screen_size = (700, 500)
        self.screen = pygame.display.set_mode(screen_size, 32)
        self.model = model

    def update(self):
        self.screen.fill([4, 156, 216])
        pygame.draw.rect(self.screen, [67, 176, 71], (0, 400, 700, 500))
        for s in self.model.sprites:
            s.draw(self.screen, self.model.mario.x)
        pygame.display.flip()


class Controller():
    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.keep_going = True
        self.thrownFireball = False

    def update(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                self.keep_going = False
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    self.keep_going = False

        keys = pygame.key.get_pressed()

        if keys[K_LEFT] and not keys[K_RIGHT]:
            self.model.mario.x -= 4
            self.model.mario.imageIndex += 1

        elif keys[K_RIGHT] and not keys[K_LEFT]:
            self.model.mario.x += 4
            self.model.mario.imageIndex += 1

        if keys[K_SPACE] and self.model.mario.framesSinceSolidGround < 5:
            self.model.mario.velocity -= 5

        if keys[K_LCTRL] and not self.thrownFireball:
            self.thrownFireball = True
            self.model.sprites.append(
                Fireball(self.model.mario.x, self.model.mario.y + 30))

        elif not keys[K_LCTRL]:
            self.thrownFireball = False


pygame.init()
m = Model()
v = View(m)
c = Controller(m, v)
while c.keep_going:
    c.update()
    m.update()
    v.update()
    sleep(0.016)
print("Tschüss!")
