class V3(object):
  
  def __init__(self, x, y, z = 0, w = 0):
    self.x = x
    self.y = y
    self.z = z

  # Suma
  def __add__(self, other):
    return V3((self.x + other.x), (self.y + other.y), (self.z + other.z))

  # Resta
  def __sub__(self, other):
    return V3((self.x - other.x), (self.y - other.y), (self.z - other.z))

  # Multiplicacion
  def __mul__(self, other):

    # Vector por un numero
    if ((type(other) == int) or (type(other) == float)):
      return V3((other * self.x), (other * self.y), (other * self.z))

    # Producto cruz
    return V3(
      ((self.y * other.z) - (self.z * other.y)),
      ((self.z * other.x) - (self.x * other.z)),
      ((self.x * other.y) - (self.y * other.x)),
    )

  # Producto punto
  def __matmul__(self, other):
    return ((self.x * other.x) + (self.y * other.y) + (self.z * other.z))

  #  longitud de un vector.
  def length(self):
    return (((self.x ** 2) + (self.y ** 2) + (self.z ** 2)) ** 0.5)

  # vector normalizado.
  def norm(self):
    return (self * (1 / self.length())) if (self.length() > 0) else V3(0, 0, 0)

  # Redondea las coordenadas del vector.
  def round_coords(self):
    self.x = round(self.x)
    self.y = round(self.y)
    self.z = round(self.z)

  # Vector en String
  def __repr__(self):
    return f"<{self.x}, {self.y}, {self.z}>"