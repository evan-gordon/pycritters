import pygame
from gamestate import GameState
from statemachine.load import Load

if __name__ == "__main__":
  pygame.init()
  pygame.display.set_caption('PyCritters')
  pygame.display.set_mode((500, 320))
  state = GameState()
  sim = Load(25, 15)
  while(1):
    sim = sim.update(state)