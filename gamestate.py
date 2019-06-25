class GameState():
  __instance = None

  def __init__(self):
    if GameState.__instance is not None:
      raise Exception("This class is a singleton!")
    else:
      GameState.__instance = self

  @staticmethod
  def getinstance():
    if (GameState.__instance is None):
      GameState()
    return GameState.__instance
