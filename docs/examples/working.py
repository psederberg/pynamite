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
    y.set_cx(0.0)
    y.set_cy(0.0)
    with parallel():
        fadein(2.0,y)
        y.set_cx(.5,duration=2.0,func="smooth")
        y.set_cy(.5,duration=2.0,func="smooth")
        fadeout(1.0,x)

    # wait for intput
    pause()

    # last actor leaves
    with parallel():
        fadeout(2.0,y)
        y.set_cx(1.0,duration=2.0,func="smooth")
        y.set_cy(1.0,duration=2.0,func="smooth")
           
    pause()
# add that scene to the play
add_scene(scene1)

def scene2():
    # define the actor
    x = TextBox("Yes, it Rocks!!!")
    
    # set its opacity to 0.0
    x.set_opacity(0.0)
    
    # have it enter (but remember it's still not visible)
    x.enter()
    
    # have it become visible, but in a fancy way
    x.set_opacity(.5, duration=.5, func="smooth")
    x.set_opacity(.25, duration=.25, func="smooth")
    x.set_opacity(.75, duration=.5, func="smooth")
    x.set_opacity(.5, duration=.25, func="smooth")
    x.set_opacity(1.0, duration=.5, func="smooth")

    # wait for input
    pause()

    # have the actor leave
    x.fadeout(1.0)
    
# add this scene
add_scene(scene2)

# run it
run()

