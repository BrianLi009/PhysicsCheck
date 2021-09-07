import itertools
from collections import Counter, OrderedDict
from itertools import repeat, chain

def all_neighbors(edge_lst, v):
    neighbors = []
    for edge in edge_lst:
        if v in edge:
            v_index = edge.index(v)
            if v_index == 0:
                neighbor = edge[1]
            else:
                neighbor = edge[0]
            neighbors.append(neighbor)
    return neighbors

def find_ortho(edge_lst, unassigned, assigned):
    # return a dictionary for all unassigned vertices and their adjacent distinct assigned if they exist
    dict = {}
    for v in unassigned:
        neighbors = all_neighbors(edge_lst, v) #a list of all neighbors of unassigned vertex v
        if sum(el in neighbors for el in assigned) >= 2: #if more than one neighbor are in assigned list
            adjacent_vertices = [value for value in neighbors if value in assigned] 
            dict[v] = adjacent_vertices
        break
    return dict

def sort_by_degree(edge_lst):
    """given an edge_lst, return a list based on number of degrees"""
    """edge_lst starts from 0"""
    edge_lst = list(sum(edge_lst, ()))
    edge_lst = list(chain.from_iterable(repeat(i, c) for i,c in Counter(edge_lst).most_common()))
    edge_lst =  list(OrderedDict.fromkeys(edge_lst))
    return edge_lst

def embedability(edge_lst, vertices_lst):
    orthogonal_relations = []
    colinear_relations = []
    assignment = {}
    unassigned_edges = edge_lst.copy()
    assigned_edges = []
    unassigned = vertices_lst.copy()
    assigned = [] #at the very beginning, all vertices are unassigned
    potential_edges = list(itertools.combinations(vertices_lst,2))
    while unassigned != []:
        vertex = unassigned[0] #here we probably want to pick vertices with the highest degrees
        assignment[vertex] = [vertex]
        assigned.append(unassigned.pop(unassigned.index(vertex))) #mark vertex as free
        orthogonal_dict = find_ortho(edge_lst, unassigned, assigned) #a dictionary
        while len(orthogonal_dict)>0:
            #pick a vertex w adjacent to w1 and w2
            for v in list(orthogonal_dict):
                if len(orthogonal_dict[v]) > 1:
                    v_1 = orthogonal_dict[v][0] #we'll just pick the first two for now for runtime's sake
                    v_2 = orthogonal_dict[v][1]
                    if v > v_1:
                        edge_1 = (v_1, v)
                    else:
                        edge_1 = (v, v_1)
                    if v > v_2:
                        edge_2 = (v_2, v)
                    else:
                        edge_2 = (v, v_2)
                    assigned_edges.append(edge_1)
                    assigned_edges.append(edge_2)
                    unassigned_edges.remove(edge_1)
                    unassigned_edges.remove(edge_2)
                    assignment[v] = [v_1, v_2]
                    assigned.append(unassigned.pop(unassigned.index(v)))
                orthogonal_dict = find_ortho(edge_lst, unassigned, assigned)
    for pairs in potential_edges:
        if pairs not in edge_lst:
            colinear_relations.append(pairs)
    for edges in unassigned_edges:
        orthogonal_relations.append(edges)
    return [orthogonal_relations, colinear_relations, assignment, vertices_lst]

