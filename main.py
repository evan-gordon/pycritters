from statemachine.load import Load

if __name__ == "__main__":
  game_state = Load(500, 320, 25, 15)
  while(1):
    game_state = game_state.update()