import time
start_time = time.time()

import sys
from gexf import Gexf

lsArgs = sys.argv

stats_file = open(lsArgs[2], 'r')
stats_lines = stats_file.readlines()
stats_file.close()

dump_file = open(lsArgs[4], 'r')
dump_lines = dump_file.readlines()
dump_file.close()

gexf = Gexf("Pedro and David", "Dynamic graph")
graph = gexf.addGraph("directed", "dynamic", "Graph")
idTotalNodeDuration = graph.addNodeAttribute("Total Duration", "0.0", "float") #name, default, type
idTotalEdgeDuration = graph.addEdgeAttribute("Total Duration", "0.0", "float")

#...:: Nodes ::................................................................................................................................#

lsNodes = []

for line in stats_lines:

	if (line.startswith('Thread')):
	
		totalDuration = (line.split(' '))[5]
		lbl = ((line.split(' '))[1].split('_'))[0]
		id = ((line.split('_'))[0])[9:]
		lsNodes.append(id)
		n = graph.addNode(str(id), str(lbl))
		n.addAttribute(idTotalNodeDuration, totalDuration)

#...:: Edges ::................................................................................................................................#

dicLinks = {}

for n1 in lsNodes:
	for n2 in lsNodes:	
		if (n2 != n1):		
			dicLinks[str(n1) + '_' + str(n2)] = [[], [], []] # []start []end []weight

del(dump_lines[0])
dl = list(reversed(dump_lines))

for l1 in range(len(dl)):

	line1 = dl[l1].split()
	nodesLink = str(line1[0]) + '_' + str(line1[1])
	
	if len((dicLinks[nodesLink])[0]) == 0:
	
		(dicLinks[nodesLink])[0].append(float(line1[4]))
		(dicLinks[nodesLink])[1].append(float(line1[11]))
		(dicLinks[nodesLink])[2].append(float(line1[2]))
		
	else:
		
		t = -1
		while float(line1[4]) < float(((dicLinks[nodesLink])[0])[t]) and float(((dicLinks[nodesLink])[0])[t]) != float(((dicLinks[nodesLink])[0])[0]):
			t -= 1
		
		for i in range(t, 0):
		
			if float(((dicLinks[nodesLink])[1])[i]) > float(line1[4]):
			
				newStart = float(line1[4])
				newEnd = min(float(((dicLinks[nodesLink])[1])[i]), float(line1[11]))
				newWeight = float(((dicLinks[nodesLink])[2])[i]) + float(line1[2])
				line1[11] = max(float(line1[11]), float(((dicLinks[nodesLink])[1])[i]))
				line1[4] = newEnd
				((dicLinks[nodesLink])[1])[i] = newStart
				
				(dicLinks[nodesLink])[0].append(newStart)
				(dicLinks[nodesLink])[1].append(newEnd)
				(dicLinks[nodesLink])[2].append(newWeight)
			
			(dicLinks[nodesLink])[0].append(float(line1[4]))
			(dicLinks[nodesLink])[1].append(float(line1[11]))
			(dicLinks[nodesLink])[2].append(float(line1[2]))

id = 0
for item in dicLinks:

	for i in range(len((dicLinks[item])[0])):
		
		if float(((dicLinks[item])[0])[i]) != float(((dicLinks[item])[1])[i]):
		
			id += 1
			srcdst = item.split('_')
			edgeDuration = float(((dicLinks[item])[1])[i]) - float(((dicLinks[item])[0])[i])
			e = graph.addEdge(str(id), str(srcdst[0]), str(srcdst[1]), float(((dicLinks[item])[2])[i]), str(((dicLinks[item])[0])[i]), str(((dicLinks[item])[1])[i]), str(item))
			e.addAttribute(idTotalEdgeDuration, str(edgeDuration))

#..............................................................................................................................................#

gexf_file = open((lsArgs[2].split('.'))[0] + "_gexf.gexf", "w")
gexf.write(gexf_file)

print("::.. %s seconds ..::" % (time.time() - start_time))