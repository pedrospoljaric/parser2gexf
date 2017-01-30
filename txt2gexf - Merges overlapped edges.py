import Tkinter as tk
from Tkinter import *
from tkFileDialog import *
from gexf import Gexf

root = tk.Tk()
root.withdraw()

eventosDesejados = ['PajeCreateContainer', 'PajeDestroyContainer', 'PajeStartLink', 'PajeEndLink']

gexf = Gexf("Pedro e David", "Dynamic graph")
graph = gexf.addGraph("directed", "dynamic", "Graph")

def setCodes():

	numEv = 0
	for line in range(len(lines)):
	
		if 'ID:' in lines[line]:
			return numEv

		for evento in eventosDesejados:

			if evento in lines[line]:
			
				numEv += 1
				div = lines[line].split(' ')
				div2 = div[-1].split('\n')
				dicEventos[evento] = div2[0]

def formatTime(time):

	if 'e+' in time:
		calctime = time.split('e+')
		time = str(float(calctime[0]) * pow(10, int(calctime[1])))
		  
	elif 'e-' in time:
		calctime = time.split('e-')
		time = str(float(calctime[0]) * pow(10, int(calctime[1]) * (-1)))
	
	return time

print("Select .txt file to convert:")
file_path = askopenfilename()
filetxt = open(file_path, 'r')
lines = filetxt.readlines()
filetxt.close()
print 'Selected file: ', file_path, '\n'

nodeId = 0
edgeId = 0

list7 = []
list8 = []
list42 = []
list43 = []

print 'Listing wanted events...'
dicEventos = {}
numEventos = setCodes()
print numEventos, 'events listed.\n'

totalEvents = 0

print 'Collecting events info...'
for lineStart in range(len(lines)):
	
	if lines[lineStart].startswith('ID: ' + dicEventos['PajeCreateContainer'] + ':') and ('CT_Thread' in lines[lineStart]):
		list7.append(lines[lineStart])
		totalEvents += 1
		
	elif lines[lineStart].startswith('ID: ' + dicEventos['PajeDestroyContainer'] + ':') and 'CT_Thread' in lines[lineStart]:
		list8.append(lines[lineStart])
		totalEvents += 1
		
	elif lines[lineStart].startswith('ID: ' + dicEventos['PajeStartLink'] + ':'):
		list42.append(lines[lineStart])
		totalEvents += 1
		
	elif lines[lineStart].startswith('ID: ' + dicEventos['PajeEndLink'] + ':'):	
		list43.append(lines[lineStart])
		totalEvents += 1
		
print 'Info from', totalEvents, 'events collected.\n'

totalNodes = 0

print 'Generating and iserting nodes into graph...'
for lineCreate in list7:
	
	lineC = lineCreate.split(': ')
	done = 0
	for lineDestroy in list8:

		lineD = lineDestroy.split(': ')
		
		if (str(lineC[11]) == str(lineD[5])):
			id = (lineC[9].split('#'))[-1].replace('"', '')
			graph.addNode(str(id), str(lineC[9]).replace('"', ''), str(formatTime(lineC[3])), str(formatTime(lineD[3])))
			done = 1
			list8.remove(lineDestroy)
			totalNodes += 1
			break
	
	if done == 0:
		id = (lineC[9].split('#'))[-1].replace('"', '')
		graph.addNode(str(id), str(lineC[9]).replace('"', ''), str(formatTime(lineC[3])))
		totalNodes += 1
			
print 'Done.', totalNodes, 'nodes created.\n'

intervalErrors = 0
totalP2P = 0
totalColl = 0

lsLabel = []
lsWeight = []
lsStart = []
lsEnd = []

