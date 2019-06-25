import pygame, math
from typing import List
from statemachine.wander_ai import WanderAI

class Character(pygame.sprite.Sprite):

  def __init__(self, image_info, birthday: int, x=0, y=0):
    pygame.sprite.Sprite.__init__(self)
    self.ismale, image = image_info
    img, rect = image
    self.texture, rect = img.copy(), rect.copy()
    self.texture.set_colorkey((0, 0, 0))
    rect.height, rect.width = rect.height / 3, rect.width / 4
    self.birthday, self.nextchild = birthday, birthday + 1
    self.hunger = 0.5
    self.fruits_eaten = 0
    self.reproduced = 0.0
    self.lifespan = 8 # days
    self.dead = False
    self.fitness = 0.0
    self.speed = .4
    self.state = WanderAI()
    self.looking_angle = 0.0
    self.x, self.y = x - int(rect.width / 2 +
                             0.5), int(y - rect.height / 2 + 0.5)
    self.rect = pygame.Rect(0, 0, rect.width, rect.height)
    self.image = self.texture.subsurface(self.rect)
    self.rect.x, self.rect.y = self.x, self.y

  def update(self, currDay, topology):
    if (currDay > self.birthday + self.lifespan):
      self.kill()
      return
    self.state = self.state.update(self)
    self.rect.x, self.rect.y = self.x, self.y
    if (not self.validlocation(topology)):
      self.kill()

  def update2(self, inputs: List[float], new_day: bool):
    """
    Update currently used for training only

    Pipe inputs into genomes.
    Use outputs to move player and update state.
    """
    if (new_day):
      self.hunger -= .2
    outputs = self.brain.activate(inputs)
    x_input, y_input = (outputs[0] * 2.0 - 1.0), (outputs[1] * 2.0 - 1.0)
    self.x += x_input * self.speed
    self.y += y_input * self.speed
    self.rect.x, self.rect.y = self.x, self.y
    self.looking_angle = math.degrees(math.atan2(y_input, x_input))
    if (self.looking_angle < 0):
      self.looking_angle += 360.0
    self.reproduced = 0.0 # could slowly reduce later..

  def eval_fitness(self, currDay: int):
    """
    Use a ratio of food eaten and length of life to measure success.

    In the future could use stats such as:
    * number children had
    """
    self.fitness = currDay / 10 + .25 * self.fruits_eaten

  def try_kill(self, height_at_current_position: float, currDay: int):
    """
    Currently critters can die by:
    * Drowning
    * Old age
    * Hunger OR Overeating
    """
    if (height_at_current_position < .05):
      self.dead = True
    if (currDay > self.birthday + self.lifespan):
      self.dead = True
    if (self.hunger < 0 or 1 < self.hunger):
      self.dead = True

  def collide(self, collisions, currDay):
    if (not self.ismale):
      for other in collisions:
        if (other.ismale):
          return self.tryhavechild(currDay)

  def collideplants(self, plants, currDay):
    for plant in plants:
      if (plant.eat(currDay)):
        self.hunger += .3
        self.fruits_eaten += 1
        return

  def tryhavechild(self, currDay: int):
    if (currDay >= self.nextchild):
      self.nextchild += 3
      self.reproduced = 1.0
      return True

  def setbrainandgenome(self, gid: int, genome, network):
    self.gid = gid
    self.genome = genome
    self.brain = network

  def getcenterlocation(self):
    return self.rect.center[0], self.rect.center[1]

  def validlocation(self, topology):
    if (
        self.rect.centerx < 0 or self.rect.centery < 0 or
        self.rect.centerx >= len(topology) or
        self.rect.centery >= len(topology[0])
    ):
      return False
    if (
        topology[int(self.rect.centerx)][int(self.rect.centery)] <
        0.3 - .03
    ): # height less than water, with some give
      return False
    return True