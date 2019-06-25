from island import Island, rgb_to_greyscale

def test_create_island_of_size():
  island = Island(5, 5)
  assert 5 == island.width
  assert 5 == island.height

def test_can_get_color_at_point():
  island = Island(5, 5)
  color = island.get_color_at(2, 2)
  assert 4 == len(color)

def test_can_get_greyscale_at_point():
  island = Island(5, 5)
  color = island.get_color_at(2, 2)
  grey = island.get_greyscale_at(2, 2)
  assert rgb_to_greyscale(color) == grey
