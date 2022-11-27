from collections import namedtuple

#------------------V2-----------------

V2 = namedtuple('Point2', ['x', 'y'])

def cross(v1, v2):
      return (
        v1.y * v2.z - v1.z * v2.y,
        v1.z * v2.x - v1.x * v2.z,
        v1.x * v2.y - v1.y * v2.x
      )
      
def bbox(*vertices):
  xs = [ vertex.x for vertex in vertices ]
  ys = [ vertex.y for vertex in vertices ]
  xs.sort()
  ys.sort()

  return V2(xs[0], ys[0]), V2(xs[-1], ys[-1])

def barycentric(A, B, C, P):

  bary = cross(
    V3(C.x - A.x, B.x - A.x, A.x - P.x), 
    V3(C.y - A.y, B.y - A.y, A.y - P.y)
  )

  if abs(bary[2]) < 1:
    return -1, -1, -1   # this triangle is degenerate, return anything outside

  return (
    1 - (bary[0] + bary[1]) / bary[2], 
    bary[1] / bary[2], 
    bary[0] / bary[2]
  )

#---------------------V3---------------------
class V3(object):
    # creacion del vector en 3D
    def __init__(self, x, y, z=0):
        self.x = x
        self.y = y
        self.z = z

    # suma
    def __add__(self, other):
        return V3(
            self.x + other.x,
            self.y + other.y,
            self.z + other.z
        )

    # resta
    def __sub__(self, other):
        return V3(
            self.x - other.x,
            self.y - other.y,
            self.z - other.z
        )

    # multiplicacion
    def __mul__(self, other):
        # si es escalar
        if (type(other) == int or type(other) == float):
            return V3(
                self.x * other,
                self.y * other,
                self.z * other
            )
        # si es vector retorna el producto cruz
        return V3(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x
        )

    # producto punto
    def __matmul__(self, other):
        return self.x * other.x + self.y * other.y + self.z * other.z

    # magnitud de un vector
    def length(self):
        return (self.x**2 + self.y**2 + self.z**2)**0.5

    def norm(self):
        return self * (1/self.length())

    # print bonito
    def __repr__(self):
        return "V3 (%s, %s, %s)" % (self.x, self.y, self.z)
    
    #se redondean cordenadas 
    def round_coords(self):
        self.x = round(self.x)
        self.y = round(self.y)
        self.z = round(self.z)