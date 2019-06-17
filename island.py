import random, math
import numpy as np
from noise import snoise2
from pygame import PixelArray, Surface, surfarray, Color
from gameobj import GameObject

# https://www.pygame.org/docs/ref/pixelarray.html
class Island(GameObject):

  def __init__(self, width, height):
    self.width = width
    self.height = height
    self.center = (self.width / 2.0, self.height / 2)
    self.octaves = 3
    self.scale = 5.0
    self.seed = (random.random() * 9999.0, random.random() * 9999.0)
    return super().__init__(self.generate())

  # using perlin noise generate an island with:
  # blue for water, tan for sand, and green for land
  # return surface obj with said colors, and topology 2d array
  def generate(self):
    print(f'Generating Terrain {self.width}x{self.height}')
    a, b, c = 0.78, 1.4, 1.25
    self.topology = np.ndarray((self.width, self.height, 1))
    pixel_array = np.ndarray(
        (self.topology.shape[0], self.topology.shape[1], 3)
    )
    pixels = Surface((self.topology.shape[0], self.topology.shape[1]))

    # this code needs to be vectorized
    for x in range(len(self.topology)):
      for y in range(len(self.topology[0])):
        self.topology[x][y] = self.noise(x, y)
        self.topology[x][y] += self.islandify(x, y, a, b, c)
        pixel_array[x][y] = self.height_to_color(self.topology[x][y])

    surfarray.blit_array(pixels, pixel_array)
    print('Finished Proc Gen')
    return pixels

  def islandify(self, x, y, a, b, c):
    d = np.clip(
        2 * (
            math.hypot(self.center[0] - x, self.center[1] - y) /
            self.center[0]
        ), 0, 1
    )
    return (a - (b * d**c))

  def noise(self, x, y):
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

  def height_to_color(self, height):
    if (height < 0.05):
      return (0, 0, 128) # Color('blue')
    elif (height < 0.3):
      return (240, 230, 140) # Color('khaki')
    else:
      return (0, 200, 0) # Color('green')
