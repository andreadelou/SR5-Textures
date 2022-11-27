import struct
from obj import Obj
from Vector import *
from textures import *

def char(c):
    # 1 byte
  return struct.pack('=c', c.encode('ascii'))


def word(w):
    # 2 bytes
    return struct.pack('=h', w)

def dword(d):
    # 4 bytes
    return struct.pack('=l',d)


def color(r, g, b):
    r = int(min(255, max(r, 0)))
    g = int(min(255, max(g, 0)))
    b = int(min(255, max(b, 0)))
    return bytes([b, g, r])

def cross(v1, v2):
      return (
        v1.y * v2.z - v1.z * v2.y,
        v1.z * v2.x - v1.x * v2.z,
        v1.x * v2.y - v1.y * v2.x
      )
    
def bounding_box(A, B, C):
    coords = [(A.x, A.y),(B.x, B.y),(C.x, C.y)]

    xmin = 999999
    xmax = -999999
    ymin = 999999
    ymax = -999999

    for (x, y) in coords:
        if x < xmin:
            xmin = x
        if x > xmax:
            xmax = x
        if y < ymin:
            ymin = y
        if y > ymax:
            ymax = y
    return V3(xmin, ymin), V3(xmax, ymax)

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

      return (w, v, u)
    
class Render(object):
    # Constructor
    def __init__(self):
        self.pixels = 0
        self.viewPortX = 0
        self.viewPortY = 0
        self.height = 0
        self.width = 0
        self.clearColor = color(0, 0, 0)
        self.texture = None

        self.current_color = color(255,255,255)
        self.framebuffer = []
       
        self.glViewport(0,0,self.width, self.height)
        self.glClear() 

    def glCreateWindow(self, width, height):
        self.width = width
        self.height = height
        self.glClear()
        
        self.zBuffer = [
          [-9999 for x in range(self.width)]
          for y in range(self.height)
        ]

    def glViewport(self, x, y, width, height):
        self.viewpx = x
        self.viewpy = y
        self.viewpwidth = width
        self.viewpheight = height
    
    def glClear(self):
        self.framebuffer = [[self.clearColor for x in range(self.width+1)]
                            for y in range(self.height+1)]

    def glClearColor(self, r, g, b):
        self.clearColor = color(r, b, g)
        self.glClear()

    def glColor(self, r, g, b):
        self.current_color = color(r, g, b)

    def glPoint(self, x, y, colort = None):
        if (0 <= x < self.width) and (0 <= y < self.height):
          self.framebuffer[x][y] = colort or self.current_color

    # def glLine(self, v1, v2):
        
    #     x0 = int((v1.x + 1) * self.viewpwidth * 1/2 ) + self.viewpx
    #     y0 = int((v1.y + 1) * self.viewpheight * 1/2) + self.viewpy

    #     x1 = int((v2.x + 1) * self.viewpwidth * 1/2 ) + self.viewpx
    #     y1 = int((v2.y + 1) * self.viewpheight * 1/2) + self.viewpy

    #     #realizar conversion
    #     dy = abs(y1 - y0)
    #     dx = abs(x1 - x0)

    #     steep = dy > dx

    #     if steep:
    #         x0, y0 = y0, x0
    #         x1, y1 = y1, x1

    #     if  x0 > x1:
    #         x0, x1 = x1, x0
    #         y0, y1 = y1, y0

    #     dy = abs(y1 - y0)
    #     dx = abs(x1 - x0)

    #     offset = 0
        
    #     threshold = dx
        
    #     y = y0

    #     for x in range(x0, x1 + 1):
    #         if steep:
    #             self.glPoint(y, x)
    #         else:
    #             self.glPoint(x, y)

    #         offset += dy * 2
    #         if offset >= threshold:
    #             y += 1 if y0 < y1 else -1
    #             threshold += dx * 2
            
    def glObjModel(self, filename, scale_factor, translate_factor, texture=None):
      model = Obj(filename)
      
      for face in model.faces:
  
        if len(face) == 4:
          f1 = face[0][0] - 1
          f2 = face[1][0] - 1
          f3 = face[2][0] - 1
          f4 = face[3][0] - 1

          v1 = self.transform_vertex(model.vertex[f1], scale_factor, translate_factor)
          v2 = self.transform_vertex(model.vertex[f2], scale_factor, translate_factor)
          v3 = self.transform_vertex(model.vertex[f3], scale_factor, translate_factor)
          v4 = self.transform_vertex(model.vertex[f4], scale_factor, translate_factor)
          
          if not texture:
            self.triangle_babycenter(v1,v2,v3, colort=color(0,0,0))
            self.triangle_babycenter(v1,v2,v3, colort=color(0,0,0))
          
          else:

            ft1 = face[0][1] - 1
            ft2 = face[1][1] - 1
            ft3 = face[2][1] - 1
            ft4 = face[3][1] - 1

            vt1 = V3(*model.tvertex[ft1],0)
            vt2 = V3(*model.tvertex[ft2],0)
            vt3 = V3(*model.tvertex[ft3],0)
            vt4 = V3(*model.tvertex[ft4],0)

            self.triangle_babycenter((v1, v2, v3), (vt1, vt2, vt3), texture=texture)
            self.triangle_babycenter((v1, v3, v4), (vt1, vt3, vt4), texture=texture)
          
        
        if len(face) == 3:
          f1 = face[0][0] - 1
          f2 = face[1][0] - 1
          f3 = face[2][0] - 1

          v1 = self.transform_vertex(model.vertex[f1], scale_factor, translate_factor)
          v2 = self.transform_vertex(model.vertex[f2], scale_factor, translate_factor)
          v3 = self.transform_vertex(model.vertex[f3], scale_factor, translate_factor)

          if not texture:
            self.triangle_babycenter(v1,v2,v3, colort=color(0,0,0))
            
          else:

            ft1 = face[0][1] - 1
            ft2 = face[1][1] - 1
            ft3 = face[2][1] - 1
            
            vt1 = V3(*model.tvertex[ft1])
            vt2 = V3(*model.tvertex[ft2])
            vt3 = V3(*model.tvertex[ft3])

            self.triangle_babycenter((v1, v2, v3), (vt1, vt2, vt3), texture=texture)
            
    
    def transform_vertex(self, vertex, scale_factor, translate_factor):
      return V3(
        (vertex[0] * scale_factor[0]) + translate_factor[0], 
        (vertex[1] * scale_factor[1]) + translate_factor[1],
        (vertex[2] * scale_factor[2]) + translate_factor[2]
      )  
        
    # SR4               
    
    def triangle_babycenter(self, vertices, tvertices=(), texture=None, intensity=1, colort=None):
        
        A, B, C = vertices
        min,max = bounding_box(A, B, C)
        min.round_coords()
        max.round_coords()
        
        # if self.texture:
        #     tA, tB, tC = tvertices
        
        Light = self.light
        Normal = (B - A) * (C - A)
        i = Normal.norm() @ Light.norm()
        
        if i < 0:
          i=abs(i)
        if i > 1:
          i = 1
          
        color_textura = 1*i
        
        self.current_color = color(color_textura,color_textura,color_textura)
        
        for x in range(min.x, max.x + 1):
            for y in range(min.y, max.y + 1):
                w, v, u = barycentric(A, B, C, V3(x, y))

                if (w < 0 or v < 0 or u < 0):
                    continue
                if texture: 
                  tA, tB, tC = tvertices
                  tx = tA.x * w + tB.x * u + tC.x * v
                  ty = tA.y * w + tB.y * u + tC.y * v
                  
                  colort = self.texture.get_color_with_intensity(tx, ty, i)
                  
                  z = A.z * w + B.z * v + C.z * u
                  
                  if (x<0) or (y<0):
                    continue
                  if x < len(self.zbuffer) and y < len(self.zbuffer[x]) and z > self.zbuffer[x][y]:
                    self.zbuffer[x][y] = z 
                    self.glPoint(x, y, colort)
                    
    def lightPosition(self, x:int, y:int, z:int):
      self.light = V3(x, y, z)
                  
    def glFinish(self, filename):
        with open(filename, 'bw') as file:
            # Header
            file.write(bytes('B'.encode('ascii')))
            file.write(bytes('M'.encode('ascii')))

            # file size
            file.write(dword(14 + 40 + self.height * self.width * 3))
            file.write(dword(0))
            file.write(dword(14 + 40))

            # Info Header
            file.write(dword(40))
            file.write(dword(self.width))
            file.write(dword(self.height))
            file.write(word(1))
            file.write(word(24))
            file.write(dword(0))
            file.write(dword(self.width * self.height * 3))
            file.write(dword(0))
            file.write(dword(0))
            file.write(dword(0))
            file.write(dword(0))

            # Color table
            for y in range(self.height):
                for x in range(self.width):
                    file.write(self.framebuffer[y][x])
            file.close()
      

  
r = Render()
r.glCreateWindow(1000, 1000)
# r.glViewport(int(0),int(0),int(800/1), int(800/1))
r.lightPosition(0.3, 0.2, 1)
textura = Texture('./model.bmp')

#                          escala            posicion y , x
r.glObjModel('face.obj', (10, 10, 10), (400, 200, 0), texture=textura)
# r.glObjModel('arbol.obj', (20, 20, 20), (400, 100, 0))
r.glFinish("obj.bmp")
