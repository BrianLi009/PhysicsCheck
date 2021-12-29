We want to show that the four extra graphs do not belong in the existing results by Bas and Sanders


```python
import itertools
import math
```


```python
from collections import Counter
from itertools import chain

def check_squarefree(graph):
    vertices_lst = list(graph.vertices())
    possible_c4 = list(itertools.combinations(vertices_lst, 4))
    squares = False
    for c4 in possible_c4:
        edge_lst = graph.subgraph(list(c4)).edges()
        if len(edge_lst) >= 4:
            res = Counter(chain(*edge_lst))
            del res[None]
            value_lst = []
            for value in res.values():
                value_lst.append(value)
            if value_lst == [2,2,2,2]:
                print ("squares exists")
                squares = True
    if squares == False:
        print ("the graph is squarefree")
```


```python
def check_all_triangle(graph):
    vertices_lst = list(graph.vertices())
    edge_lst = [(a, b) for (a, b, c) in graph.edges()]
    good_vertex = []
    for vertex in vertices_lst:
        adjacent_lst = graph.neighbors(vertex)
        all_possible = list(itertools.combinations(adjacent_lst, 2))
        for comb in all_possible:
            if comb in edge_lst or Reverse(comb) in edge_lst:
                good_vertex.append(vertex)
    for v in vertices_lst:
        if v not in good_vertex:
            print (v)
            return False
    return True

def Reverse(tuples):
    new_tup = tuples[::-1]
    return new_tup
```


```python
def colorable(graph):
    """
    given a list of edges, return a valid coloring if possible
    we can move this function to PySAT to change the SAT solver we are using.
    """
    solver = SAT()
    edge_lst = [(a+1, b+1) for (a, b, c) in graph.edges()]
    for edge in edge_lst:
        solver.add_clause(tuple([-edge[0],-edge[1]])) #no two adjacent vertices can be both 1
    vertices_lst = list(range(1, (max(max(edge_lst,key=lambda item:item[1])))+1))
    potential_triangles = list(itertools.combinations(vertices_lst, 3))
    for triangle in potential_triangles:
        v1 = triangle[0]
        v2 = triangle[1]
        v3 = triangle[2]
        if ((v1, v2) in edge_lst or (v2,v1) in edge_lst) and ((v2, v3) in edge_lst or (v3, v2) in edge_lst) and ((v1, v3) in edge_lst or (v3,v1) in edge_lst):
            solver.add_clause((v1,v2,v3))
            solver.add_clause((-v1, -v2))
            solver.add_clause((-v2, -v3))
            solver.add_clause((-v1, -v3))
        """
        if the triangle exists in this particular graph, it must satisfy 010 coloring
        """
    return solver()
```

We first show that these four graphs are non-isomorphic to any of the existing graph, and non-isomoprhic to one another as well.


```python
ext_1 = 'S????CB@GoD?LCQPI@BCCaaEPBD@GEG@C'
ext_2 = 'S???GKGCGqCMI_QAIAR?IaGAOGD?CMG@O'
ext_3 = 'S???GKGCGqCMIAOgIAB?EaGAOHD?GMG@O'
ext_4 = 'S????CCA?`b_GUI`GTI_GW?eDEC_OE?@G'
new_candidates = [Graph(ext_1), Graph(ext_2), Graph(ext_3), Graph(ext_4)]
print ('there are ' + str(len(new_candidates)) + ' new candidates')
old_candidates = []
file1 = open('solutions_20.txt', 'r')
for line in file1:
    G = Graph(line[:-1])
    old_candidates.append(G)
print ('there are ' + str(len(old_candidates)) + ' old candidates')
for comparison in itertools.combinations(new_candidates, 2):
    graph_1 = comparison[0]
    graph_2 = comparison[1]
    if graph_1.is_isomorphic(graph_2):
        print ("there exist isomorphic graphs")
print ("the 4 new candidates are not isomorphic to each other.")
```

    there are 4 new candidates
    there are 441 old candidates
    the 4 new candidates are not isomorphic to each other.



```python
print ("check that every graph is squarefree")
for graph in new_candidates:
    check_squarefree(graph)
```

    check that every graph is squarefree
    the graph is squarefree
    the graph is squarefree
    the graph is squarefree
    the graph is squarefree



```python
print ("check that every vertex is part of a triangle")
for graph in new_candidates:
    print (check_all_triangle(graph))
```

    check that every vertex is part of a triangle
    True
    True
    True
    True



```python
print ("check the minimum degree is 3")
for graph in new_candidates:
    print (graph.degree_sequence())
```

    check the minimum degree is 3
    [6, 5, 5, 5, 5, 5, 5, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 3, 3]
    [5, 5, 5, 5, 5, 5, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 3, 3]
    [5, 5, 5, 5, 5, 5, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 3, 3]
    [6, 6, 6, 6, 6, 5, 4, 4, 4, 4, 4, 3, 3, 3, 3, 3, 3, 3, 3, 3]



```python
print ("check the graph is non-colorable")
for graph in new_candidates:
    print (colorable(graph))
```

    check the graph is non-colorable
    False
    False
    False
    False



```python

```
