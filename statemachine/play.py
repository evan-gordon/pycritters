import pygame, pygame_helpers, sys
import reproduction
from statemachine.state_machine import StateMachine

def render_ui(state):
  ui_info = (
      f"{round(state.clock.get_fps())}fps " +
      f"Day: {state.day} Population: {len(state.sprites)}"
  )
  ui_font = state.FONT.render(ui_info, True, (0, 0, 0))
  state.screen.blit(ui_font, (0, 0))

class Play(StateMachine):

  def __init__(self):
    self.paused = False
    StateMachine.__init__(self)

  def update(self, state):
    while (not self.paused):
      state.clock.tick(60)
      state.screen.blit(state.world.img, state.world.pos) # draw background
      self.handle_events(state)

      for critter in state.sprites:
        critter_center = critter.getcenterlocation()
        curr_height = state.world.topology[int(
            critter_center[0]
        )][int(critter_center[1] + 2)]
        observed_points = state.world.observe_world(state, critter)
        genome_input = (
            observed_points[0], observed_points[1], observed_points[2],
            observed_points[3], observed_points[4],
            critter.looking_angle / 360, critter.hunger, critter.reproduced
        )

        if (critter.try_kill(curr_height, state.day)):
          state.sprites.remove(critter)
        else:
          critter.update(genome_input, state.new_day)
      state.plants.update(state.day)
      state.new_day = False
      self.handle_collisions(state)
      state.sprites.draw(state.screen) # draw stuff
      state.plants.draw(state.screen)
      render_ui(state)
      pygame.display.flip()
    return Pause()

  def handle_events(self, state):
    for event in pygame.event.get():
      if (event.type == pygame.QUIT):
        sys.exit()
      if (event.type == pygame.USEREVENT + 1):
        state.day += 1
        state.new_day = True
      if (event.type == pygame.KEYUP):
        if (event.key == pygame.K_SPACE):
          self.paused = True

  def handle_collisions(self, state):
    for character in state.sprites:
      collided_chars = pygame.sprite.spritecollide(
          character, state.sprites, False
      )
      if (collided_chars):
        (repro_partner,
         hadchild) = character.collide(collided_chars, state.day)
        if (hadchild):
          character.eval_fitness(state.day)
          repro_partner.eval_fitness(state.day)
          new_child = pygame_helpers.spawn_critter(
              state, character.x, character.y
          )

          (genome, network) = reproduction.reproduce(
              state.NEAT_CONFIG, state.GID_INDEX, character.genome,
              repro_partner.genome
          )

          new_child.setbrainandgenome(state.GID_INDEX, genome, network)
          state.GID_INDEX += 1

      collided_plants = pygame.sprite.spritecollide(
          character, state.plants, False
      )
      if (collided_plants):
        character.collideplants(collided_plants, state.day)

class Pause(StateMachine):

  def __init__(self):
    self.paused = True
    StateMachine.__init__(self)

  def update(self, state):
    while (self.paused):
      state.clock.tick(60)
      self.handle_events()

      state.screen.blit(state.world.img, state.world.pos) # draw background
      state.sprites.draw(state.screen) # draw stuff
      state.plants.draw(state.screen)
      render_ui(state)
      pygame.display.flip()
    return Play()

  def handle_events(self):
    for event in pygame.event.get():
      if (event.type == pygame.QUIT):
        sys.exit()
      if (event.type == pygame.KEYUP):
        if (event.key == pygame.K_SPACE):
          self.paused = False
