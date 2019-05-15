import os, sys, pygame, random, pygame_helpers#, config
from island import Island
from bush import Bush
from gamestate import GameState
from statemachine.state_machine import StateMachine
from statemachine.play import Play

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

class Load(StateMachine):
  def __init__(self, width, height, population, bush_pop):
    pygame.init()
    pygame.display.set_caption('PyCritters')
    pygame.display.set_mode((width, height))
    self.population = population
    self.bush_pop = bush_pop
    StateMachine.__init__(self)

  def update(self):
    state = GameState()
    state.FONT = pygame.font.SysFont("comicsansms", 24)
    state.FOOD_TEXTURE = load_image('food.png')
    state.CHAR_TEXTURES = [(False, load_image('F_01.png')), (True, load_image('M_01.png'))]
    state.screen = pygame.display.get_surface()
    state.day = 1
    state.width, state.height = state.screen.get_size()#split work for this into processes
    state.world = Island(state.width, state.height)
    state.clock = pygame.time.Clock()
    state.sprites = pygame.sprite.Group()
    state.plants = pygame.sprite.Group()
    for i in range(self.population):
      x, y = pygame_helpers.random_position(state)
      state.sprites.add(pygame_helpers.spawn_critter(state, x, y))
    for i in range(self.bush_pop):
      x, y = pygame_helpers.random_position(state)
      state.plants.add(Bush(state.FOOD_TEXTURE, state.day, x, y))
    pygame.time.set_timer(pygame.USEREVENT+1, 5000)
    print('finished loading')
    return Play(state)