import os, sys, pygame, random
from island import Island
from character import Character
from bush import Bush

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

class Scene:
  def __init__(self, width, height):
    pygame.init()
    pygame.display.set_caption('PiCritters')
    self.colors = {'black': (0, 0, 0), 'green': (0, 245, 0)}
    self.font = pygame.font.SysFont("comicsansms", 24)
    self.width, self.height = width, height
    self.screen = pygame.display.set_mode((width, height))
    self.day, self.initial_pop, self.bush_pop = 1, 25, 15
    self.bg = Island(width, height)
    self.clock = pygame.time.Clock()
    self.food_texture = load_image('food.png')
    self.char_textures = [(False, load_image('F_01.png')), (True, load_image('M_01.png'))]
    self.sprites = pygame.sprite.Group()
    self.plants = pygame.sprite.Group()
    for i in range(self.initial_pop):
      x, y = self.random_position()
      self.spawn_critter(x, y)
    for i in range(self.bush_pop):
      x, y = self.random_position()
      self.plants.add(Bush(self.food_texture, self.day, x, y))
    pygame.time.set_timer(pygame.USEREVENT+1, 5000)

  def spawn_critter(self, x, y):
    image = self.char_textures[random.randint(0, len(self.char_textures) - 1)]
    self.sprites.add(Character(image, self.day, x, y))

  def random_position(self):
    while(1):
      x, y = random.randint(20, self.width - 21), random.randint(20, self.height - 21)
      if(self.bg.topology[x][y] > 0.31):
        return x, y

  def handle_events(self):
    for event in pygame.event.get():
      if(event.type == pygame.QUIT): sys.exit()
      if(event.type == pygame.USEREVENT+1):
        self.day += 1
      #   x, y = self.random_position()
      #   #print(f'Spawning at ({x}, {y}) height: {self.bg.topology[x][y]}')
      #   if(self.day % 2 == 0):
      #     self.sprites.add(Character(self.textures['m1'], self.day, x, y))
      #   if(self.day % 2 != 0):
      #     self.sprites.add(Character(self.textures['f1'], self.day, x, y))

  def handle_collisions(self):
    for character in self.sprites:
      collided_chars = pygame.sprite.spritecollide(character, self.sprites, False)
      if(collided_chars):
        hadchild = character.collide(collided_chars, self.day)
        if(hadchild):
          self.spawn_critter(character.x, character.y)
      collided_plants = pygame.sprite.spritecollide(character, self.plants, False)
      if(collided_plants):
        character.collideplants(collided_plants, self.day)

  def loop(self):
    while 1:
      self.clock.tick(60)
      self.handle_events()

      self.screen.blit(self.bg.img, self.bg.pos)  # draw background
      self.sprites.update(self.day, self.bg.topology)# update stuff
      self.plants.update(self.day)
      self.handle_collisions()
      self.sprites.draw(self.screen)              # draw stuff
      self.plants.draw(self.screen)
      self.render_ui()
      pygame.display.flip()
  
  def render_ui(self):
    ui_info = f'{round(self.clock.get_fps())}fps Day: {self.day} Population: {len(self.sprites)}'
    ui_font = self.font.render(ui_info, True, (0, 0, 0))
    self.screen.blit(ui_font, (0, 0))