import neat, pygame, os, sys
import _pickle as pickle
import pygame_helpers as pgh
from island import Island
from gamestate import GameState
from bush import Bush
from visualize import draw_net

FPS = 200
OUTPUT_WINNER_TO_FILE = True # False
# try later: 640×480, 800×600, 960×720, 1024×768, 1280×960
SCREENWIDTH, SCREENHEIGHT = 800, 600
BUSH_POP = 20
SCORE = 0
GENERATION = 0
MAX_FITNESS = 0
BEST_GENOME = 0
STATE = GameState()

def save_genome(genome):
  """Save genome to a .p file"""
  os.chdir("savedcritters")
  serial = len(os.listdir())
  filename = str(serial) + "_" + str(int(MAX_FITNESS))
  os.mkdir(filename)
  os.chdir(filename)
  outputfile = open(filename + ".p", "wb")
  pickle.dump(genome, outputfile)
  draw_net(config, genome, filename + ".png")
  os.chdir(os.path.join("..", ".."))

def init_pygame():
  pygame.init()
  pygame.display.set_caption("PyCritters")
  pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))

def setup():
  STATE.FONT = pygame.font.SysFont("comicsansms", 24)
  STATE.FOOD_TEXTURE = pgh.load_image("food.png")
  STATE.CHAR_TEXTURES = [
      (False, pgh.load_image("F_01.png")),
      (True, pgh.load_image("M_01.png")),
  ]
  STATE.screen = pygame.display.get_surface()
  STATE.clock = pygame.time.Clock()
  STATE.width, STATE.height = STATE.screen.get_size()
  STATE.world = Island(STATE.width, STATE.height)
  STATE.sprites = pygame.sprite.Group()
  STATE.plants = pygame.sprite.Group()
  pygame.time.set_timer(pygame.USEREVENT + 1, 5000)
  print("finished loading")

def handle_events():
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      sys.exit()
    if event.type == pygame.USEREVENT + 1:
      STATE.new_day = True
      STATE.day += 1
    if event.type == pygame.KEYUP:
      if event.key == pygame.K_SPACE:
        STATE.paused = True

def handle_paused_events():
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      sys.exit()
    if event.type == pygame.MOUSEBUTTONUP:
      x, y = event.pos
      for critter in STATE.critters:
        if critter.rect.collidepoint(x, y):
          print(
              "Selected critter: " +
              f"{critter.x}, {critter.y}, {critter.rect.center}"
          )
          STATE.selected_critter = critter
          break
      else:
        print(f"Cleared selection")
        STATE.selected_critter = None
    if event.type == pygame.KEYUP:
      if event.key == pygame.K_SPACE:
        STATE.paused = False

def handle_collisions():
  global STATE
  for character in STATE.sprites:
    collided_chars = pygame.sprite.spritecollide(
        character, STATE.sprites, False
    )
    if collided_chars:
      hadchild = character.collide(collided_chars, STATE.day)
      if hadchild:
        pgh.spawn_critter(STATE, character.x, character.y)
    collided_plants = pygame.sprite.spritecollide(
        character, STATE.plants, False
    )
    if collided_plants:
      character.collideplants(collided_plants, STATE.day)

def game(genome, config):
  global STATE
  STATE.paused = False
  STATE.day = 1
  not_extinct = True
  state = play
  while not_extinct:
    result = state(config)
    if result == "pause":
      state = pause
    elif result == "play":
      state = play
    elif result == "extinct":
      print("extinct")
      not_extinct = False
    else:
      print("ERROR: result not found")

