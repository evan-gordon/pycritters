# PyCritters

Watch these little duders have kids and die!

## Planned Features

* Use NEAT-python reproduction interface to spawn critters
* Update fitness function
* Option to see in color
* Click on critter and display neural structure
* group UI elements in moveable window
* Ability to kill from paused menu
* during training spawn critters away from food
* allow critters to `see` backwards
* genes, (speed, distance can see)

## Environment

Written in python `3.7`

Make sure you have `pipenv` installed.

To enable, run:

```bash
pipenv shell
```

## Up and Running

training:

```bash
python train.py
```

main simulation:

```bash
python main.py
```

run tests:

```bash
pytest -q

# with code coverage
pytest --cov tests/

# generate coverage report
pytest --cov --cov-report html tests/
```
