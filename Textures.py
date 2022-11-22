import struct
from main import *

class Texture(object):
    
    def __init__(self, path):
        self.path = path
        self.read()
    
    def read(self):
        with open(self.path, 'rb') as image:
            image.seek(2 + 4 + 2 +  2)
            header_size = struct.unpack('=l', image.read(4))[0]
            image.seek(2 + 4 + 2 + 2 + 4 + 4)
            self.width = struct.unpack('=l', image.read(4))[0]
            self.height = struct.unpack('=l', image.read(4))[0]
            
            image.seek(header_size)
            
            self.pixels = []
            
            for y in range(self.height):
                self.pixels.append([])
                for x in range(self.width):
                    b = ord(image.read(1))
                    g = ord(image.read(1))
                    r = ord(image.read(1))
                    
                    self.pixels[y].append(
                        color(r, g, b)
                    )
                    
    def get_color(self, tx, ty):
        x = round(tx * self.width)
        y = round(ty * self.height)
        
        return self.pixels[y][x]
    
    def get_color_with_intensity(self, tx, ty, intensity):
        x = round(tx * self.width)
        y = round(ty * self.height)
        
        b = self.pixels[y][x][0] * intensity
        g = self.pixels[y][x][1] * intensity
        r = self.pixels[y][x][2] * intensity
        
        return color(r, g, b)
                    

r = Render()
r.glCreateWindow(800, 800)
t = Texture('./obj.bmp')
r.framebuffer = t.pixels

cube = Obj("./silla.obj")

r.current_color = color(25,25,112)

for face in cube.faces:
    if len(face) == 3:
        f1 = face[0][1] - 1
        f2 = face[1][1] - 1
        f3 = face[2][1] - 1
        
        vt1 = V3(
            cube.tvertex[f1][0] * t.width,
            cube.tvertex[f1][1] * t.height,
        )
        vt2 = V3(
            cube.tvertex[f2][0] * t.width,
            cube.tvertex[f2][1] * t.height,
        )
        vt3 = V3(
            cube.tvertex[f3][0] * t.width,
            cube.tvertex[f3][1] * t.height,
        )
        
        r.glLine(vt1,vt2)
        r.glLine(vt2,vt3)
        r.glLine(vt3,vt1)
        
r.glFinish("t.bmp")