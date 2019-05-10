import random, math, numpy
from noise import snoise2
from pygame import PixelArray, Surface
from gameobj import GameObject

# https://www.pygame.org/docs/ref/pixelarray.html
class Island(GameObject):
  colors = {
        'green': (0, 245, 0),
        'blue': (0, 0, 245),
        'sand': (242, 215, 196)
      }

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
    print('Generating Terrain ', self.width, self.height)
    a = .53
    b = .92
    c = 0.98
    waterHeight = 0.3
    self.topology = [[0] * self.height] * self.width
    sfc = Surface((self.width, self.height))
    pa = PixelArray(sfc)
    for x in range(len(self.topology)):
      for y in range(len(self.topology[0])):
        self.topology[x][y] = self.noise(x, y)
        self.topology[x][y] += self.islandify(x, y, a, b, c)
        pa[x, y] = self.height_to_color(x, y)
    print('Finished Proc Gen')
    return pa.make_surface()

  def islandify(self, x, y, a, b, c):
    d = numpy.clip(2 * (math.hypot(self.center[0] - x, self.center[1] - y) / self.center[0]), 0, 1)
    return (a - (b * d**c))

  def pixel_array(self):
    sfc = Surface((self.width, self.height))
    pa = PixelArray(sfc)
    for x in range(len(self.topology)):
      for y in range(len(self.topology[0])):
        pa[x][y] = self.height_to_color(x, y)
    return pa.make_surface()

  def noise(self, x, y):
    r = 0.0
    newnoise = 0.0
    for i in range(self.octaves):
      newnoise = self.noise_at_point(x, y, self.scale * 2**i) * (1.0 / 2**i)
      if(i != 0):
        newnoise = (2 * newnoise) - newnoise
      r += newnoise
    return numpy.clip(r, 0, 1)

  def noise_at_point(self, x, y, frequency):
    newx = ((x + self.center[0]) / self.width) * frequency + self.seed[0]
    newy = ((y + self.center[1]) / self.height) * frequency + self.seed[1]
    noise = snoise2(newx, newy)
    return numpy.clip(noise, 0, 1)

  def height_to_color(self, x: int, y: int):
    h = self.topology[x][y]
    if(h < 0.3):
      return Island.colors['blue']
    elif(h < 0.5):
      return Island.colors['sand']
    else:
      return Island.colors['green']
