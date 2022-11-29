from lib import Render
from Vector import V3
from obj import *

r = Render()

r.glCreateWindow(800, 800)

r.lightPosition(0, 0, 1)

textura = Texture('./cafe.bmp')
r.load('silla.obj', translate=[400, 400, 100], scale=[100, 100, 0],texture=textura)
r.glFinish('out.bmp')
