import pygame
from wander_ai import WanderAI, WaitAI
class Character(pygame.sprite.Sprite):
  def __init__(self, image_info, birthday, x=0, y=0):
    pygame.sprite.Sprite.__init__(self)
    img, rect = image_info
    self.texture, rect = img.copy(), rect.copy()
    rect.height = rect.height / 3
    rect.width = rect.width / 4
    self.birthday = birthday
    self.lifespan = 5 # days
    self.state = WaitAI()#WanderAI()
    self.x = x - rect.width / 2
    self.y = y - rect.height / 2
    self.texture.set_colorkey((0, 0, 0))
    
    self.rect = pygame.Rect(0, 0, rect.width, rect.height)
    self.rect.center = (self.rect.width / 2,  self.rect.height / 2 )
    self.image = self.texture.subsurface(self.rect)

  def update(self, currDay, topology):
    if(currDay > self.birthday + self.lifespan):
      self.kill()
      return
    self.state = self.state.update(self)
    self.rect.x = self.x
    self.rect.y = self.y
    if(not self.validlocation(topology)):
      self.kill()

# could i have x and y swapped for location?
  def validlocation(self, topology):
    if(self.rect.centerx < 0 or self.rect.centery < 0 or 
          self.rect.centerx >= len(topology) or self.rect.centery  >= len(topology[0])):
      return False
    if(topology[int(self.rect.centerx)][int(self.rect.centery)] < 0.3):
      return False
    return True