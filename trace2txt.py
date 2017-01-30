import Tkinter as tk
from Tkinter import *
from tkFileDialog import *
from collections import OrderedDict

root = tk.Tk()
root.withdraw()

print("Select .trace file to convert:\n")
file_path = askopenfilename()
filetrc = open(file_path, 'r')
lines = filetrc.readlines()
filetrc.close()
filepath = file_path.split('.')
output_file = open(filepath[0] + "_txt.txt", "w")

print 'Generating .txt file...'

dicEvents = {}
for i in range(len(lines)):

	if ('%EventDef' in lines[i]):
	
		ln = lines[i].split(' ')
		id = ln[2].split('\n')
		id = id[0]
		dicEv = OrderedDict()
		
		output_file.write(ln[1] + ' ' + ln[2])
			
		i += 1
		while (lines[i].startswith('%EndEventDef') == False):
			
			ln = lines[i].split(' ')
			typ = ln[2].split('\n')
			typ = typ[0]
			dicEv[str(ln[1])] = typ
			i += 1
			
		dicEvents[str(id)] = dicEv

for i in range(len(lines)):

	if (lines[i].startswith('%') == False):
	
		ln = lines[i].split(' ')
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
		output_file.write(fileLine)

print 'File generated successfully.'
print 'Path: ', filepath[0] + "_txt.txt"