import pygame, os, sys
import _pickle as pickle
from visualize import draw_net

def handle_events():
  for event in pygame.event.get():
    if(event.type == pygame.QUIT): sys.exit() 

pygame.init()
pygame.display.set_caption('PyCritters')
pygame.display.set_mode((800, 600))
genome = load(os.path.join('savedcritters','test_output.p'))
while(1):
  handle_events()