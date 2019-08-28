import pygame, math, numpy
from typing import List
from worldtype import WorldType

class Character(pygame.sprite.Sprite):

  def __init__(
      self,
      image_info,
      birthday: int,
      x=0,
      y=0,
      *,
      mode=WorldType.SURVIVAL
  ):
    pygame.sprite.Sprite.__init__(self)
    self.mode = mode
    self.ismale, image = image_info
    img, rect = image
    self.texture, rect = img.copy(), rect.copy()
    self.texture.set_colorkey((0, 0, 0))
    rect.height, rect.width = rect.height / 3, rect.width / 4
    self.birthday, self.nextchild = birthday, birthday + 1
    self.hunger = 0.5
    self.hunger_decay_rate = 0.1
    self.max_hunger = 2.0
    self.fruits_eaten, self.children_had = 0, 0
    self.reproduced = 0.0
    self.lifespan = 10 # days, set different for different modes
    self.dead = False
    self.fitness = 0.0
    self.speed = .4
    self.looking_angle = 0.0
    self.observed_positions = []
    self.x, self.y = x - int(rect.width / 2 +
                             0.5), int(y - rect.height / 2 + 0.5)
    self.rect = pygame.Rect(0, 0, rect.width, rect.height)
    self.image = self.texture.subsurface(self.rect)
    self.rect.x, self.rect.y = self.x, self.y

  def update(self, inputs: List[float], new_day: bool):
    """
    Pipe inputs into genomes.
    Use outputs to move player and update state.
    """
    if (new_day):
      self.hunger -= self.hunger_decay_rate
    outputs = self.brain.activate(inputs)
    self.move_rotation_mag_outputs(outputs)
    self.reproduced = max(self.reproduced - 0.5, 0.0)

  def eval_fitness(self, currDay: int) -> float:
    """
    Use a ratio of
    * food eaten
    * length of life
    * number children had
    to measure success.
    """
    if (self.mode == WorldType.FOOD):
      self.fitness = self.fruits_eaten
    elif (self.mode == WorldType.SURVIVAL):
      self.fitness = currDay / 10 + self.fruits_eaten + \
        (self.children_had * 10.0) ** 2
    self.genome.fitness = self.fitness

  def try_kill(
      self, height_at_current_position: float, currDay: int
  ) -> bool:
    """
    Currently critters can die by:
    * Drowning (survival)
    * Old age
    * Hunger OR Overeating
    """
    if (
        self.mode == WorldType.SURVIVAL and
        height_at_current_position < .05
    ):
      self.dead = True
    if (currDay > self.birthday + self.lifespan):
      self.dead = True
    if (self.hunger < 0 or self.max_hunger < self.hunger):
      self.dead = True
    return self.dead

  def move(self, x, y):
    self.x += x * self.speed
    self.y += y * self.speed
    self.rect.x, self.rect.y = self.x, self.y
    self.looking_angle = math.degrees(math.atan2(y, x))
    if (self.looking_angle < 0.0):
      self.looking_angle += 360.0

  def teleport(self, x, y):
    self.x, self.y = x, y
    self.rect.x, self.rect.y = x, y

  def rotate(self, degrees: float):
    self.looking_angle += degrees
    if (self.looking_angle < 0.0):
      self.looking_angle += 360.0
    elif (self.looking_angle > 360.0):
      self.looking_angle -= 360.0

  def collide(self, collisions, currDay):
    if (not self.ismale):
      for other in collisions:
        if (other.ismale):
          return (other, self.tryhavechild(currDay))
    return (None, False)

  def collideplants(self, plants, currDay):
    for plant in plants:
      if (plant.eat(currDay)):
        self.hunger += .2
        self.fruits_eaten += 1
        return

  def tryhavechild(self, currDay: int) -> bool:
    had_child = currDay >= self.nextchild
    if (had_child):
      self.nextchild += 2
      self.reproduced = 1.0
      self.children_had += 1
    return had_child

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

  def move_xy_outputs(self, outputs):
    """
    Map x and y network outputs to x and y [-1, 1] vectors.
    """
    x, y = (outputs[0] * 2.0 - 1.0), (outputs[1] * 2.0 - 1.0)
    self.move(x, y)

  def move_rotation_mag_outputs(self, outputs):
    """
    Map left right and forward movement vector outputs to x, y movement.
    Currently critters can turn up to 1 deg per update.
    """
    # outputs, left, right magnitude
    left = lower_dclip(outputs[0], .15, 1.0, 0.0)
    right = lower_dclip(outputs[1], .15, 1.0, 0.0)
    magnitude = lower_dclip(outputs[2], .15, 1.0, 0.0)
    self.rotate(right - left)
    rads = math.radians(self.looking_angle)
    delta_x = math.cos(rads) * magnitude
    delta_y = math.sin(rads) * magnitude
    self.x += delta_x * self.speed
    self.y += delta_y * self.speed
    self.rect.x, self.rect.y = self.x, self.y

  def move_rotation_mag_outputs_single(self, outputs):
    """
    Map single rotation vector (w/ deadzone) and movement vector
    outputs to x, y movement
    """
    # outputs rotation, magnitude
    pass

def lower_dclip(value, lower_bound, upper_bound, lower_default):
  """
  Restrict value to [lower_bound, upper_bound]
  if value is less than lower_bound, lower_default is returned
  """
  if (value < lower_bound):
    return lower_default
  elif (upper_bound < value):
    return upper_bound
  return value

def upper_dclip(value, lower_bound, upper_bound, upper_default):
  """
  Restrict value to [lower_bound, upper_bound]
  if value is more than upper_bound, upper_default is returned
  """
  if (value < lower_bound):
    return lower_bound
  if (upper_bound < value):
    return upper_default
  return value
