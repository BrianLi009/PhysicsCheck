import pandas as pd
subgraph_data = pd.read_csv('19-subgraph.csv')
with open('embed_result (19, subgraph all solved).txt') as f:
    lines = f.readlines()
count = 0
for line in lines:
    print (line)
    count += 1
    if count %2 == 1:
        #graph info
        try:
            info = list(line.split(' '))
            label = info[2][:-1]
            result = info[3]
            vertices = info[5]
            edges = info[7][:-1]
        except:
            info = list(line.split(' '))
            label = info[2][:-1]
            result = info[3]
            vertices = info[4]
            edges = info[5][:-1]
        """print (label)
        print (result)
        print (vertices)
        print (edges)"""
        subgraph_data.at[count, 'label'] = label
        subgraph_data.at[count, 'result'] = result
        subgraph_data.at[count, 'vertices'] = vertices
        subgraph_data.at[count, 'edges'] = edges
    else:
        #runtime
        subgraph_data.at[count-1, 'runtime'] = line
    print (subgraph_data.head())

subgraph_data.to_csv('19_subgraph.csv', encoding='utf-8', index=False)
