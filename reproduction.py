import neat

def reproduce(config, gid, parent, parent2):
  print(str(parent))
  print(str(parent2))
  child = config.genome_type(gid)
  child.configure_crossover(parent, parent2, config.genome_config)
  child.mutate(config.genome_config)
  network = neat.nn.FeedForwardNetwork.create(child, config)
  return (child, network)