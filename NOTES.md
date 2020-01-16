# Notes

Currently im observing two things while training the critters.

* Stagnation is happening too quickly
* Critters are getting extrodinarily high fitness scores for bad behaviours

The latter could easily be causing the former.

Somehow it needs to be more apparent to the critters when theyre about to die from drowning.
It needs to be a bit easier for critters to survive long enough to reproduce.
Possibly try a 3 step training program.

* Train in world with just apples
* Train in world with apples and other critters
* Train in world with water
* Then real world simulation (no artificial populations)

## Post swap to using RGB at point inputs

Survival rate increased over time with training much better.
They also seemed to be able to figure out how to reproduce very well.
I saw two males sitting on top of a female very early on.

Current issues:

* Vibrating is too commmon, need to dissalow that
* single point in a direction sampling might be hurting their ability to understand what is bad and what is good
* my fitness function is horrendous and clearly not working
* The island does seem a bit too small for the critters

I could make a map generation function that generates a circle, that would be possibly easier to train on, and could allow for more reliable stable maps with a small map size.

Distance traveled could also be something that might be beneficial to fitness.

## Post swap to vector outputs and raycasting

Fps on my machine right now is too low and i need to look into a different machine to run on.

I tried using unconnected brains which seems to evolve a more organic process for brain structure development, but theyre still stagnating too early. Early versions of this weeded out moving because it would cause them to drown so i had to remove that as an obstical. 

There are some methods i can look into for optimizing the ray tracing:

* building a Bounding Volume Hierarchy (BVH) for optimizing groups of objects im scanning for hit detection.
* use circles joined on end along the ray for collecting groups of objects that may be collided with.

I have not yet added distance to the inputs for these critters, but they will need that to know which direction they should prioritize movement.

For the past two phases i still see similar behaviors (using unconnected at start networks). First they learn its useful to move. They then learn moving in a circle brings better chances of running into food. Sometimes the will then learn to move in a larger circle, but they always get stuck at this point in the process. After adding distances i could start them with more nodes in their brain and more connections to increase the probability of them learning to move towards food.

## After Dynamic food placement

Apparently the cause for most of the previous issues was due to the static placement of 
food. With dynamic placement critters became quickly able to determine moving towards food to be a desirable trait. 

Also with these changes i reduced the distance critters could see (mostly for performance reasons) but this seemed to also reduce unnessisary inputs to the critters.

Perhaps in the future when i try out Genes i could try having distance they can see be a gene that is evolved.

## Todo

* metabolism - hunger is increased by ammount of distance traveled instead of only by time.
* after perfecting the current stage, build out stage 2 (islands) and 3 (reproduction).
