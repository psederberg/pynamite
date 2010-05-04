#
# My wish for Pynamite
#

from __future__ import with_statement

from pynamite import *
from pynamite.actor import TextBox

def scene1():
    x = TextBox("Pynamite")
    y = TextBox("Rocks!!!")
    enter(x)
    pause()
    # with parallel():
    #     fadeout(1.0,x)
    #     fadein(1.0,y)
    def together():
        fadeout(1.0,x)
        fadein(1.0,y)
    in_parallel(together)
    pause()
    fadeout(1.0,y)
    pause()
add_scene(scene1)

def scene2():
    x = TextBox("Yes, it Rocks!!!")
    set_var(x, "opacity", 0.0)
    enter(x)
    linear(x, "opacity", end_val=.5,duration=.5)
    linear(x, "opacity", end_val=.25,duration=.5)
    linear(x, "opacity", end_val=.75,duration=.5)
    linear(x, "opacity", end_val=.5,duration=.5)
    linear(x, "opacity", end_val=1.0,duration=.5)
    pause()
    leave()
add_scene(scene2)

# run it
run()
