
class Obj(object):
    def __init__(self, filename):
        with open(filename) as f:
            self.lines = f.read().splitlines()
            self.vertex = []
            self.faces = []
            self.tvertex = []
            
            i = 1
            
            for line in self.lines:

                if not line or line.startswith("#"):
                    continue

                prefix, value =  line.split(' ', 1)

                i += 1
                
                if prefix == 'v':
                    self.vertex.append(list(map(float, value.split(' '))))
                if prefix == 'vt':
                    self.tvertex.append(list(map(float, value.split(' '))))
                elif prefix == 'f':
                    try:
                        self.faces.append([list(map(int , face.split('/'))) for face in value.split(' ')])
                    except:
                        self.faces.append([list(map(int , face.split('//'))) for face in value.split(' ')])

