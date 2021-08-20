import math

def matching_upper(v):
    num_edges = math.comb(v, 2)
    all_entries = list(range(1, num_edges+1))
    matching = {}
    all_cols = []
    col_size = 1
    while all_entries != []:
        col = []
        while len(col) < col_size:
            col.append(all_entries.pop(0))
        col_size += 1
        all_cols.append(col)
    original_order = list(range(1, num_edges+1))
    i = 0
    while i < original_order[-1]:
        for col in all_cols:
            if col != []:
                matching[original_order[i]] = col.pop(0)
                i += 1
    return matching

def relabel_from_matching(constraint, matches):
    """input a constraint, relable it based on matches"""
    new_constraint = []
    for variable in constraint:
        if abs(variable) in matches.keys():
            if variable > 0:
                new_var = matches[abs(variable)]
            else:
                new_var = -matches[abs(variable)]
            new_constraint.append(new_var)
        else:
            new_constraint.append(variable)
    return new_constraint
