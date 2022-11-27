import struct
import random
import numpy
from obj import Obj, Texture
from collections import namedtuple
from lib import *

BLACK = color(0, 0, 0)
WHITE = color(255, 255, 255)

class Render(object):
  def __init__(self, width, height):
    self.width = width
    self.height = height
    self.current_color = WHITE
    self.clear()

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
    try:
      self.framebuffer[y][x] = color or self.current_color
    except:
      pass
  
  
  def shader(self, A,B,C,x,y):
    centro_x, centro_y = 330,260 #centro del planeta
    radio = 2 + random.randint(0,20) 
  
    #el lunar de Jupiter
    if(x-centro_x)**2 +(y-centro_y)**2 < radio**2:
      return color(244, 98, 3)
    
    
    #Esto se basa en el tama;o que quiero que tengan las lineas de color
    #El y determina que tanto espacio del planeta ocuparan con las debidas coordenadas de alto
    #Mientras que el random es el tama;o de dispersion de las "particulas" para hacerlo ver "gaseoso"
    
    
    #arriba
    if(y>=375 + random.randint(0,50)):
      return color(171, 155, 57)
    #linea 2
    if(y>=360 + random.randint(0,20) and y<375 + random.randint(0,20)):
      return color(252, 246, 243)
    #Linea 2
    if(y>=355 + random.randint(0,30) and y<360 + random.randint(0,20)):
      return color(235, 175, 122)
    #Linea 3
    if(y>=340 + random.randint(0,20) and y<355 + random.randint(0,20)):
      return color(249, 217, 189)
    #Linea 3
    if(y>=320 + random.randint(0,20) and y<340 + random.randint(0,20)):
      return color(235, 175, 122)
    #Linea 4
    if(y>=295 + random.randint(0,50) and y<320 + random.randint(0,50)):
      return color(121, 21, 21)
    #Linea 4
    if(y>=285 + random.randint(0,10) and y<320 + random.randint(0,20)):
      return color(192, 138, 113)
    #Linea "amarilla"
    if(y>=280 + random.randint(0,10) and y<285 + random.randint(0,20)):
      return color(244, 198, 98) 
    #Linea arriba del lunar (no lo toca)
    if(y>=250 + random.randint(0,20) and y<280 + random.randint(0,20)):
      return color(223, 211, 205)
    
    #Lineas del lunar 
    #Linea que va en la parte superior del lunar 
    if(y>=250 + random.randint(0,50) and y<260 + random.randint(0,50) and x < centro_x ):
      return color(192, 138, 113)
    if(y>=250 + random.randint(0,10) and y<260 + random.randint(0,8) and x > centro_x ):
      return color(192, 138, 113)
    #Linea que va en la parte superior del lunar 
    if(y>=250 + random.randint(0,10) and y<260 + random.randint(0,8) and x > centro_x ):
      return color(207, 94, 41)
    #Linea que va en la parte superior del lunar 
    if(y>=240 + random.randint(0,10) and y<250 + random.randint(0,8)and x > centro_x):
      return color(121, 21, 21)
    if(y>=240 + random.randint(0,50) and y<250 + random.randint(0,50)and x < centro_x):
      return color(121, 21, 21)
    #Linea que va en la parte inferior del lunar 
    if(y>=230 + random.randint(0,10) and y<250 + random.randint(0,20)):
      return color(253, 244, 239)
    
    #Fuera lunar 
    
    #Tercera linea abajo para arriba
    if(y>=200 + random.randint(0,20) and y<220 + random.randint(0,20)):
      return color(245, 237, 222)
    #Segunda linea de abajo para arriba
    if(y>=180 + random.randint(0,20) and y<230 + random.randint(0,20)):
       return color(229, 212, 184)
    #Color de abajo
    if(y>0 + random.randint(0,20) and y<200 + random.randint(0,20)):
      return color(171, 155, 57)
      
    #color base 
    if(y>=0 + random.randint(0,5) and y<=375 + random.randint(0,5)):
      return color(234, 190, 122)

  def triangle(self, A, B, C, color=None):
    bbox_min, bbox_max = bbox(A, B, C)

    for x in range(bbox_min.x, bbox_max.x + 1):
      for y in range(bbox_min.y, bbox_max.y + 1):
        w, v, u = barycentric(A, B, C, V2(x, y))
        if w < 0 or v < 0 or u < 0: 
          continue
        
        color = self.shader(A,B,C,x,y)

        z = A.z * w + B.z * v + C.z * u

        if x < 0 or y < 0:
          continue

        if x < len(self.zbuffer) and y < len(self.zbuffer[x]) and z > self.zbuffer[x][y]:
          self.point(x, y, color)
          self.zbuffer[x][y] = z

  def transform(self, vertex, translate=(0, 0, 0), scale=(1, 1, 1)):
    return V3(
      round((vertex[0] + translate[0]) * scale[0]),
      round((vertex[1] + translate[1]) * scale[1]),
      round((vertex[2] + translate[2]) * scale[2])
    )
    
  def load(self, filename, translate=(0, 0, 0), scale=(1, 1, 1)):
    model = Obj(filename)
    light = V3(0,0,1)

    for face in model.vfaces:
        vcount = len(face)

        if vcount == 3:
          f1 = face[0][0] - 1
          f2 = face[1][0] - 1
          f3 = face[2][0] - 1

          a = self.transform(model.vertices[f1], translate, scale)
          b = self.transform(model.vertices[f2], translate, scale)
          c = self.transform(model.vertices[f3], translate, scale)

          normal = norm(cross(sub(b, a), sub(c, a)))
          intensity = dot(normal, light)

          grey = round(255 * intensity)
          if grey < 0:
            continue
          self.triangle(a, b, c, color=color(grey, grey, grey))
          
        else:
          f1 = face[0][0] - 1
          f2 = face[1][0] - 1
          f3 = face[2][0] - 1
          f4 = face[3][0] - 1   

          vertices = [
            self.transform(model.vertices[f1], translate, scale),
            self.transform(model.vertices[f2], translate, scale),
            self.transform(model.vertices[f3], translate, scale),
            self.transform(model.vertices[f4], translate, scale)
          ]

          normal = norm(cross(sub(vertices[0], vertices[1]), sub(vertices[1], vertices[2])))  
          intensity = dot(normal, light)
          grey = round(255 * intensity)

          A, B, C, D = vertices 

          grey = round(255 * intensity)
          if grey < 0:
            continue
          self.triangle(A, B, C, color(grey, grey, grey))
          self.triangle(A, C, D, color(grey, grey, grey))            
            

r = Render(500, 500)
r.load('./sphere.obj', translate=(1, 1, 1), scale=(300, 300, 300))

r.display('Jupiter.bmp')