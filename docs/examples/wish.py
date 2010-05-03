#
# My wish for Pynamite
#

from pynamite.play import Play

# set up your scenes
scenes = []

def scene1():
    pass
scenes.append(scene1)


def scene2():
    # set up the actors
    a = TextBox("one")
    b = TextBox("two")
    # tell them what to do
    with parallel():
        # start at same time
        fade_in([a],1.0)
        fade_in([b],2.0)
    pause()
    
               
scenes.append(scene2)


# Put on the play
myplay = Play(800,600,scenes=scenes)
myplay.show()
