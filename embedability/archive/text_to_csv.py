import pandas as pd
#subgraph_data = pd.read_csv('19-subgraph.csv')
with open('embed_result(n=12).txt') as f:
    lines = f.readlines()
count = 0
unsat_lst =[]
for line in lines:
    #print (line)
    count += 1
    if count %2 == 1:
        #graph info
        info = list(line.split(' '))
        label = info[2][:-1]
        result = info[3]
        vertices = info[4]
        edges = info[5][:-1]
        if result == 'unsat':
            unsat_lst.append(label)
        """print (label)
        print (result)
        print (vertices)
        print (edges)"""
        """subgraph_data.at[count, 'label'] = label
        subgraph_data.at[count, 'result'] = result
        subgraph_data.at[count, 'vertices'] = vertices
        subgraph_data.at[count, 'edges'] = edges"""
    else:
        #runtime
        #subgraph_data.at[count-1, 'runtime'] = line
        pass
print (len(unsat_lst))

#subgraph_data.to_csv('19_subgraph.csv', encoding='utf-8', index=False)

with open('squarefree_12.txt') as g:
    lines = g.readlines()
count = 0
for line in lines:
    count += 1
    if str(count) in unsat_lst:
        g6_string = list(line.split(": "))[1][:-1]
        print (g6_string)