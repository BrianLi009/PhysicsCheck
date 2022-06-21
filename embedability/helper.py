from z3 import * 

def cross(v,w):
    return (v[1]*w[2]-v[2]*w[1], v[2]*w[0]-v[0]*w[2], v[0]*w[1]-v[1]*w[0])

def dot(v,w):
    return (v+'[0]'+'*'+w+'[0]' + '+' + v+'[1]'+'*'+w+'[1]' + '+' + v +'[2]'+'*'+w+'[2]')

def nested_cross(x):
    if isinstance(x, tuple):
        return 'cross({},{})'.format(*map(nested_cross, x))
    str = 'v{}'.format(x)
    return str

"""def complex_mult(a,b,c,d):
    #encode a+bi * c+di = (ac-bd, ad+bc)
    return (ac-bd, ad+bc)

def complex_minus(a,b,c,d):
    return (a-c, b-d)"""

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

