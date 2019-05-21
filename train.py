import neat, pygame, random, sys
import pygame_helpers as pgh
from island import Island
from gamestate import GameState
from character import Character

FPS = 200
# try later
# 640×480, 800×600, 960×720, 1024×768, 1280×960
SCREENWIDTH  = 800
SCREENHEIGHT = 600
SCORE = 0
GENERATION = 0
MAX_FITNESS = 0
BEST_GENOME = 0
STATE = GameState()

def init_pygame():
	pygame.init()
	pygame.display.set_caption('PyCritters')
	pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))

def setup():
	STATE.FONT = pygame.font.SysFont("comicsansms", 24)
	STATE.FOOD_TEXTURE = pgh.load_image('food.png')
	STATE.CHAR_TEXTURES = [(False, pgh.load_image('F_01.png')), (True, pgh.load_image('M_01.png'))]
	STATE.screen = pygame.display.get_surface()
	STATE.clock = pygame.time.Clock()
	STATE.width, STATE.height = STATE.screen.get_size()
	STATE.world = Island(STATE.width, STATE.height)
	STATE.sprites = pygame.sprite.Group()
	pygame.time.set_timer(pygame.USEREVENT+1, 5000)
	print('finished loading')

def handle_events():
  for event in pygame.event.get():
    if(event.type == pygame.QUIT): sys.exit()
    if(event.type == pygame.USEREVENT+1):
      STATE.day += 1
    if(event.type == pygame.KEYUP):
      if(event.key == pygame.K_SPACE):
        STATE.paused = True

def game(genome, config):
	net = neat.nn.FeedForwardNetwork.create(genome, config)
	
	global SCORE
	global STATE
	x, y = pgh.random_position(STATE)
	STATE.day = 1
	STATE.player = pgh.spawn_critter(STATE, x, y)
	STATE.sprites.add(STATE.player)
	# optionally reset group upon new game

	while True:
		STATE.clock.tick(200)
		STATE.screen.blit(STATE.world.img, STATE.world.pos)
		handle_events()
		input = (STATE.world.topology[int(STATE.player.x-5)][int(STATE.player.y)],
		STATE.world.topology[int(STATE.player.x)][int(STATE.player.y-5)],
		STATE.world.topology[int(STATE.player.x+5)][int(STATE.player.y)],
		STATE.world.topology[int(STATE.player.x)][int(STATE.player.y+5)])

		#print(input)
		# calculate fitness
		fitness = SCORE + (STATE.day/10.0)

		#fail setting
		if(STATE.world.topology[int(STATE.player.x)][int(STATE.player.y)] < .05):
			return(fitness)
		
		if(STATE.day > STATE.player.birthday + STATE.player.lifespan):
			STATE.player.dead = True
			#STATE.player.kill()
			return(fitness)
		
		# pipe inputs to character
		outputs = net.activate(input)# tuple(float) -> list(float)
		STATE.player.update2(outputs)			
		

		# update world
		STATE.sprites.draw(STATE.screen)
		render_ui()
		pygame.display.flip()

def render_ui():
    ui_info = f'{round(STATE.clock.get_fps())}fps Day: {STATE.day} Population: {len(STATE.sprites)}'
    ui_font = STATE.FONT.render(ui_info, True, (0, 0, 0))
    STATE.screen.blit(ui_font, (0, 0))

def eval_genomes(genomes, config):
	i = 0
	global SCORE
	global GENERATION, MAX_FITNESS, BEST_GENOME

	GENERATION += 1
	for genome_id, genome in genomes:
		genome.fitness = game(genome, config)
		print("Gen : %d Genome # : %d  Fitness : %f Max Fitness : %f"%(GENERATION,i,genome.fitness, MAX_FITNESS))
		if genome.fitness >= MAX_FITNESS:
			MAX_FITNESS = genome.fitness
			BEST_GENOME = genome
		SCORE = 0
		i+=1

config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         'config')

init_pygame()
setup()
pop = neat.Population(config)
winner = pop.run(eval_genomes, 30)
print(winner)