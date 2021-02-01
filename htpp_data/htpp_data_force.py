# ------------------------------------------------------------------------------
# -------------------------------------------------------------- IMPORT PACKAGES
from odbAccess import *
from abaqusConstants import *
import numpy as np
from textRepr import prettyPrint
import os

# ---------------------------------------------------------------- FORCE OPTIONS
def htpp_data_force_option(odb,option):
	step = '\n'.join(s for s in option if 'step=' in s).replace(",", "").replace("\n", "")[6:-1].strip().split(';')
	step = [int(s) for s in step]
	node_set = '\n'.join(s for s in option if 'nodeSet=' in s).replace(",", "").replace("\n", "")[9:-1].split(';')
	direc = '\n'.join(s for s in option if 'direction=' in s).replace(",", "").replace("\n", "")[11:-1].strip().split(';')
	direc = [int(i) for i in direc]

	return step,node_set,direc

# -------------------------------------------------------------------- FORCE AUX
def htpp_data_force_aux(odb_data,soi,direc):
	odb_data_RF = odb_data.fieldOutputs['RF']
	odb_data_U = odb_data.fieldOutputs['U']
	vals_RF = odb_data_RF.getSubset(region=soi,position=NODAL).values
	vals_U = odb_data_U.getSubset(region=soi,position=NODAL).values

	force = 0.0
	for i in range(len(vals_RF)):
		force += vals_RF[i].data[direc-1]

	disp = vals_U[-1].data[direc-1]

	return force,disp

# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------ FORCE
# ------------------------------------------------------------------------------
def htpp_data_force(odb,ioi,option,section,odb_name):
	step,node_set,direc = htpp_data_force_option(odb,option)

	step_names = odb.steps.keys()

	dir = 'htpp_output/' + odb_name + '/'

	for l in step:
		sT = odb.steps[step_names[l-1]]
		for j in range(len(node_set)):
			if node_set[j] != '':
				soi = ioi.nodeSets[node_set[j]]
				strings = ['force',node_set[j].lower(),'s'+str(l), 'd'+str(direc[j])]
				fname = '_'.join(strings)
				with open(dir + fname + '.dat','w') as file:
					file.write('Disp , Force\n')
					for f in range(len(sT.frames)):
						odb_data = sT.frames[f]
						force,disp = htpp_data_force_aux(odb_data,soi,direc[j])
						file.write('%f , %f\n' %(disp,force))
# ------------------------------------------------------------------------------
