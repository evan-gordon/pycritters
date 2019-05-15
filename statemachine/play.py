import pygame, pygame_helpers, sys
from statemachine.state_machine import StateMachine

def render_ui(state):
    ui_info = f'{round(state.clock.get_fps())}fps Day: {state.day} Population: {len(state.sprites)}'
    ui_font = state.FONT.render(ui_info, True, (0, 0, 0))
    state.screen.blit(ui_font, (0, 0))

class Play(StateMachine):
  def __init__(self, state):
    self.state = state
    self.paused = False
    StateMachine.__init__(self)

  def update(self):
    while(not self.paused):
      self.state.clock.tick(60)
      self.handle_events()

      self.state.screen.blit(self.state.world.img, self.state.world.pos)  # draw background
      self.state.sprites.update(self.state.day, self.state.world.topology)# update stuff
      self.state.plants.update(self.state.day)
      self.handle_collisions()
      self.state.sprites.draw(self.state.screen)              # draw stuff
      self.state.plants.draw(self.state.screen)
      render_ui(self.state)
      pygame.display.flip()
    return Pause(self.state)

  def handle_events(self):
    for event in pygame.event.get():
      if(event.type == pygame.QUIT): sys.exit()
      if(event.type == pygame.USEREVENT+1):
        self.state.day += 1
      if(event.type == pygame.KEYUP):
        if(event.key == pygame.K_SPACE):
          self.paused = True
      #   x, y = self.random_position()
      #   #print(f'Spawning at ({x}, {y}) height: {self.bg.topology[x][y]}')
      #   if(self.day % 2 == 0):
      #     self.sprites.add(Character(self.textures['m1'], self.day, x, y))
      #   if(self.day % 2 != 0):
      #     self.sprites.add(Character(self.textures['f1'], self.day, x, y))

  def handle_collisions(self):
    for character in self.state.sprites:
      collided_chars = pygame.sprite.spritecollide(character, self.state.sprites, False)
      if(collided_chars):
        hadchild = character.collide(collided_chars, self.state.day)
        if(hadchild):
          pygame_helpers.spawn_critter(self.state, character.x, character.y)
      collided_plants = pygame.sprite.spritecollide(character, self.state.plants, False)
      if(collided_plants):
        character.collideplants(collided_plants, self.state.day)


class Pause(StateMachine):
  def __init__(self, state):
    self.paused = True
    self.state = state
    StateMachine.__init__(self)

  def update(self):
    while(self.paused):
      self.handle_events()
      self.state.screen.blit(self.state.world.img, self.state.world.pos)  # draw background
      self.state.sprites.draw(self.state.screen)              # draw stuff
      self.state.plants.draw(self.state.screen)
      render_ui(self.state)
      pygame.display.flip()
    return Play(self.state)

  def handle_events(self):
    for event in pygame.event.get():
      if(event.type == pygame.QUIT): sys.exit()
      if(event.type == pygame.KEYUP):
        if(event.key == pygame.K_SPACE): 
          self.paused = False