import time
start_time = time.time()

import sys
from gexf import Gexf

lsArgs = sys.argv

stats_file = open(lsArgs[1], 'r')
stats_lines = stats_file.readlines()
stats_file.close()

dump_file = open(lsArgs[2], 'r')
dump_lines = dump_file.readlines()
dump_file.close()

dump_bcast = open(lsArgs[3], 'r')
dump_blines = dump_bcast.readlines()
dump_bcast.close()

if (len(lsArgs) > 4):
	score_file = open(lsArgs[4], 'r')
	score_lines = score_file.readlines()
	score_file.close()

gexf = Gexf("Pedro and David", "Dynamic graph")
graph = gexf.addGraph("directed", "dynamic", "Graph")
idTotalNodeDuration = graph.addNodeAttribute("Total Duration", "0.0", "float") #name, default, type
idNodeWeight = graph.addNodeAttribute("Weight", "1.0", "float")
idNodeHighestScore = graph.addNodeAttribute("Highest Score", "0.0", "float")
idTotalEdgeDuration = graph.addEdgeAttribute("Total Duration", "0.0", "float")
idLinkType = graph.addEdgeAttribute("Type", "None", "string")

#...:: Nodes ::................................................................................................................................#

lsNodes = []

for line in stats_lines:

	if (line.startswith('CT_Process')): break
	if (line.startswith('Thread')):
	
		totalDuration = (line.split(' '))[5]
		lbl = ((line.split(' '))[1].split('_'))[0]
		id = ((line.split('_'))[0])[9:]
		wgt = line.split('(')[1].replace(' %)\n', '')
		lsNodes.append(id)
		n = graph.addNode(str(id), str(lbl).replace('P#', ''))
		n.addAttribute(idNodeWeight, wgt)
		n.addAttribute(idTotalNodeDuration, totalDuration)
		
		if (len(lsArgs) > 4):
			container = line.split(' ')[1]
			hs = 0.0
			for l2 in range(len(score_lines)):
			
				if (container in score_lines[l2]):
				
					l2 += 1
					while (l2 < len(score_lines) and score_lines[l2].startswith('+')):
					
						score = score_lines[l2].split('	')[2].split('=')[1].replace(')\n', '')
						if (score > hs): hs = score
						l2 += 1
					
					break
			
			n.addAttribute(idNodeHighestScore, hs)

#...:: Edges ::................................................................................................................................#

dicLinks = {}

for n1 in lsNodes:
	for n2 in lsNodes:	
		if (n2 != n1):		
			dicLinks[str(n1) + '_' + str(n2)] = [[], [], [], []] # []start []end []weight

#P2P----------------------------------------------------------------------------------------
del(dump_lines[0])
dl = list(reversed(dump_lines))

for l1 in range(len(dl)):

	line1 = dl[l1].split()
	nodesLink = str(line1[0]) + '_' + str(line1[1])
	
	if len((dicLinks[nodesLink])[0]) == 0:
	
		(dicLinks[nodesLink])[0].append(float(line1[4]))
		(dicLinks[nodesLink])[1].append(float(line1[11]))
		(dicLinks[nodesLink])[2].append(float(line1[2]))
		(dicLinks[nodesLink])[3].append('P2P')
		
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
				if (line1[11] < float(((dicLinks[nodesLink])[1])[i])): line1[2] = float(((dicLinks[nodesLink])[2])[i])
				
				(dicLinks[nodesLink])[0].append(newStart)
				(dicLinks[nodesLink])[1].append(newEnd)
				(dicLinks[nodesLink])[2].append(newWeight)
				(dicLinks[nodesLink])[3].append('P2P')
			
			(dicLinks[nodesLink])[0].append(float(line1[4]))
			(dicLinks[nodesLink])[1].append(float(line1[11]))
			(dicLinks[nodesLink])[2].append(float(line1[2]))
			(dicLinks[nodesLink])[3].append('P2P')

#BCAST--------------------------------------------------------------------------------------------------------
del(dump_blines[0])
dlb = list(reversed(dump_blines))

for lb1 in range(len(dlb)):

	bline1 = dlb[lb1].split()
	bcast_source = str(bline1[2])
	
	for bMsg in range(6, len(bline1), 3):
	
		nodesLink = bcast_source + '_' + ((bline1[bMsg].split('#'))[1]).replace('_T', '')
	
		bline1[bMsg+2] = bline1[bMsg+2].replace(']', '')
		if len((dicLinks[nodesLink])[0]) == 0:
		
			(dicLinks[nodesLink])[0].append(float(bline1[bMsg+1]))
			(dicLinks[nodesLink])[1].append(float(bline1[bMsg+2]))
			(dicLinks[nodesLink])[2].append(float(1))
			(dicLinks[nodesLink])[3].append('Collective')
			print '+1'
			
		else:
			
			t = -1
			while float(bline1[bMsg+1]) < float(((dicLinks[nodesLink])[0])[t]) and float(((dicLinks[nodesLink])[0])[t]) != float(((dicLinks[nodesLink])[0])[0]):
				t -= 1
			
			for i in range(t, 0):
			
				if float(((dicLinks[nodesLink])[1])[i]) > float(bline1[bMsg+1]):
				
					newStart = float(bline1[bMsg+1])
					newEnd = min(float(((dicLinks[nodesLink])[1])[i]), float(bline1[bMsg+2]))
					newWeight = float(((dicLinks[nodesLink])[2])[i]) + 1
					bline1[bMsg+2] = max(float(bline1[bMsg+2]), float(((dicLinks[nodesLink])[1])[i]))
					bline1[bMsg+1] = newEnd
					((dicLinks[nodesLink])[1])[i] = newStart
					if (bline1[bMsg+2] < float(((dicLinks[nodesLink])[1])[i])): bline1[2] = float(((dicLinks[nodesLink])[2])[i])
					
					(dicLinks[nodesLink])[0].append(newStart)
					(dicLinks[nodesLink])[1].append(newEnd)
					(dicLinks[nodesLink])[2].append(newWeight)
					(dicLinks[nodesLink])[3].append('Collective')
				
				(dicLinks[nodesLink])[0].append(float(bline1[bMsg+1]))
				(dicLinks[nodesLink])[1].append(float(bline1[bMsg+2]))
				(dicLinks[nodesLink])[2].append(float(1))
				(dicLinks[nodesLink])[3].append((dicLinks[nodesLink])[3][i])
			
#INSERTION------------------------------------------------------------------------------------------
			
id = 0
for item in dicLinks:

	for i in range(0, len((dicLinks[item])[0])):
		
		#if float(((dicLinks[item])[0])[i]) != float(((dicLinks[item])[1])[i]):
		
		id += 1
		srcdst = item.split('_')
		edgeDuration = float(((dicLinks[item])[1])[i]) - float(((dicLinks[item])[0])[i])
		e = graph.addEdge(str(id), str(srcdst[0]), str(srcdst[1]), float(((dicLinks[item])[2])[i]), str(((dicLinks[item])[0])[i]), str(((dicLinks[item])[1])[i]), str(item))
		e.addAttribute(idTotalEdgeDuration, str(edgeDuration))
		e.addAttribute(idLinkType, str(((dicLinks[item])[3])[i]))
		print id
			
#..............................................................................................................................................#

fname = lsArgs[1].split('\\')
fname = fname[-1]
gexf_file = open(('Grafos/' + 'grafo' + (fname.split('.'))[0]).replace('arq\\', '') + ".gexf", "w")
gexf.write(gexf_file)

print("::.. %s seconds ..::" % (time.time() - start_time))