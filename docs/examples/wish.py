#
# My wish for Pynamite
#

from __future__ import with_statement

from pynamite import *
from pynamite.actor import TextBox

def scene1():
    # define some actors
    x = TextBox("Pynamite")
    y = TextBox("Rocks!!!")

    # tell the first actor to enter
    enter(x)

    # wait for a keypress to continue
    pause()

    # fade out one actor while other comes in
    # # You can use with blocks
    # with parallel():
    #     fadeout(1.0,x)
    #     fadein(1.0,y)
    # Or the functional notation
    set_var(y, "opacity", 0.0)
    enter(y)

    def together():
        fadeout(4.0,x)
        with serial():
            linear(y, "opacity", end_val=.5, duration=1.0)
            linear(y, "opacity", end_val=.0, duration=1.0)
            linear(y, "opacity", end_val=1.0, duration=2.0)
            #fadeout(.5,y)
            #fadein(.5,y)
    in_parallel(together)

    # wait for intput
    pause()

    # last actor leaves
    fadeout(1.0,y)
    pause()
# add that scene to the play
add_scene(scene1)

def scene2():
    # define the actor
    x = TextBox("Yes, it Rocks!!!")
    
    # set its opacity to 0.0
    set_var(x, "opacity", 0.0)

    # have it enter (but remember it's still not visible)
    enter(x)
    
    # have it become visible, but in a fancy way
    smooth(x, "opacity", end_val=.5,duration=.5)
    smooth(x, "opacity", end_val=.25,duration=.25)
    smooth(x, "opacity", end_val=.75,duration=.5)
    smooth(x, "opacity", end_val=.5,duration=.25)
    smooth(x, "opacity", end_val=1.0,duration=.5)

    # wait for input
    pause()

    # have the actor leave
    leave()
# add this scene
add_scene(scene2)

# run it
run()

