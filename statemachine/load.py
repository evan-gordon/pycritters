import neat, pygame, pygame_helpers
import _pickle as pickle
import reproduction
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
    state.GID_INDEX = 1
    state.NEAT_CONFIG = neat.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        "config",
    )
    # load default genome
    pickle_in = open("default_genome.p", "rb")
    default_genome = pickle.load(pickle_in)

    state.screen = pygame.display.get_surface()
    state.clock = pygame.time.Clock()
    state.new_day = False
    state.day = 1
    state.width, state.height = state.screen.get_size()
    # split work for this into processes later
    state.world = Island(state.width, state.height)

    state.sprites, state.plants = pygame.sprite.Group(
    ), pygame.sprite.Group()
    for _ in range(self.population):
      x, y = pygame_helpers.random_position(state)
      new_critter = pygame_helpers.spawn_critter(state, x, y)
      state.sprites.add(new_critter)
      # give each critter a brain based on the input one
      (genome, network) = reproduction.reproduce(
          state.NEAT_CONFIG, state.GID_INDEX, default_genome,
          default_genome
      )

      new_critter.setbrainandgenome(state.GID_INDEX, genome, network)
      state.GID_INDEX += 1
    for _ in range(self.bush_pop):
      x, y = pygame_helpers.random_position(state)
      state.plants.add(Bush(state.FOOD_TEXTURE, state.day, x, y))
    pygame.time.set_timer(pygame.USEREVENT + 1, 5000)
    print('finished loading')
    return Play()
