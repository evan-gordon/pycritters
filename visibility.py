import math

# possibly change the second two arguments to magnitude and vector
def ray_cast(
    critter, deg_angle, dist, critters, plants, world, *, step_dist=12
): # TODO pass in map as well
  """
  returns tuple of:
  * object collided with
  * position
  * color at point
  """

  rad_angle = math.radians(deg_angle)
  origin = critter.rect.center
  print(f'{origin}: {len(critters)}, {len(plants)}')
  if (dist == 0):
    return (None, origin, (0, 0, 0, 255))

  i = 0
  rise, run = math.sin(rad_angle
                      ) * step_dist, math.cos(rad_angle) * step_dist
  curr_dist, curr_run, curr_rise = 0, 0, 0
  while curr_dist < dist:
    curr_run += run
    curr_rise += rise
    curr_dist += step_dist
    curr_point = (origin[0] + curr_run, origin[1] + curr_rise)

    result = any_collide_with_point(plants, curr_point)
    if (result is not None):
      print("char")
      return (result, curr_point, (255, 0, 0, 255))
    result = any_collide_with_point(critters, curr_point)
    if (result is not None):
      print("plant")
      return (result, curr_point, (255, 255, 255, 255))
    world_info = world.get_info_at(int(curr_point[0]), int(curr_point[1]))
    if (world_info[0] <= 0.05):
      return (None, curr_point, world_info[1])
    i += 1
  return (None, curr_point, (0, 0, 255, 255))

def any_collide_with_point(group, point):
  for obj in group:
    if obj.rect.collidepoint(point):
      return obj
  else:
    return None

def any_collide_with(group, x, y):
  for obj in group:
    if obj.rect.collidepoint(x, y):
      return obj
  else:
    return None
