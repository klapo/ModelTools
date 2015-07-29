#! /usr/bin/env python
import sys
import os

# Example call
# python run_sntherm.py MeltSens

#####################
## Read MasterList ##
#####################
# Open the masterlist
FID = open("MasterList.txt","read")
# Read the list
str1 = FID.read()

experiment_name = sys.argv[1];                          # Folder appending for this experiment
input_dir = "INPUT." + experiment_name
layer_dir = "LAYER." + experiment_name
output_dir = "OUTPUT." + experiment_name

sites = []
scenarios = []
for masterlist in str1.splitlines():
	s, sc = masterlist.strip().split("\t")              # Site and scenario name
	sites.append(s)
	scenarios.append(sc)

os.chdir(output_dir)
if not os.path.isdir('.original'):
	os.mkdir('.original')
os.chdir('../')

#####################
## Execute SNTHERM ##
#####################

for s, sc in zip(sites, scenarios):

	print(s+"."+sc)

	# sntherm file names
	new_filename = s + "." + sc + ".FILENAME"			# filename
	new_in = s + "." + sc + ".in"						# *.in
	layer_in = s + ".in"								# layer.in

	# System commands - unpack input folder
	os.system("cp " + input_dir + "/" + new_filename + " FILENAME")		# Copy the new filename to FILENAME
	os.system("mv " + input_dir + "/" + new_in + " ./")					# Move the met.in file into the sntherm directory
	os.system("mv " + layer_dir + "/" + layer_in + " ./")				# Move the layer.in file into the sntherm directory 

	# Execute sntherm
	os.system("./sntherm")

	# Output names
	MFout = s + "." + sc + ".MetFlux.out"
	LFout = s + "." + sc + ".out"
	flux_out = s + "." + sc + ".Flux.out"
	lay_out = s + "." + sc + ".Layer.out"
	ts_out = s + "." + sc + ".Surface.out"

	#####################
	## REFORMAT OUTPUT ##
	#####################

	### METFLUX OUTPUT ###

	# Read the indicated SNTHERM file
	f = open(MFout,'r')
	MFdata = []
	for line in f:
		line = line.strip()
		# Ignore header lines
		if line.find('change') >= 0 or line.find('date-time') >= 0 or line.find('snowpack') >= 0  or line.find('(w/m**2)') >= 0:
			continue
		# Ignore empty lines and read the line with data
		elif line:
			MFdata.append(line)
	f.close

	# Re-write formatted output
	fMFout = open(flux_out,'w')
	for i in MFdata:
		fMFout.write(i+'\n')

	### LAYER OUTPUT ###

	# Read the layer file
	f = open(LFout,'r')

	# Initialize 
	lay_data = []
	ts_data = []
	numlayers = 0
	for line in f:
		line = line.strip()
		# Fill in NaNs 
		if line.find('*******'):
			line = line.replace('*******','NaN     ')

		# Ignore header lines
		if line.find('(kg/m^3)') >= 0 or line.find('date-time') >= 0 or line.find('(w/m**2)') >= 0:
			continue
		# Ignore empty lines and read the line with data
		elif line:
			# Number of elements in the line
			numel = len(line.split(','))
			# layer output every 6 hours (some longer time step)
			if numel == 14:
				lay_data.append(line)
			# Time series output between layer outputs at a higher temporal frequency
			elif numel == 9:
				ts_data.append(line)
				numlayers = max(numlayers,float(line.split(',')[7]))
	f.close

	# Write formatted output
	flay_out = open(lay_out,'w')
	fts_out = open(ts_out,'w')
	flay_out.write(str(numlayers)+'\n')
	for i in lay_data:
		flay_out.write(i+'\n')
	flay_out.close

	for j in ts_data:
		fts_out.write(j+'\n')
	fts_out.close

	# Put things away 
	os.system("mv " + new_in + " " + input_dir)				# Put met.in back
	os.system("mv " + layer_in + " " + layer_dir) 			# Put layer.in back
	os.system("rm *dum2.out")								# Remove the dummy file
#	os.system("mv *.out " + output_dir)						# Temp line - move the original output files back

	# Clean-up output folder
	os.system("mv " + MFout + " "+output_dir+"/.original")
	os.system("mv " + LFout + " "+output_dir+"/.original")
	os.system("mv " + lay_out + " " + output_dir)
	os.system("mv " + ts_out + " " + output_dir)
	os.system("mv " + flux_out + " " + output_dir)
