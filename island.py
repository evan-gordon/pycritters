import random, math
import numpy as np
from typing import List, Tuple
# from enum import Enum, auto
from worldtype import WorldType
from noise import snoise2
from pygame import Surface, surfarray
from gameobj import GameObject
import pygame_helpers as pgh

# https://www.pygame.org/docs/ref/pixelarray.html
class Island(GameObject):

  def __init__(self, width: int, height: int, *, type=WorldType.SURVIVAL):
    self.width = width
    self.height = height
    self.center = (self.width / 2.0, self.height / 2)
    self.octaves = 3
    self.scale = 5.0
    self.seed = (random.random() * 9999.0, random.random() * 9999.0)
    if (type == WorldType.SURVIVAL):
      return super().__init__(self.__generate())
    else:
      return super().__init__(self.__generate_basic())

  # using perlin noise generate an island with:
  # blue for water, tan for sand, and green for land
  # return surface obj with said colors, and topology 2d array
  def __generate(self):
    print(f'Generating Terrain {self.width}x{self.height}')
    a, b, c = 0.78, 1.4, 1.25
    self.topology = np.ndarray((self.width, self.height, 1))
    pixel_array = np.ndarray(
        (self.topology.shape[0], self.topology.shape[1], 3)
    )
    background_surface = Surface(
        (self.topology.shape[0], self.topology.shape[1])
    )

    # this code needs to be vectorized
    for x in range(len(self.topology)):
      for y in range(len(self.topology[0])):
        self.topology[x][y] = self.noise(x, y)
        self.topology[x][y] += self.__islandify(x, y, a, b, c)
        pixel_array[x][y] = self.height_to_color(self.topology[x][y])

    surfarray.blit_array(background_surface, pixel_array)
    print('Finished Proc Gen')
    return background_surface

  def __generate_basic(self):
    print(f'Generating Basic Terrain {self.width}x{self.height}')
    self.topology = np.ndarray((self.width, self.height, 1))
    pixel_array = np.ndarray(
        (self.topology.shape[0], self.topology.shape[1], 3)
    )
    background_surface = Surface(
        (self.topology.shape[0], self.topology.shape[1])
    )

    water_width = int(self.width / 12.0)
    water_height = int(self.height / 12.0)
    for x in range(len(self.topology)):
      for y in range(len(self.topology[0])):
        if (
            x < water_width or x > self.width - water_width or
            y < water_height or y > self.height - water_height
        ):
          self.topology[x][y] = 0.04
        else:
          self.topology[x][y] = 0.6
        pixel_array[x][y] = self.height_to_color(self.topology[x][y])

    surfarray.blit_array(background_surface, pixel_array)
    print('Finished Proc Gen')
    return background_surface

  def __islandify(self, x: int, y: int, a: float, b: float, c: float):
    d = np.clip(
        2 * (
            math.hypot(self.center[0] - x, self.center[1] - y) /
            self.center[0]
        ), 0, 1
    )
    return (a - (b * d**c))

  def noise(self, x: int, y: int):
    r = 0.0
    newnoise = 0.0
    for i in range(self.octaves):
      newnoise = self.noise_at_point(x, y,
                                     self.scale * 2**i) * (1.0 / 2**i)
      if (i != 0):
        newnoise = (2 * newnoise) - newnoise
      r += newnoise
    return np.clip(r, 0, 1)

  def noise_at_point(self, x, y, frequency):
    newx = ((x + self.center[0]) / self.width) * frequency + self.seed[0]
    newy = ((y + self.center[1]) / self.height) * frequency + self.seed[1]
    noise = snoise2(newx, newy)
    return np.clip(noise, 0, 1)

  def get_info_at(self, x: int, y: int):
    """
    return tuple of:
    * height at point
    * color at point
    """
    x, y = np.clip(x, 0, self.width - 1), np.clip(y, 0, self.height - 1)
    return (self.topology[x][y], self.get_color_at(x, y))

  # WHITE = (255, 255, 255)
  def height_to_color(self, height: float):
    if (height < 0.05):
      return (0, 0, 128) # Color('blue')
    elif (height < 0.3):
      return (240, 230, 140) # Color('khaki')
    else:
      return (0, 200, 0) # Color('green')

  def get_color_at(self, x: int, y: int):
    """
    Returns RGBA value at a point
    """
    return self.img.get_at((x, y))

  def get_greyscale_at(self, x: int, y: int):
    rgb = self.get_color_at(x, y)
    return rgb_to_greyscale(rgb)

  def view_positions(self, critter, view_dist=15) -> List[Tuple]:
    """
    Given a critter at a certain location
    return a list of points where it is looking
    """
    # global STATE
    starting_angle = critter.looking_angle - 45.0
    critter_center = critter.getcenterlocation()
    observed_points = []
    for _ in range(5):
      point = vectorize_distance_from_position(
          starting_angle, view_dist, critter_center[0], critter_center[1]
      )
      observed_points.append(point)
      starting_angle += 22.5
    return observed_points

  def observe_world(self, state, critter, view_dist=15) -> List[float]:
    """
    Given a critter at a certain location
    calculate points in a view cone.
    Map those points onto the `world` map
    and get colors at those points.
    If that point intersects with a critter
    or a plant (apple) then change color
    accordingly.
    """
    starting_angle = critter.looking_angle - 45.0
    critter_center = critter.getcenterlocation()
    observed_points = []

    for _ in range(5):
      (observed_x, observed_y) = vectorize_distance_from_position(
          starting_angle, view_dist, critter_center[0], critter_center[1]
      )
      if (
          pgh.any_collide_with_point(state.plants, observed_x, observed_y)
          is not None
      ):
        greyscale = rgb_to_greyscale((250, 0, 0))
      elif (
          pgh.any_collide_with_point(
              state.sprites, observed_x, observed_y
          ) is not None
      ):
        greyscale = rgb_to_greyscale((255, 255, 255))
      else:
        greyscale = self.get_greyscale_at(observed_x, observed_y)

      observed_points.append(greyscale)
      starting_angle += 22.5
    return observed_points

# ====Static functions====

def rgb_to_greyscale(rgb: Tuple):
  """
  The National Telecision System Committee suggests this formual
  for optimal greyscale conversion `y = .299r + .587g + .114b`
  where rgb values are on a [0, 1] scale.
  """
  red, green, blue = rgb[0] / 255.0, rgb[1] / 255.0, rgb[2] / 255.0
  return (.299 * red) + (.587 * green) + (.114 * blue)

def vectorize_distance_from_position(angle_deg, hyp, originx, originy):
  """
  Given an angle and a magnitude map that vector to a x,y coord

  x axis needs output flipped due to cos of 0 or up being positive
  """
  angle_rads = math.radians(angle_deg)
  return (
      int(math.cos(angle_rads) * hyp + originx + 0.5),
      int((-1 * math.sin(angle_rads) * hyp) + originy + 0.5)
  )