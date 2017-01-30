import Tkinter as tk
from Tkinter import *
from tkFileDialog import *
from collections import OrderedDict
from gexf import Gexf

root = tk.Tk()
root.withdraw()

def setCodes():

	numEv = 0
	for line in range(len(lines_txt)):
	
		if 'ID:' in lines_txt[line]:
			return numEv

		for evento in eventosDesejados:

			if evento in lines_txt[line]:
			
				numEv += 1
				div = lines_txt[line].split(' ')
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

print("Select .trace file to convert:\n")
file_path_trace = askopenfilename()
file_trace = open(file_path_trace, 'r')
lines_trace = file_trace.readlines()
file_trace.close()
filepathtrace = file_path_trace.split('.')
output_file_txt = open(filepathtrace[0] + "_txt.txt", "w")

print 'Generating .txt file...'

dicEvents = {}
for i in range(len(lines_trace)):

	if ('%EventDef' in lines_trace[i]):
	
		ln = lines_trace[i].split(' ')
		id = ln[2].split('\n')
		id = id[0]
		dicEv = OrderedDict()
		
		output_file_txt.write(ln[1] + ' ' + ln[2])
			
		i += 1
		while (lines_trace[i].startswith('%EndEventDef') == False):
			
			ln = lines_trace[i].split(' ')
			typ = ln[2].split('\n')
			typ = typ[0]
			dicEv[str(ln[1])] = typ
			i += 1
			
		dicEvents[str(id)] = dicEv

for i in range(len(lines_trace)):

	if (lines_trace[i].startswith('%') == False):
	
		ln = lines_trace[i].split(' ')
		fileLine = ""
		
		j = 0
		fileLine += 'ID: ' + ln[j] + ': '
		j += 1
		
		for item in dicEvents[str(ln[0])]:		
			
			it = item.upper() + ':'
			
			if str(ln[j])[0] == '"':			
				while True:
					it += ' ' + str(ln[j])
					j += 1
					if (len(str(ln[j-1])) > 0):
						if (str(ln[j-1])[-1] == '"' or str(ln[j-1]).endswith('\n')): break
					
			else:
				it += ' ' + str(ln[j])
				j += 1
			
			fileLine += (it.split('\n'))[0] + ': '
			
		fileLine += '\n'
		output_file_txt.write(fileLine)

print 'File generated successfully.'
print 'Path: ', filepathtrace[0] + "_txt.txt\n"
output_file_txt.close()

eventosDesejados = ['PajeCreateContainer', 'PajeDestroyContainer', 'PajeStartLink', 'PajeEndLink']

gexf = Gexf("Pedro e David", "Dynamic graph")
graph = gexf.addGraph("directed", "dynamic", "Graph")

filetxt = open(filepathtrace[0] + "_txt.txt", "r")
lines_txt = filetxt.readlines()
filetxt.close()

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
for lineStart in range(len(lines_txt)):
	
	if lines_txt[lineStart].startswith('ID: ' + dicEventos['PajeCreateContainer'] + ':') and ('CT_Thread' in lines_txt[lineStart]):
		list7.append(lines_txt[lineStart])
		totalEvents += 1
		
	elif lines_txt[lineStart].startswith('ID: ' + dicEventos['PajeDestroyContainer'] + ':') and 'CT_Thread' in lines_txt[lineStart]:
		list8.append(lines_txt[lineStart])
		totalEvents += 1
		
	elif lines_txt[lineStart].startswith('ID: ' + dicEventos['PajeStartLink'] + ':'):
		list42.append(lines_txt[lineStart])
		totalEvents += 1
		
	elif lines_txt[lineStart].startswith('ID: ' + dicEventos['PajeEndLink'] + ':'):	
		list43.append(lines_txt[lineStart])
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

output_file_gexf = open(filepathtrace[0] + "_gexf.gexf", "w")
gexf.write(output_file_gexf)
