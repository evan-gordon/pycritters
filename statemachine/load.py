import pygame, pygame_helpers
from island import Island
from bush import Bush
from statemachine.state_machine import StateMachine
from statemachine.play import Play

class Load(StateMachine):

  def __init__(self, population, bush_pop):
    self.population = population
    self.bush_pop = bush_pop
    StateMachine.__init__(self)

  def update(self, state):
    state.FONT = pygame.font.SysFont("comicsansms", 24)
    state.FOOD_TEXTURE = pygame_helpers.load_image('food.png')
    state.CHAR_TEXTURES = [
        (False, pygame_helpers.load_image('F_01.png')),
        (True, pygame_helpers.load_image('M_01.png'))
    ]
    state.screen = pygame.display.get_surface()
    state.clock = pygame.time.Clock()
    state.day = 1
    state.width, state.height = state.screen.get_size()
    # split work for this into processes later
    state.world = Island(state.width, state.height)
    state.sprites, state.plants = pygame.sprite.Group(
    ), pygame.sprite.Group()
    for _ in range(self.population):
      x, y = pygame_helpers.random_position(state)
      state.sprites.add(pygame_helpers.spawn_critter(state, x, y))
    for _ in range(self.bush_pop):
      x, y = pygame_helpers.random_position(state)
      state.plants.add(Bush(state.FOOD_TEXTURE, state.day, x, y))
    pygame.time.set_timer(pygame.USEREVENT + 1, 5000)
    print('finished loading')
    return Play()
