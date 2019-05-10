import pygame

class GameObject:
  def __init__(self, image, pos=(0, 0)):
    self.img = image
    self.pos = pos
    
  def move(self):
    pass