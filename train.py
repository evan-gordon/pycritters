import math, neat, pygame, os, sys, numpy, visibility
import _pickle as pickle
import pygame_helpers as pgh
from worldtype import WorldType
from typing import List, Tuple
from island import Island
from gamestate import GameState
from bush import Bush
from visualize import draw_net
from gui_manager import GUIManager
import factory

FPS = 200
OUTPUT_WINNER_TO_FILE = False
# try later: 640×480, 800×600, 960×720, 1024×768, 1280×960
SCREENWIDTH, SCREENHEIGHT = 960, 720
BUSH_POP = 15
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
  # STATE.world = Island(STATE.width, STATE.height)
  STATE.sprites = pygame.sprite.Group()
  STATE.plants = pygame.sprite.Group()
  STATE.GUIMANAGER = GUIManager()
  (id, cbox) = factory.create_ui(
      "checkbox", manager=STATE.GUIMANAGER, id="show_directions", y=16
  )
  print(id)
  print(str(cbox))
  pygame.time.set_timer(pygame.USEREVENT + 1, 5000)

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
  global STATE
  events = pygame.event.get()
  for event in events:
    if event.type == pygame.QUIT:
      sys.exit()
    if event.type == pygame.MOUSEBUTTONUP:
      selection = visibility.any_collide_with_point(STATE.critters, event.pos)
      if (selection is not None):
        print(
            "Selected critter: " + f"center: {selection.rect.center}, " +
            f"looking_direction: {selection.looking_angle}"
        )
        STATE.selected_critter = selection
      else:
        print(f"Cleared selection")
        STATE.selected_critter = None
    if event.type == pygame.KEYUP:
      if event.key == pygame.K_SPACE:
        STATE.paused = False
  STATE.GUIMANAGER.update(events)

def handle_collisions():
  global STATE
  for character in STATE.sprites:
    collided_chars = pygame.sprite.spritecollide(
        character, STATE.sprites, False
    )
    if collided_chars:
      (_partner, _hadchild) = character.collide(collided_chars, STATE.day)
      # if hadchild:
      #   pgh.spawn_critter(STATE, character.x, character.y)
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
  Returns when all critters have died.

  Format of critter inputs:
  * 5 points of world data, (distance, red, green, blue)
  * current angle critter is facing
  * hunger level
  * if the critter has reproduced
  """
  global STATE, MAX_FITNESS, BEST_GENOME
  global SCREENHEIGHT, SCREENWIDTH

  # tmp
  # x, y = int(STATE.width / 2.0), int(STATE.height / 2.0)
  # STATE.borg = pgh.spawn_critter(STATE, x, y)
  # collective = pygame.sprite.Group()
  # collective.add(STATE.borg)

  # optionally reset group upon new game
  critters_still_living = True
  while critters_still_living and not STATE.paused:
    STATE.clock.tick(200)
    STATE.screen.blit(STATE.world.img, STATE.world.pos)
    handle_events()
    # tmp
    # STATE.borg.rotate(-0.5)

    critters_still_living = False
    for critter in STATE.critters:
      if (not critter.dead): # use continue here instead of not.. haha
        # observe world
        critter_center = critter.getcenterlocation()
        # trace rays of view into the world with different colors for:
        # * other characters
        # * food
        # * different types of terrain
        point_colors = observe_world(critter)
        curr_height = STATE.world.topology[int(
            critter_center[0]
        )][int(critter_center[1] + 2)]

        # TODO for every rgb value need to also add a distance value
        # if this solution works i could also look into 3 vs 5 input points
        genome_input = (
            point_colors[0][0], point_colors[0][1],
            point_colors[0][2], point_colors[1][0],
            point_colors[1][1], point_colors[1][2],
            point_colors[2][0], point_colors[2][1],
            point_colors[2][2], point_colors[3][0],
            point_colors[3][1], point_colors[3][2],
            point_colors[4][0], point_colors[4][1],
            point_colors[4][2], critter.looking_angle / 360,
            critter.hunger, critter.reproduced
        )

        # record fitness
        critter.eval_fitness(STATE.day)
        if (critter.fitness > MAX_FITNESS):
          MAX_FITNESS = critter.fitness
          BEST_GENOME = critter.brain

        if (not critter.try_kill(curr_height, STATE.day)):
          critter.update(genome_input, STATE.new_day)
          updated_center = critter.getcenterlocation()
          if(
              STATE.mode != WorldType.SURVIVAL and
              STATE.world.topology[int(updated_center[0]
              )][int(updated_center[1] + 2)] < 0.05
          ):
            x, y = back_to_land(updated_center)
            critter.teleport(x, y)
          critters_still_living = True
        else:
          STATE.critters.remove(critter)
          STATE.sprites.remove(critter)

    # update world
    STATE.plants.update(STATE.day)
    handle_collisions()
    STATE.plants.draw(STATE.screen)
    STATE.sprites.draw(STATE.screen)
    if (STATE.GUIMANAGER.get_widget("show_directions").enabled):
      draw_sprite_directions(STATE.sprites)

    # tmp
    # collective.draw(STATE.screen)
    # draw_raycast_directions(collective)

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
      for observed_pos in STATE.selected_critter.observed_positions:
        draw_line(STATE.selected_critter.getcenterlocation(), observed_pos)
        
    if (STATE.GUIMANAGER.get_widget("show_directions").enabled):
      draw_sprite_directions(STATE.sprites)
    render_ui()
    STATE.GUIMANAGER.draw(STATE.screen)
    pygame.display.flip()
  STATE.selected_critter = None
  return "play"

def render_ui():
  ui_info = (
      f"{round(STATE.clock.get_fps())}fps " +
      f"Generation: {GENERATION} " + f"Max Fitness: {MAX_FITNESS}" +
      f"Day: {STATE.day} " + f"Population: {len(STATE.sprites)}"
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
    c = pgh.spawn_critter(STATE, x, y, mode=STATE.mode)
    STATE.critters.append(c)
    STATE.sprites.add(c)
  for (genome_id, genome), critter in zip(genomes, STATE.critters):
    network = neat.nn.FeedForwardNetwork.create(genome, config)
    critter.setbrainandgenome(genome_id, genome, network)
  game(genome, config)
  print(f"Gen : {GENERATION} Max Fitness : {MAX_FITNESS}")
  for (gene_id, gene), critter in zip(genomes, STATE.critters):
    gene.fitness = critter.fitness
  STATE.sprites.empty()
  STATE.plants.empty()

def draw_sprite_directions(group):
  global STATE
  for sprite in group:
    center = sprite.getcenterlocation()
    point = vectorize_distance_from_position(
        sprite.looking_angle, 15, center[0], center[1]
    )
    draw_line(center, point)

def draw_raycast_directions(group):
  global STATE
  for sprite in group:
    center = sprite.getcenterlocation()
    ray = visibility.ray_cast(
        sprite, sprite.looking_angle, int(STATE.width / 2.0),
        STATE.critters,
        STATE.plants,
        STATE.world
    )
    draw_line(center, ray[1])

def draw_line(source, dest, *, color=(250, 0, 0)):
  global STATE
  pygame.draw.line(
      STATE.screen, color, source, dest
  )

# def view_positions(critter, view_dist=15) -> List[Tuple]:
#   """
#   Given a critter return:
#   list of points where was last looking
#   """
#   global STATE
#   starting_angle = critter.looking_angle - 45.0
#   critter_center = critter.getcenterlocation()
#   observed_points = []
#   for _ in range(5):
#     (x, y) = vectorize_distance_from_position(
#         starting_angle, view_dist, critter_center[0], critter_center[1]
#     )
#     observed_points.append(
#         (numpy.clip(x, 0, STATE.width), numpy.clip(y, 0, STATE.height))
#     )
#     starting_angle += 22.5
#   return observed_points

