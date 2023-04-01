import networkx as nx
from networkx.algorithms import isomorphism
from verify import *

def maple_to_edges(input, v):
    str_lst = input.split()[1:-1]
    edge_lst = []
    for j in range(0, v):
        for i in range(0, j):
            edge_lst.append((i,j))
    actual_edges = []
    for i in str_lst:
        indicator = int(i)
        if indicator > 0:
            actual_edges.append(edge_lst[int(i)-1])
    return actual_edges

#maple_to_edges("a -1 -2 -3 -4 -5 -6 -7 -8 -9 -10 -11 -12 -13 -14 -15 -16 -17 -18 -19 -20 -21 -22 -23 -24 -25 -26 -27 28 -29 -30 -31 -32 -33 -34 35 36 -37 -38 -39 -40 -41 42 -43 -44 -45 -46 -47 -48 -49 50 -51 -52 -53 54 -55 -56 -57 -58 59 -60 -61 -62 -63 64 65 66 -67 -68 -69 70 71 -72 -73 74 -75 -76 -77 -78 -79 -80 81 -82 -83 -84 85 -86 -87 -88 -89 -90 -91 -92 -93 94 -95 96 -97 -98 -99 -100 -101 -102 -103 104 105 -106 107 -108 -109 -110 111 -112 -113 -114 115 -116 -117 -118 -119 -120 -121 122 123 124 -125 -126 -127 -128 -129 -130 -131 132 -133 -134 -135 -136 137 -138 -139 -140 -141 142 143 -144 -145 -146 -147 -148 -149 150 -151 -152 -153 154 -155 -156 -157 158 -159 -160 -161 -162 -163 164 -165 -166 -167 -168 -169 -170 -171 172 -173 -174 175 -176 -177 -178 -179 -180 -181 -182 -183 184 -185 -186 -187 -188 189 -190 191 -192 193 -194 -195 -196 -197 198 -199 -200 -201 -202 -203 -204 -205 -206 207 -208 209 -210 211 212 -213 -214 -215 -216 -217 -218 -219 -220 -221 -222 -223 -224 225 226 -227 -228 -229 -230 -231 0", 22)

def test_minimal_2(file, order):
    #this approach should not be used
    my_file = open(file, "r")
    content = my_file.read()
    candidates = content.split("\n")
    my_file.close()
    graph_lst = []
    for g in candidates[:-1]:
        edge_lst = maple_to_edges(g, order)
        G = nx.Graph()
        G.add_edges_from(edge_lst)
        graph_lst.append(G)
    for graph in graph_lst:
        print ("checking " + str(graph_lst.index(graph)))
        minimum = True
        graph_17="a -1 -2 -3 -4 -5 -6 -7 -8 -9 -10 -11 -12 -13 -14 15 -16 -17 -18 -19 20 21 -22 -23 -24 25 -26 -27 28 -29 -30 31 -32 -33 -34 35 36 -37 -38 39 40 -41 42 -43 -44 -45 -46 47 -48 -49 -50 51 -52 -53 -54 55 -56 57 -58 59 -60 -61 -62 63 -64 -65 -66 -67 68 69 -70 71 -72 -73 -74 -75 -76 -77 78 79 -80 -81 -82 83 -84 -85 -86 -87 -88 -89 -90 91 92 -93 -94 95 -96 -97 -98 -99 -100 101 -102 -103 -104 105 106 -107 108 -109 -110 -111 -112 -113 114 -115 -116 -117 -118 -119 -120 121 122 -123 -124 -125 -126 -127 -128 -129 -130 131 -132 -133 -134 -135 136 0"
        edge_lst = maple_to_edges(graph_17, 17)
        G17 = nx.Graph()
        G17.add_edges_from(edge_lst)
        gm17 = isomorphism.GraphMatcher(graph, G17)
        if gm17.subgraph_is_monomorphic():
            print ("entering 17")
            minimum = False
        if minimum == True:
            print ("minimum ks system")
            output_f = open("minimal_ks_17_" + str(order) + ".exhaust", "a")
            output_f.write(candidates[graph_lst.index(graph)] + "\n")
            output_f.close()

test_minimal_2("22.exhaust", 22)


