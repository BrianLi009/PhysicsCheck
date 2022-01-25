import networkx as nx
from networkx.algorithms import isomorphism
g1 = nx.complete_graph(5)
g2 = nx.complete_graph(4)
gm = isomorphism.GraphMatcher(g1,g2)
#g1 contain g2
print(gm.subgraph_is_isomorphic())