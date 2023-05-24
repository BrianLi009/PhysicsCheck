from z3 import * 

#Complex Functions
def crossc(v,w):
    return ((v[1]*w[2]-v[2]*w[1]).conjugate(), (v[2]*w[0]-v[0]*w[2]).conjugate(), (v[0]*w[1]-v[1]*w[0]).conjugate())

def dotc(v,w):
    return (v[0] * (w[0].conjugate()) + v[1] * (w[1].conjugate()) + v[2] * (w[2].conjugate()))

def normc2(v):
    return (v[0].r*v[0].r + v[0].i*v[0].i + v[1].r*v[1].r + v[1].i*v[1].i + v[2].r*v[2].r + v[2].i*v[2].i)

def norm2(v):
    return (v[0]*v[0] + v[1]*v[1] + v[2]*v[2])

def normalizer(v):
    magnitude = z3.Sqrt(norm2(v))
    return (v[0]/magnitude, v[1]/magnitude, v[2]/magnitude)

def normalizec(v):
    magnitude = z3.Sqrt(normc2(v))
    v[0].r = v[0].r/magnitude
    v[0].i = v[0].i/magnitude
    v[1].r = v[1].r/magnitude
    v[1].i = v[1].i/magnitude
    v[2].r = v[2].r/magnitude
    v[2].i = v[2].i/magnitude
    return v

#Real Functions

def cross(v,w):
    return ((v[1]*w[2]-v[2]*w[1]), (v[2]*w[0]-v[0]*w[2]), (v[0]*w[1]-v[1]*w[0]))

#define new variable, pass 

def dot(v,w):
    return (v[0]*w[0] + v[1]*w[1] + v[2]*w[2])

def _to_complex(a):
    if isinstance(a, ComplexExpr):
        return a
    else:
        return ComplexExpr(a, RealVal(0))

def _is_zero(a):
    return (isinstance(a, int) and a == 0) or (is_rational_value(a) and a.numerator_as_long() == 0)

class ComplexExpr:
    def __init__(self, r, i):
        self.r = r
        self.i = i

    def __add__(self, other):
        other = _to_complex(other)
        return ComplexExpr(self.r + other.r, self.i + other.i)

    def __radd__(self, other):
        other = _to_complex(other)
        return ComplexExpr(other.r + self.r, other.i + self.i)

    def __sub__(self, other):
        other = _to_complex(other)
        return ComplexExpr(self.r - other.r, self.i - other.i)

    def __rsub__(self, other):
        other = _to_complex(other)
        return ComplexExpr(other.r - self.r, other.i - self.i)

    def __mul__(self, other):
        other = _to_complex(other)
        return ComplexExpr(self.r*other.r - self.i*other.i, self.r*other.i + self.i*other.r)

    def __mul__(self, other):
        other = _to_complex(other)
        return ComplexExpr(other.r*self.r - other.i*self.i, other.i*self.r + other.r*self.i)

    def conjugate(self):
        return ComplexExpr(self.r, -self.i)

    def inv(self):
        den = self.r*self.r + self.i*self.i
        return ComplexExpr(self.r/den, -self.i/den)

    def __div__(self, other):
        inv_other = _to_complex(other).inv()
        return self.__mul__(inv_other)

    def __rdiv__(self, other):
        other = _to_complex(other)
        return self.inv().__mul__(other)

    def __eq__(self, other):
        other = _to_complex(other)
        return And(self.r == other.r, self.i == other.i)

    def __neq__(self, other):
        return Not(self.__eq__(other))

    def simplify(self):
        return ComplexExpr(simplify(self.r), simplify(self.i))

    def repr_i(self):
        if is_rational_value(self.i):
            return "%s*I" % self.i
        else:
            return "(%s)*I" % str(self.i)

    def __repr__(self):
        if _is_zero(self.i):
            return str(self.r)
        elif _is_zero(self.r):
            return self.repr_i()
        else:
            return "%s + %s" % (self.r, self.repr_i())

def Complex(a):
    return ComplexExpr(Real('%s.r' % a), Real('%s.i' % a))

def evaluate_cexpr(m, e):
    return ComplexExpr(m[e.r], m[e.i])
