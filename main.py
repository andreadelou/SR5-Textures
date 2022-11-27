import struct
import random
import numpy
from obj import Obj, Texture
from collections import namedtuple
from lib import *

BLACK = color(0, 0, 0)
WHITE = color(255, 255, 255)

def bounding_box(A, B, C):

  coords = [(A.x, A.y), (B.x, B.y), (C.x, C.y)]

  x_min = 999999
  x_max = -999999
  y_min = 999999
  y_max = -999999

  for(x, y) in coords:

      if x < x_min:
          x_min = x
      if x > x_max:
          x_max = x
      if y < y_min:
          y_min = y
      if y > y_max:
          y_max = y

  return V3(x_min, y_min), V3(x_max, y_max)

def barycentric(A, B, C, P):

  cx, cy, cz = cross(
      V3(B.x - A.x, C.x - A.x, A.x - P.x),
      V3(B.y - A.y, C.y - A.y, A.y - P.y)
  )

  if cz == 0:
      return(-1, -1, -1)

  u = cx / cz
  v = cy / cz
  w = 1 - (u + v)

  return(w, v, u)


class Render(object):
  def __init__(self, width, height):
    self.width = width
    self.height = height
    self.current_color = WHITE
    self.clear()
    self.texture = None

  def clear(self):
    self.framebuffer = [
      [BLACK for x in range(self.width)] 
      for y in range(self.height)
    ]
    self.zbuffer = [
          [-9999 for x in range(self.width)]
          for y in range(self.height)
        ]

  def write(self, filename):
    f = open(filename, 'bw')

    f.write(char('B'))
    f.write(char('M'))
    f.write(dword(14 + 40 + self.width * self.height * 3))
    f.write(dword(0))
    f.write(dword(14 + 40))

    # Image header (40 bytes)
    f.write(dword(40))
    f.write(dword(self.width))
    f.write(dword(self.height))
    f.write(word(1))
    f.write(word(24))
    f.write(dword(0))
    f.write(dword(self.width * self.height * 3))
    f.write(dword(0))
    f.write(dword(0))
    f.write(dword(0))
    f.write(dword(0))

   
    for x in range(self.height):
      for y in range(self.width):
        f.write(self.framebuffer[x][y])

    f.close()

  def display(self, filename='out.bmp'):
      #Esto es para que el bpm pueda ser previamente visto como una imagen y no se tenga que descarfar el bmp
      #para poderlo visualizar 
    self.write(filename)

    try:
      from wand.image import Image
      from wand.display import display

      with Image(filename=filename) as image:
        display(image)
    except ImportError:
      pass 

  def set_color(self, color):
    self.current_color = color

  def point(self, x, y, color = None):
     if (0 <= x < self.width) and (0 <= y < self.height):
        self.framebuffer[x][y] = color or self.current_color
  
  
  def triangle(self, A, B, C, cord_tex = None, texture = None, color = None, intensity = 1):

    light = V3(0, 0, 1)
    normal = (B - A) * (C - A)

    i = normal.norm() @ light.norm()

    if i < 0:
        i = abs(i)
    if i > 1:
        i = 1

    color_tex = 1 * i

    self.render_color = color(color_tex, color_tex, color_tex)

    min, max = bounding_box(A, B, C)
    min.round_coords()
    max.round_coords()

    for x in range(min.x, max.x + 1):
        for y in range(min.y, max.y + 1):
            w, v, u = barycentric(A, B, C, V3(x, y))

            if(w < 0 or v < 0 or u < 0):
                continue
            
            if texture:
                tA, tB, tC = cord_tex
                tx = tA.x * w + tB.x * u + tC.x * v
                ty = tA.y * w + tB.y * u + tC.y * v

                color = texture.get_color_with_intensity(tx, ty, intensity)

            z = A.z * w + B.z * v + C.z * u

            if(x < len(self.zBuffer) and y < len(self.zBuffer) and z > self.zBuffer[x][y]):
                self.zBuffer[x][y] = z
                self.glPoint(x, y, color)


  def transform_vertex(self, vertex, translate=(0, 0, 0), scale=(1, 1, 1)):
    return V3(
      round((vertex[0] + translate[0]) * scale[0]),
      round((vertex[1] + translate[1]) * scale[1]),
      round((vertex[2] + translate[2]) * scale[2])
    )
    
  def load(self, filename, translate, scale, texture = None):
    model = Obj(filename)

    for face in model.vfaces:
        vcount = len(face)
        
        if vcount == 4:
            f1 = face[0][0] - 1
            f2 = face[1][0] - 1
            f3 = face[2][0] - 1
            f4 = face[3][0] - 1

            v1 = self.transform_vertex(model.vertices[f1], translate, scale)
            v2 = self.transform_vertex(model.vertices[f2], translate, scale)
            v3 = self.transform_vertex(model.vertices[f3], translate, scale)
            v4 = self.transform_vertex(model.vertices[f4], translate, scale)

            if not texture:
                self.triangle(v1, v2, v3)
                self.triangle(v1, v3, v4)
            else:
                t1 = face[0][1] - 1
                t2 = face[1][1] - 1
                t3 = face[2][1] - 1
                t4 = face[3][1] - 1

                tA = V3(*model.tvertices[t1])
                tB = V3(*model.tvertices[t2])
                tC = V3(*model.tvertices[t3])
                tD = V3(*model.tvertices[t4])

                self.triangle(v1, v2, v3, (tA, tB, tC), texture)
                self.triangle(v1, v3, v4, (tA, tC, tD), texture)

        
        elif vcount == 3:
            f1 = face[0][0] - 1
            f2 = face[1][0] - 1
            f3 = face[2][0] - 1

            v1 = self.transform_vertex(model.vertices[f1], translate, scale)
            v2 = self.transform_vertex(model.vertices[f2], translate, scale)
            v3 = self.transform_vertex(model.vertices[f3], translate, scale)

            if not texture:
                self.triangle(v1, v2, v3)
            else:
                t1 = face[0][1] - 1
                t2 = face[1][1] - 1
                t3 = face[2][1] - 1

                tA = V3(*model.tvertices[t1])
                tB = V3(*model.tvertices[t2])
                tC = V3(*model.tvertices[t3])

                self.triangle(v1, v2, v3, (tA, tB, tC), texture)
            

r = Render(500, 500)


textura = Texture('./earth.bmp')

r.load('./earth.obj', translate=[512, 512, 0], scale=[1, 1, 1], texture=textura)

r.display('SR5.bmp')
