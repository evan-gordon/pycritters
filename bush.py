import pygame, random

class Bush(pygame.sprite.Sprite):

  def __init__(self, image_info, currday, x=0, y=0):
    pygame.sprite.Sprite.__init__(self)
    self.ripeness = min(max(0.3, random.random()), 1.0)
    self.nextgrowth = currday + 1
    self.original_image, self.original_rect = self.setup_sprite(image_info)
    self.image = self.original_image.copy()
    self.rect = self.original_rect.copy()
    self.x, self.y = x - self.rect.width / 2, y - self.rect.height / 2
    self.rect.x, self.rect.y = self.x, self.y
    self.set_ripeness()

  def setup_sprite(self, image_info):
    img, rect = image_info
    self.texture, rect = img.copy(), rect.copy()
    self.texture.set_colorkey((0, 0, 0))
    sprite_width, sprite_height = rect.width / 8, rect.height / 8
    rect.width, rect.height = sprite_width, sprite_height
    rect.topleft = (sprite_width * 4, sprite_height)
    return self.texture.subsurface(rect), rect.copy()

  def update(self, currDay):
    self.rect.x, self.rect.y = self.x, self.y
    if (currDay >= self.nextgrowth and self.ripeness <= 1):
      self.nextgrowth += 1
      self.ripeness = round(self.ripeness + 0.1, 1)
      self.set_ripeness()

  def set_ripeness(self):
    self.image = self.original_image.copy()
    self.image = pygame.transform.scale(
        self.image, (
            int(self.rect.width * self.ripeness
               ), int(self.rect.height * self.ripeness)
        )
    )

  def eat(self, currDay: int):
    if (self.ripeness <= .6):
      return False
    self.nextgrowth = currDay + 1
    self.ripeness = 0.1
    self.set_ripeness()
    self.kill()
    return True

  def collide(self, collision, currDay):
    pass
