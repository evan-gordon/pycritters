import random, math
from oven_timer import OvenTimer
from statemachine.state_machine import StateMachine

class WanderAI(StateMachine):
  def __init__(self):
    StateMachine.__init__(self)
    self.timer = OvenTimer(random.randint(1000, 4000))
    self.speed = .4
    self.angle = random.randint(0, 360)
    self.x_vec = math.cos(self.angle) * self.speed
    self.y_vec = math.sin(self.angle) * self.speed

  def update(self, character):
    character.x += self.x_vec
    character.y += self.y_vec
    if(self.timer.isended()):
      return WaitAI()
    return self

class WaitAI(StateMachine):
  def __init__(self):
    StateMachine.__init__(self)
    self.timer = OvenTimer(random.randint(1000, 4000))

  def update(self, character):
    if(self.timer.isended()):
      return WanderAI()
    return self