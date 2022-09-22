import math

def verify_sat(g, filename):
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
        if count % 4 == 0:
            vec_dict[int(i)] = [float(lines[count+1]), float(lines[count+2]), float(lines[count+3])]
        count += 1
    dot_product_verify = True
    for vec in g:
        for adj_vec in g[vec]:
            dot_prod = vec_dict[vec][0]*vec_dict[adj_vec][0]+vec_dict[vec][1]*vec_dict[adj_vec][1]+vec_dict[vec][2]*vec_dict[adj_vec][2]
            if not (math.isclose(0, dot_prod, abs_tol=0.00001)):
                dot_product_verify = False
    if dot_product_verify:
        print ("all adjacent vertices has corresponding orthogonal vectors")
    colinear_verify = True
    for vec_1 in g:
        for vec_2 in g:
            if vec_1 != vec_2:
                cross_product_1 = vec_dict[vec_1][1]*vec_dict[vec_2][2] - vec_dict[vec_1][2]*vec_dict[vec_2][1]
                cross_product_2 = vec_dict[vec_1][2]*vec_dict[vec_2][0] - vec_dict[vec_1][0]*vec_dict[vec_2][2]
                cross_product_3 = vec_dict[vec_1][0]*vec_dict[vec_2][1] - vec_dict[vec_1][1]*vec_dict[vec_2][0]
                if math.isclose(0, cross_product_1, abs_tol=0.00001) and math.isclose(0, cross_product_2, abs_tol=0.00001) and math.isclose(0, cross_product_3, abs_tol=0.00001):
                    colinear_verify = False
    if dot_product_verify:
        print ("all non-adjacent vertices has corresponding noncolinear vectors")
    if dot_product_verify and colinear_verify:
        return True


