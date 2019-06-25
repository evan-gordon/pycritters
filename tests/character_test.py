import pytest, neat
from pygame import Rect
from island import Island
from gamestate import GameState
from character import Character
from train import vectorize_distance_from_position, view_positions
from tests.mock_image import MockImage

CONFIG = neat.Config(
    neat.DefaultGenome,
    neat.DefaultReproduction,
    neat.DefaultSpeciesSet,
    neat.DefaultStagnation,
    "config",
)
MOCK_IMG = (True, (MockImage(), Rect(0, 0, 16, 16)))

def genome_and_network_fixture(gid: int):
  genome = neat.DefaultGenome(gid)
  genome.configure_new(CONFIG.genome_config)
  network = neat.nn.FeedForwardNetwork.create(genome, CONFIG)
  return genome, network

@pytest.mark.parametrize(
    "angle,dist,origin,expected", [
        (0, 5, (5, 5), (10, 5)), (180, 5, (5, 5), (0, 5)),
        (90, 5, (5, 5), (5, 0))
    ]
)
def test_vectorize_distance_from_critter(angle, dist, origin, expected):
  genome, network = genome_and_network_fixture(42)
  result = vectorize_distance_from_position(
      angle, dist, origin[0], origin[1]
  )
  assert expected == result

def test_view_positions():
  STATE = GameState.getinstance()
  STATE.world = Island(10, 10)
  char = Character(MOCK_IMG, 0, 5, 5)
  results = view_positions(char)
  assert (9, 9) == results[0]
  assert (10, 5) == results[2]
  assert (9, 1) == results[4]

def test_nn_output_to_view_position():
  # island = Island(10, 10)
  char = Character(MOCK_IMG, 0, 5, 5)
  genome, network = genome_and_network_fixture(42)
  char.setbrainandgenome(42, genome, network)
  assert 0 == char.looking_angle
  # observed_points = observe_world(char)

@pytest.mark.parametrize(
    "height,day,isDead",
    [(.001, 0, True), (1.0, 9, True), (1.0, 4, False)]
)
def test_can_kill(height, day, isDead):
  c = Character(MOCK_IMG, 0)
  assert not c.dead
  c.try_kill(height, day)
  assert isDead == c.dead
