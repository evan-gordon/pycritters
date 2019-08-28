import os, sys, pygame, random
from character import Character
from worldtype import WorldType

def spawn_critter(state, x, y, *, mode=WorldType.SURVIVAL):
  image = state.CHAR_TEXTURES[
      random.randint(0,
                     len(state.CHAR_TEXTURES) - 1)]
  return Character(image, state.day, x, y, mode=mode)

def random_position(state, minheight=0.35):
  while (1):
    x = random.randint(100, state.width - 100)
    y = random.randint(100, state.height - 100)
    if (state.world.topology[x][y] > 0.31):
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
      colorkey = image.get_at((0, 0))
    image.set_colorkey(colorkey, RLEACCEL)
  return image, image.get_rect()

def any_collide_with_point(group, x, y):
  for obj in group:
    if obj.rect.collidepoint(x, y):
      return obj
  else:
    return None
