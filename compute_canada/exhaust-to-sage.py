import sys
#translate result from the exhaust file to edge lists readable by Sage
f=sys.argv[1]
o=int(sys.argv[2])

our_candidate = []
file1 = open(f, 'r')
for line in file1:
    info = line[2:-2].split(' ')[:-1]
    potential_edge = []
    for j in range(o):
        for i in range(o):
            if i < j:
                potential_edge.append((i,j))
    actual_edge = []
    for i in range(len(potential_edge)):
        if int(info[i]) > 0:
            actual_edge.append(potential_edge[i])
    print (actual_edge)