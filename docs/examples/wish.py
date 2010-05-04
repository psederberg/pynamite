#
# My wish for Pynamite
#

from actor import TextBox

def scene1():
    x = TextBox("Pynamite")
    y = TextBox("Rocks!!!")
    enter(x)
    pause()
    with parallel():
        fadeout(1.0,x)
        fadein(1.0,y)
    pause()
    fadeout(1.0,y)
    pause()

def scene2(p):
    x = TextBox("Yes, it Rocks!!!")
    fadein(1.0,x)
    pause()
    leave()

run()
