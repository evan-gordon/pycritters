import os, sys, pygame, random
from island import Island
from character import Character

# load image and return or close on fail to load
def load_image(name, colorkey=None):
    fullname = os.path.join('images', name)
    try:
        image = pygame.image.load(fullname).convert()
    except:
        print('Cannot load image:', name)
        sys.exit(-1)
    image = image.convert()
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0,0))
        image.set_colorkey(colorkey, RLEACCEL)
    return image, image.get_rect()

def make_text(str, font):
  textSurface = font.render(str, True, (0, 0, 0))
  return textSurface, textSurface.get_rect()

def draw_ui():
  pass

class Scene:
  def __init__(self, width, height):
    pygame.init()
    pygame.display.set_caption('PiCritters')
    self.colors = {'black': (0, 0, 0), 'green': (0, 245, 0)}
    self.font = pygame.font.SysFont("comicsansms", 24)
    self.width = width
    self.height = height
    self.screen = pygame.display.set_mode((width, height))
    self.day = 1
    self.bg = Island(width, height)
    self.clock = pygame.time.Clock()
    self.textures = {'f1': load_image('F_01.png'), 'm1': load_image('M_01.png')}
    self.sprites = pygame.sprite.Group()
    #self.sprites.add(Character(self.textures['f1'], 200, 100))
    pygame.time.set_timer(pygame.USEREVENT+1, 5000)
  
  def random_position(self):
    valid_pos = False
    x = 0
    y = 0
    while(not valid_pos):
      x, y = random.randint(0, self.width - 1), random.randint(0, self.height - 1)
      if(self.bg.topology[x][y] > 0.31):
        valid_pos = True
    return x, y

  def handle_events(self):
    for event in pygame.event.get():
      if(event.type == pygame.QUIT): sys.exit()
      if(event.type == pygame.USEREVENT+1):
        self.day += 1
        x, y = self.random_position()
        self.bg.img.set_at((x, y), (255, 0, 0))
        print(f'Spawning at ({x}, {y}) height: {self.bg.topology[x][y]}')
        if(self.day % 2 == 0):
          self.sprites.add(Character(self.textures['m1'], self.day, x, y))
        if(self.day % 2 != 0):
          self.sprites.add(Character(self.textures['f1'], self.day, x, y))

  def loop(self):
    while 1:
      self.clock.tick(60)
      self.handle_events()

      self.screen.blit(self.bg.img, self.bg.pos)  # draw background
      self.sprites.update(self.day, self.bg.topology)# update stuff
      self.sprites.draw(self.screen)              # draw stuff
      self.render_ui()
      pygame.display.flip()
  
  def render_ui(self):
    frames = "{}fps".format(round(self.clock.get_fps()))
    fps = self.font.render(frames, True, (0, 0, 0))
    self.screen.blit(fps, (0, 0))
    currDay = self.font.render("Day: {}".format(self.day), True, (0, 0, 0))
    self.screen.blit(currDay, (50, 0))