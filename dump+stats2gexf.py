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
idTotalDuration = graph.addNodeAttribute("Total Duration", "0.0", "float")

#...:: Nodes ::................................................................................................................................#

for line in stats_lines:

	if (line.startswith('Thread')):
	
		totalDuration = (line.split(' '))[5]
		lbl = ((line.split(' '))[1].split('_'))[0]
		id = ((line.split('_'))[0])[9:]
		n = graph.addNode(str(id), str(lbl))
		n.addAttribute(idTotalDuration, totalDuration)

#...:: Edges ::................................................................................................................................#

lsRemove = []

dl = dump_lines
del(dl[0])

for l1 in range(len(dl)):

	for l2 in range(len(dl)):

		line1 = dl[l1].split()
		line2 = dl[l2].split()
		
		if (dl[l1] != dl[l2]) and (line1[0:2] == line2[0:2]) and (l1 not in lsRemove) and (l2 not in lsRemove):
		
			#start 4 end 5
			if (float(line1[4]) == float(line2[4])):
				if (float(line1[5]) < float(line2[5])):
					line1[5] = line2[5]				
				line1[2] = float(line1[2]) + float(line2[2])
				lsRemove.add(l2)
				
			elif (float(line1[4]) > float(line2[4])):
				if (float(line1[4]) <= float(line2[5])):
					if (float(line1[5]) == float(line2[5])):
						line1[4] = line2[4]
						line1[2] = float(line1[2]) + float(line2[2])
						lsRemove.add(l2)			
					elif (float(line1[5]) < float(line2[5])):
						line1[4] = line2[4]
						line1[5] = line2[5]
						line1[2] = float(line1[2]) + float(line2[2])
						lsRemove.add(l2)
				
			elif (float(line1[4]) < float(line2[4])):
				if (float(line1[5]) >= float(line2[4])):	
					if (float(line1[5]) < float(line2[5])):
						line1[5] = line2[5]						
					line1[2] = float(line1[2]) + float(line2[2])
					lsRemove.add(l2)
					
for i in range(len(dl)):

	if i not in lsRemove:
	
		line1 = dl[i].split()
		graph.addEdge(str(i), str(line1[0]), str(line1[1]), float(line1[2]), str(line1[4]), str(line1[5]), str(line1[0]) +'_'+ str(line1[1]))

#..............................................................................................................................................#

gexf_file = open((lsArgs[2].split('.'))[0] + "_gexf.gexf", "w")
gexf.write(gexf_file)