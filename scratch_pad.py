# File for trying to optimize loading times

# TODO
# get numpy version of mapping function
# map values of array one to array two using function
#

import pygame, random, sys
import numpy as np
from island import Island

def handle_events():
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      sys.exit()

WIDTH, HEIGHT = 1000, 1000

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

world = Island(WIDTH, HEIGHT)

while (True):
  clock.tick(60)
  handle_events()

  screen.fill((0, 0, 0))
  screen.blit(world.img, world.pos)
  pygame.display.flip()