def observe_world(critter, view_dist=15) -> List[Tuple]:
  """
  Given a critter at a certain location
  cast rays in a view cone.
  Map those points onto the `world` map
  and get colors at those points.
  If that point intersects with a critter
  or plant (apple) then change color accordingly.
  """
  global STATE
  starting_angle = critter.looking_angle - 45.0
  observed_points = []
  critter.observed_positions = []

  for _ in range(5):
    ray = visibility.ray_cast(
        critter, starting_angle, int(STATE.width / 2.0),
        STATE.critters,
        STATE.plants,
        STATE.world
    )
    observed_points.append(ray[2])
    critter.observed_positions.append(ray[1])
    starting_angle += 22.5
  return observed_points

def back_to_land(position, bounce_dist=6):
  """
  Tries to find a position in a radius of bounce_dist units that's above water.
  Otherwise selects middle of the map.
  Return that position.
  """
  bounce_dist = numpy.clip(bounce_dist, 0, sys.maxsize)
  global STATE
  diag = int(math.sqrt(2.0 * (bounce_dist ** 2.0)) + .5)
  OFFSETS = [
      (bounce_dist, 0), (-bounce_dist, 0), (0, bounce_dist), (0, -bounce_dist),
      (-diag, -diag), (-diag, diag), (diag, -diag), (diag, diag)
  ]
  for x_offset, y_offset in OFFSETS:
    if(
        0.05 < STATE.world.topology[int(
            numpy.clip(position[0] + x_offset, 0, STATE.width))][int(
            numpy.clip(position[1] + y_offset, 0, STATE.height))]
    ):
      return position[0] + x_offset, position[1] + y_offset
  return int(STATE.width / 2.0), int(STATE.height / 2.0)

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

if __name__ == "__main__":
  init_pygame()
  setup()
  # global STATE
  # current_best = neat.DefaultGenome
  print("finished loading")
  # for _, member in WorldType.__members__.items():
  STATE.mode = WorldType.FOOD # member
  print(f'Setting mode to: {STATE.mode}')
  STATE.world = Island(STATE.width, STATE.height, type=STATE.mode)
  BUSH_POP = 40
  config = neat.Config(
      neat.DefaultGenome, # current_best,
      neat.DefaultReproduction,
      neat.DefaultSpeciesSet,
      neat.DefaultStagnation,
      "config",
  )
  pop = neat.Population(config) # create population obj
  winner = pop.run(eval_genomes, 75)
  BUSH_POP = 20
  print(config.genome_type)
  # if similar change set genome type to winner
  print(winner)
  if OUTPUT_WINNER_TO_FILE:
    save_genome(winner)
