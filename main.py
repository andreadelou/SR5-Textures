from lib import Render
from Vector import V3
from obj import *

r = Render()

r.glCreateWindow(1024, 1024)

r.lightPosition(0, 0, 1)
    
textura = Texture('./earth.bmp')
r.load('./earth.obj', translate=[512, 512, 90], scale=[1, 1, 1], texture=textura)

r.glFinish('out.bmp')
