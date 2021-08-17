from embedability import *
from cross_product import *
import networkx as nx

g6_string = 'JRPCSGoAgJ_'
edge_lst = g6_to_edge(g6_string)
relations = embedability(edge_lst)
print (relations)
output_clause(relations, "11", [8,9,10])