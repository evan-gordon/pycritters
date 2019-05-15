import pygame
class GameState():
  __instance = None

  def __init__(self):
    if GameState.__instance != None:
      raise Exception("This class is a singleton!")
    else:
      GameState.__instance = self
  @staticmethod
  def getinstance():
    if(GameState.__instance == None):
      GameState()
    return GameState()

  