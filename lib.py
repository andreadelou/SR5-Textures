import struct
from Obj import Obj
from Vector import V3

def char(c):
    c = struct.pack('=c', c.encode('ascii'))
    return c
def word(w):
    w = struct.pack('=h', w)   
    return w  
def dword(dw):
    dw = struct.pack('=l', dw)   
    return dw  

# def color_select(r, g, b):
#     return bytes([int(b * 255), int(g * 255), int(r * 255)])
def colorrgb(r, g, b):
    return bytes([b, g, r])

def color_select(r, g, b):
  return colorrgb(clamping(r*255), clamping(g*255), clamping(b*255))
  
def clamping(num):
  return int(max(min(num, 255), 0))

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
    def __init__(self):
        self.width = 0
        self.height = 0
        self.pixels = 0
        self.colort = color_select(255, 255, 255)
        self.background = color_select(0, 0, 0)
        self.viewport_x = 0 
        self.viewport_y = 0
        self.viewport_height = 0
        self.viewport_width = 0
        self.texture = None
        self.active_shader = None

    
    def glCreateWindow(self, width, height):
        self.width = width
        self.height = height
        
        self.framebuffer = [[self.background for x in range(self.width)]
                       for y in range(self.height)]
        
        self.zBuffer = [
            [-9999 for x in range(self.width)]
            for y in range(self.height)
        ]

        
    def glPoint(self, x, y, color = None):
        if (0 <= x < self.width) and (0 <= y < self.height):
            self.framebuffer[x][y] = color or self.colort

    
    def transform_vertex(self, vertex, translate, scale):
        return V3(
            round((vertex[0] * scale[0]) + translate[0]),
            round((vertex[1] * scale[1]) + translate[1]),
            round((vertex[2] * scale[2]) + translate[2])
        )
    
    def load(self, filename, translate, scale, texture = None):
        model = Obj(filename)

        for face in model.faces:
            vcount = len(face)
            
            if vcount == 4:
                f1 = face[0][0] - 1
                f2 = face[1][0] - 1
                f3 = face[2][0] - 1
                f4 = face[3][0] - 1

                v1 = self.transform_vertex(model.vertex[f1], translate, scale)
                v2 = self.transform_vertex(model.vertex[f2], translate, scale)
                v3 = self.transform_vertex(model.vertex[f3], translate, scale)
                v4 = self.transform_vertex(model.vertex[f4], translate, scale)

                if not texture:
                    self.triangle_babycenter(v1, v2, v3)
                    self.triangle_babycenter(v1, v3, v4)
                else:
                    t1 = face[0][1] - 1
                    t2 = face[1][1] - 1
                    t3 = face[2][1] - 1
                    t4 = face[3][1] - 1

                    tA = V3(*model.tvertex[t1])
                    tB = V3(*model.tvertex[t2])
                    tC = V3(*model.tvertex[t3])
                    tD = V3(*model.tvertex[t4])

                    self.triangle_babycenter((v1, v2, v3), (tA, tB, tC), texture)
                    self.triangle_babycenter((v1, v3, v4), (tA, tC, tD), texture)

            
            elif vcount == 3:
                f1 = face[0][0] - 1
                f2 = face[1][0] - 1
                f3 = face[2][0] - 1

                v1 = self.transform_vertex(model.vertex[f1], translate, scale)
                v2 = self.transform_vertex(model.vertex[f2], translate, scale)
                v3 = self.transform_vertex(model.vertex[f3], translate, scale)

                if not texture:
                    self.triangle_babycenter(v1, v2, v3)
                else:
                    t1 = face[0][1] - 1
                    t2 = face[1][1] - 1
                    t3 = face[2][1] - 1

                    tA = V3(*model.tvertex[t1])
                    tB = V3(*model.tvertex[t2])
                    tC = V3(*model.tvertex[t3])

                    self.triangle_babycenter((v1, v2, v3), (tA, tB, tC), texture)
    
    
    def lightPosition(self, x:int, y:int, z:int):
        self.light = V3(x, y, z)
    
    def triangle_babycenter(self, vertex, tvertex=(), texture = None, color = None, intensity = 1):
        
        A, B, C = vertex
        if self.texture:
            tA, tB, tC = tvertex
        
        Light = self.light
        Normal = (B - A) * (C - A)
        i = Normal.norm() @ Light.norm()
        
        if i < 0:
            i = abs(i)
        if i > 1:
            i = 1


        color_tex = 1 * i

        self.render_color = color_select(color_tex, color_tex, color_tex)

        min,max = bounding_box(A, B, C)
        min.round_coords()
        max.round_coords()
        
        for x in range(min.x, max.x + 1):
            for y in range(min.y, max.y + 1):
                w, v, u = barycentric(A, B, C, V3(x, y))

                if(w < 0 or v < 0 or u < 0):
                    continue
                
                if texture:
                    tA, tB, tC = tvertex
                    tx = tA.x * w + tB.x * u + tC.x * v
                    ty = tA.y * w + tB.y * u + tC.y * v

                    color = texture.get_color_with_intensity(tx, ty, intensity)

                z = A.z * w + B.z * v + C.z * u

                if 0<=x<self.width and 0<=y<self.height:
                    if(x < len(self.zBuffer) and y < len(self.zBuffer) and z > self.zBuffer[x][y]):
                        self.zBuffer[x][y] = z
                        self.glPoint(x, y, color)
                    else:
                        self.glPoint(x,y, color)

    
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
            