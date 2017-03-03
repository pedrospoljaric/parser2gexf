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
idTotalNodeDuration = graph.addNodeAttribute("Total Duration", "0.0", "float")
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
			dicLinks[str(n1) + '_' + str(n2)] = float(0)

del(dump_lines[0])

for l1 in range(len(dump_lines)):

	line1 = dump_lines[l1].split()
	nodesLink = str(line1[0]) + '_' + str(line1[1])
	edgeStart = max(dicLinks[nodesLink], float(line1[4]))
	edgeEnd = max(edgeStart, float(line1[9]))
	dicLinks[nodesLink] = edgeEnd
	
	edgeDuration = edgeEnd - edgeStart
		
	e = graph.addEdge(str(l1), str(line1[0]), str(line1[1]), float(line1[2]), str(edgeStart), str(edgeEnd), str(line1[0]) +'_'+ str(line1[1]))
	e.addAttribute(idTotalEdgeDuration, edgeDuration)

#..............................................................................................................................................#

gexf_file = open((lsArgs[2].split('.'))[0] + "_gexf.gexf", "w")
gexf.write(gexf_file)

print("::.. %s seconds ..::" % (time.time() - start_time))