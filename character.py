import pygame
from wander_ai import WanderAI, WaitAI

class Character(pygame.sprite.Sprite):
  def __init__(self, image_info, birthday, x=0, y=0):
    pygame.sprite.Sprite.__init__(self)
    self.ismale, image = image_info
    img, rect = image
    self.texture, rect = img.copy(), rect.copy()
    self.texture.set_colorkey((0, 0, 0))
    rect.height, rect.width = rect.height / 3, rect.width / 4
    self.birthday, self.nextchild = birthday, birthday + 1
    self.lifespan = 5 # days
    self.state = WanderAI()
    self.x, self.y = x - rect.width / 2, y - rect.height / 2
    self.rect = pygame.Rect(0, 0, rect.width, rect.height)
    self.rect.center = (self.rect.width / 2,  self.rect.height / 2 )
    self.image = self.texture.subsurface(self.rect)

  def update(self, currDay, topology):
    if(currDay > self.birthday + self.lifespan):
      self.kill()
      return
    self.state = self.state.update(self)
    self.rect.x, self.rect.y = self.x, self.y
    if(not self.validlocation(topology)):
      self.kill()

  def collide(self, collisions, currDay):
    if(not self.ismale):
      for other in collisions:
        if(other.ismale):
          return self.tryhavechild(currDay)

  def collideplants(self, plants, currDay):
    for plant in plants:
      if(plant.eat(currDay)):
        # increase motabolism
        return

  def tryhavechild(self, currDay):
    if(currDay >= self.nextchild):
      self.nextchild += 3
      return True

  def validlocation(self, topology):
    if(self.rect.centerx < 0 or self.rect.centery < 0 or 
          self.rect.centerx >= len(topology) or self.rect.centery  >= len(topology[0])):
      return False
    if(topology[int(self.rect.centerx)][int(self.rect.centery)] < 0.3 - .03):# height less than water, with some give
      return False
    return True