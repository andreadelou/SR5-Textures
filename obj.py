import struct 

def color(r, g, b):
  return bytes([b, g, r])


class Obj(object):
    def __init__(self, filename):
        with open(filename) as f:
            self.lines = f.read().splitlines()
            self.vertices = []
            self.tvertices = []
            self.vfaces = []
            self.read()

    def read(self):
        for line in self.lines:
            if line:
                try:
                    prefix, value = line.split(' ', 1)
                except:
                    prefix = ''
                if prefix == 'v':
                    self.vertices.append(list(map(float, value.split(' '))))
                if prefix == 'vt':
                    self.tvertices.append(list(map(float, value.split(' '))))                    
                elif prefix == 'f':
                    try:
                        self.vfaces.append([list(map(int , face.split('/'))) for face in value.split(' ')])
                    except:
                        self.vfaces.append([list(map(int , face.split('//'))) for face in value.split(' ')])


class Texture(object):
    def __init__(self, path):
        self.path = path
        self.read()

    def read(self):
        image = open(self.path, "rb")
        image.seek(2 + 4 + 4) 
        header_size = struct.unpack("=l", image.read(4))[0]  
        image.seek(2 + 4 + 4 + 4 + 4)
        
        self.width = struct.unpack("=l", image.read(4))[0]  
        self.height = struct.unpack("=l", image.read(4))[0] 
        self.pixels = []
        image.seek(header_size)
        for y in range(self.height):
            self.pixels.append([])
            for x in range(self.width):
                b = ord(image.read(1))
                g = ord(image.read(1))
                r = ord(image.read(1))
                self.pixels[y].append(color(r,g,b))
        image.close()

    def get_color(self, tx, ty, intensity=1):
        x = int(tx * self.width)
        y = int(ty * self.height)
        try:
            return bytes(map(lambda b: round(b*intensity) if b*intensity > 0 else 0, self.pixels[y][x]))
        except:
            pass  
    
    def get_color_with_intensity(self, tx, ty, intensity):
        x = round(tx * self.width)
        y = round(ty * self.height)

        try:
            return bytes(map(lambda b: round(b*intensity) 
                if b*intensity > 0 
                else 0, 
                self.pixels[y][x])
            )
        except:
            pass