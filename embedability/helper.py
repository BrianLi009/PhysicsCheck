def cross(v,w):
    return (v[1]*w[2]-v[2]*w[1], v[2]*w[0]-v[0]*w[2], v[0]*w[1]-v[1]*w[0])

def dot(v,w):
    return (v+'[0]'+'*'+w+'[0]' + '+' + v+'[1]'+'*'+w+'[1]' + '+' + v +'[2]'+'*'+w+'[2]')

def nested_cross(x):
    if isinstance(x, tuple):
        return 'cross({},{})'.format(*map(nested_cross, x))
    str = 'v{}'.format(x)
    return str