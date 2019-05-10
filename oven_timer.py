import pygame

class OvenTimer:
  def __init__(self, time_in_millis):
    self.start_time = pygame.time.get_ticks()
    self.end_time = time_in_millis

  def isended(self):
    """
    return whether or not the timer end time has passed
    """
    return self.end_time < pygame.time.get_ticks() - self.start_time