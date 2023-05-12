from decimal import *
import math

getcontext().prec = 150

def verify_sat_c(g, filename):
    """
    verify the embeddable solution in [filename] only using edge relations.
    """
    f = open(filename, "r")
    file_data = f.read()
    lines = file_data.splitlines()
    f.close()
    vec_dict = {}
    count = 0
    for i in lines:
        if count % 7 == 0:
            vec_dict[int(i)] = [Decimal(lines[count+1]), Decimal(lines[count+2]), Decimal(lines[count+3]), Decimal(lines[count+4]), Decimal(lines[count+5]), Decimal(lines[count+6])]
        count += 1
    dot_product_verify = True
    for vec in g:
        for adj_vec in g[vec]:
            v = (complex(vec_dict[vec][0],vec_dict[vec][1]), complex(vec_dict[vec][2],vec_dict[vec][3]), complex(vec_dict[vec][4],vec_dict[vec][5]))
            w = (complex(vec_dict[adj_vec][0],vec_dict[adj_vec][1]), complex(vec_dict[adj_vec][2],vec_dict[adj_vec][3]), complex(vec_dict[adj_vec][4],vec_dict[adj_vec][5]))
            dot_prod = v[0]*w[0].conjugate() + v[1]*w[1].conjugate() + v[2]*w[2].conjugate()
            if not (math.isclose(dot_prod.real, 0, abs_tol=0.00001) and math.isclose(dot_prod.imag, 0, abs_tol=0.00001)):
                dot_product_verify = False
    if dot_product_verify:
        print ("all adjacent vertices has corresponding orthogonal vectors")
    colinear_verify = True
    for vec_1 in g:
        for vec_2 in g:
            if vec_1 != vec_2:
                v = (complex(vec_dict[vec_1][0],vec_dict[vec_1][1]), complex(vec_dict[vec_1][2],vec_dict[vec_1][3]), complex(vec_dict[vec_1][4],vec_dict[vec_1][5]))
                w = (complex(vec_dict[vec_2][0],vec_dict[vec_2][1]), complex(vec_dict[vec_2][2],vec_dict[vec_2][3]), complex(vec_dict[vec_2][4],vec_dict[vec_2][5]))
                cross_product_1 = (v[1]*w[2]-v[2]*w[1]).conjugate()
                cross_product_2 = (v[2]*w[0]-v[0]*w[2]).conjugate()
                cross_product_3 = (v[0]*w[1]-v[1]*w[0]).conjugate()
                if math.isclose(0, cross_product_1.real, abs_tol=0.00001) and math.isclose(0, cross_product_2.real, abs_tol=0.00001) and math.isclose(0, cross_product_3.real, abs_tol=0.00001) and math.isclose(0, cross_product_1.imag, abs_tol=0.00001) and math.isclose(0, cross_product_2.imag, abs_tol=0.00001) and math.isclose(0, cross_product_3.imag, abs_tol=0.00001):
                    colinear_verify = False
    if colinear_verify:
        print ("every pair of non-adjacent vertices has corresponding noncolinear vectors")
    if dot_product_verify and colinear_verify:
        return True