def play(config):
  """
  Run training simulation.

  Format of critter inputs:
  * 4 points of world data
  * current angle critter is facing
  * hunger level
  """
  global STATE, MAX_FITNESS, BEST_GENOME
  global SCREENHEIGHT, SCREENWIDTH
  # optionally reset group upon new game
  view_dist = 5
  critters_still_living = True
  while critters_still_living and not STATE.paused:
    STATE.clock.tick(200)
    STATE.screen.blit(STATE.world.img, STATE.world.pos)
    handle_events()

    critters_still_living = False
    for critter in STATE.critters:
      if not critter.dead:
        # observe world
        critter_center = critter.getcenterlocation()
        genome_input = (
            STATE.world.topology[int(critter_center[0] -
                                     view_dist)][int(critter_center[1])],
            STATE.world.topology[int(critter_center[0]
                                    )][int(critter_center[1] - view_dist)],
            STATE.world.topology[int(critter_center[0] +
                                     view_dist)][int(critter_center[1])],
            STATE.world.topology[int(critter_center[0]
                                    )][int(critter_center[1] + view_dist)],
            critter.looking_angle / 360,
            critter.hunger,
        )

        critter.eval_fitness(STATE.day)
        if critter.fitness > MAX_FITNESS:
          MAX_FITNESS = critter.fitness
          BEST_GENOME = critter.brain
        # check for death
        height = STATE.world.topology[int(critter_center[0]
                                         )][int(critter_center[1] + 2)]
        critter.try_kill(height, STATE.day)
        # if(height < .05):
        # 	#print(f'{critter.x}, {critter.y} - width {critter.rect.width}')
        # 	critter.dead = True
        # if(STATE.day > critter.birthday + critter.lifespan):
        # 	critter.dead = True
        # return(fitness)
        # pipe inputs to character tuple(float) -> list(float)
        critter.update2(genome_input, STATE.new_day)
        # print(f'updated pos: {critter.x}, {critter.y}')
        if not critter.dead:
          critters_still_living = True

    # update world
    STATE.plants.update(STATE.day)
    handle_collisions()
    STATE.plants.draw(STATE.screen)
    STATE.sprites.draw(STATE.screen)
    STATE.new_day = False
    render_ui()
    pygame.display.flip()
  if not critters_still_living:
    return "extinct"
  else:
    return "pause"

def pause(config):
  global STATE
  STATE.selected_critter = None
  while STATE.paused:
    STATE.clock.tick(60)
    STATE.screen.blit(STATE.world.img, STATE.world.pos)
    handle_paused_events()
    STATE.plants.draw(STATE.screen)
    STATE.sprites.draw(STATE.screen)
    if STATE.selected_critter:
      pygame.draw.rect(
          STATE.screen, (250, 0, 0), STATE.selected_critter.rect.copy(), 2
      )
    render_ui()
    pygame.display.flip()
  STATE.selected_critter = None
  return "play"

def render_ui():
  ui_info = (
      f"{round(STATE.clock.get_fps())}fps " +
      f"Day: {STATE.day} Population: {len(STATE.sprites)}"
  )
  ui_font = STATE.FONT.render(ui_info, True, (0, 0, 0))
  STATE.screen.blit(ui_font, (0, 0))

def eval_genomes(genomes, config):
  """
  Setup world, and brains for critters.
  find and return most 'fit' critter.
  """
  global SCORE
  global GENERATION, MAX_FITNESS, BEST_GENOME
  GENERATION += 1
  global STATE
  STATE.day = 1
  STATE.new_day = False
  # create plants
  for _ in range(BUSH_POP):
    x, y = pgh.random_position(STATE)
    STATE.plants.add(Bush(STATE.FOOD_TEXTURE, STATE.day, x, y))
  # create critters
  STATE.critters = []
  for _ in range(len(genomes)):
    x, y = pgh.random_position(STATE)
    c = pgh.spawn_critter(STATE, x, y)
    STATE.critters.append(c)
    STATE.sprites.add(c)
  for (genome_id, genome), critter in zip(genomes, STATE.critters):
    critter.brain = neat.nn.FeedForwardNetwork.create(genome, config)
  game(genome, config)
  print(f"Gen : {GENERATION} Max Fitness : {MAX_FITNESS}")
  for (gene_id, gene), critter in zip(genomes, STATE.critters):
    gene.fitness = critter.fitness
  STATE.sprites.empty()
  STATE.plants.empty()

if __name__ == "__main__":
  config = neat.Config(
      neat.DefaultGenome,
      neat.DefaultReproduction,
      neat.DefaultSpeciesSet,
      neat.DefaultStagnation,
      "config",
  )

  init_pygame()
  setup()
  pop = neat.Population(config) # create population obj
  winner = pop.run(eval_genomes, 20)
  print(winner)
  if OUTPUT_WINNER_TO_FILE:
    save_genome(winner)
