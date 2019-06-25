import random, math
import numpy as np
from typing import Tuple
from noise import snoise2
from pygame import Surface, surfarray
from gameobj import GameObject

# https://www.pygame.org/docs/ref/pixelarray.html
class Island(GameObject):

  def __init__(self, width: int, height: int):
    self.width = width
    self.height = height
    self.center = (self.width / 2.0, self.height / 2)
    self.octaves = 3
    self.scale = 5.0
    self.seed = (random.random() * 9999.0, random.random() * 9999.0)
    return super().__init__(self.__generate())

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

# ====Static functions====

def rgb_to_greyscale(rgb: Tuple):
  """
  The National Telecision System Committee suggests this formual
  for optimal greyscale conversion `y = .299r + .587g + .114b`
  where rgb values are on a [0, 1] scale.
  """
  red, green, blue = rgb[0] / 255.0, rgb[1] / 255.0, rgb[2] / 255.0
  return (.299 * red) + (.587 * green) + (.114 * blue)