print 'Generating edges...'
for lineStart in list42:
	
	lineS = lineStart.split(': ')
	
	source = ((lineS[11].split(', '))[0].split('='))[1].replace('"', '')
	target = ((lineS[11].split(', '))[1].split('='))[1].replace('"', '')
	label = str(source) + '_' + str(target)
	timeS = formatTime(lineS[3])
	linkType = lineS[5]
	
	for lineEnd in list43:
	
		if linkType in lineEnd:
		
			lineE = lineEnd.split(': ')
			
			if (str(lineS[13]) == str(lineE[13])):
				
				timeE = formatTime(lineE[3])
				
				if linkType == '"L_MPI_P2P"':
					weight = ((lineS[11].split(', '))[2].split('='))[1].replace('"', '')
					totalP2P += 1
				else:
					weight = '1'
					totalColl += 1
				
				if (float(timeS) > float(timeE)):
					if (intervalErrors == 0): print '\nInterval errors in links:'
					print lineStart, lineEnd
					intervalErrors += 1
					
					timeAux = timeE
					timeE = timeS
					timeS = timeAux
				
				lsLabel.append(label)
				lsWeight.append(weight)
				lsStart.append(float(timeS))
				lsEnd.append(float(timeE))
				
				list43.remove(lineEnd)
				edgeId += 1
				
				break
				
if (intervalErrors > 0): print intervalErrors, 'interval error(s) found. (Start and End times switched)\n'

print 'Checking  generated edges...'

lsRemove = set([])
for i in range(0, len(lsLabel)):

	for j in range(0, len(lsLabel)):
	
		if (i != j and lsLabel[j] == lsLabel[i] and j not in lsRemove and i not in lsRemove):
			
			if (float(lsStart[i]) == float(lsStart[j])):
				if (float(lsEnd[i]) == float(lsEnd[j])):
					lsWeight[i] = float(lsWeight[i]) + float(lsWeight[j])
					lsRemove.add(j)				
				elif (float(lsEnd[i]) > float(lsEnd[j])):
					lsWeight[i] = float(lsWeight[i]) + float(lsWeight[j])
					lsRemove.add(j)				
				elif (float(lsEnd[i]) < float(lsEnd[j])):
					lsEnd[i] = lsEnd[j]
					lsWeight[i] = float(lsWeight[i]) + float(lsWeight[j])
					lsRemove.add(j)
				
			elif (float(lsStart[i]) > float(lsStart[j])):
				if (float(lsStart[i]) <= float(lsEnd[j])):
					if (float(lsEnd[i]) == float(lsEnd[j])):
						lsStart[i] = lsStart[j]
						lsWeight[i] = float(lsWeight[i]) + float(lsWeight[j])
						lsRemove.add(j)
					#elif (float(lsEnd[i]) > float(lsEnd[j])):				
					elif (float(lsEnd[i]) < float(lsEnd[j])):
						lsStart[i] = lsStart[j]
						lsEnd[i] = lsEnd[j]
						lsWeight[i] = float(lsWeight[i]) + float(lsWeight[j])
						lsRemove.add(j)
				
			elif (float(lsStart[i]) < float(lsStart[j])):
				if (float(lsEnd[i]) >= float(lsStart[j])):
					if (float(lsEnd[i]) == float(lsEnd[j])):
						lsWeight[i] = float(lsWeight[i]) + float(lsWeight[j])
						lsRemove.add(j)				
					elif (float(lsEnd[i]) > float(lsEnd[j])):
						lsWeight[i] = float(lsWeight[i]) + float(lsWeight[j])
						lsRemove.add(j)				
					elif (float(lsEnd[i]) < float(lsEnd[j])):
						lsEnd[i] = lsEnd[j]
						lsWeight[i] = float(lsWeight[i]) + float(lsWeight[j])
						lsRemove.add(j)

print 'Inserting edges into graph...'
for i in range(0, len(lsLabel)):

	if i not in lsRemove:
		source = (lsLabel[i].split('_'))[0]
		target = (lsLabel[i].split('_'))[1]
		graph.addEdge(str(i), str(source), str(target), float(lsWeight[i]), str(lsStart[i]), str(lsEnd[i]), lsLabel[i])

print 'Done.', len(lsLabel) - len(lsRemove), 'edges created.\n'
print 'P2P links:', totalP2P
print 'Coll links:', totalColl, '\n'

filepath = file_path.split('.')
output_file = open(filepath[0] + "_gexf.gexf", "w")
gexf.write(output_file)
