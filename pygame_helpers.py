import os, sys, pygame, random
from character import Character

def spawn_critter(state, x, y):
  image = state.CHAR_TEXTURES[random.randint(0, len(state.CHAR_TEXTURES) - 1)]
  return Character(image, state.day, x, y)

def random_position(state, minheight=0.31):
  while(1):
    x, y = random.randint(20, state.width - 21), random.randint(20, state.height - 21)
    if(state.world.topology[x][y] > 0.31):
      return x, y

def load_image(name, colorkey=None):
  try:
    fullname = os.path.join('images', name)
    image = pygame.image.load(fullname).convert()
  except:
    print('Cannot load image:', fullname)
    sys.exit(-1)
  image = image.convert()
  if colorkey is not None:
    if colorkey is -1:
      colorkey = image.get_at((0,0))
    image.set_colorkey(colorkey, RLEACCEL)
  return image, image.get_rect()