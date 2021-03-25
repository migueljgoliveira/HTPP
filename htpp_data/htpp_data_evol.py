# -----------------------------------------------------------------------------
# ------------------------------------------------------------- IMPORT PACKAGES
from odbAccess import *
from abaqusConstants import *
import numpy as np
import sys
from textRepr import prettyPrint

# ---------------------------------------------------------------- EVOL OPTIONS
def htpp_data_evol_option(odb,option):
	step = '\n'.join(s for s in option if 'step=' in s).replace(",", "").replace("\n", "")[6:-1].strip().split(';')
	step = [int(s) for s in step]
	frame = '\n'.join(s for s in option if 'frame=' in s).replace(",", "").replace("\n", "")[7:-1].strip().split(';')
	frame = [int(i) for i in frame]
	elem_set = '\n'.join(s for s in option if 'elemSet=' in s).replace(",", "").replace("\n", "")[9:-1].split(';')

	return step,frame,elem_set

# -----------------------------------------------------------------------------
# ------------------------------------------------------------------------ EVOL
# -----------------------------------------------------------------------------
def htpp_data_evol(odb,ioi,option,section,odb_name):
	step,frame,elem_set = htpp_data_evol_option(odb,option)

	step_names = odb.steps.keys()

	soi = ioi.elementSets[' ALL ELEMENTS']
	pos = INTEGRATION_POINT

	name = 'EVOL'
	dir = 'htpp_output/' + odb_name + '/'

	secs = 1
	if len(section) > 0:
		secs = len(section)

	# -------------------------------------------------------------- WRITE DATA

	pos = CENTROID
	for l in step:
		sT = odb.steps[step_names[l-1]]
		for set in elem_set:
			if set != '':
				soi = ioi.elementSets[set]
				for f in frame:
					fRa = sT.frames[f]
					odb_data = fRa.fieldOutputs[name]
					
					if len(section) == 0:
						vals = odb_data.getSubset(region=soi).values
					else:
						vals = odb_data.getSubset(region=soi, sectionPoint=section[-1]).values
					strings = ['evol',set.lower(),'s'+str(l),'f'+str(f)]
					fname = dir+'_'.join(strings)+'.dat'
					with open(fname,'w') as f:
						for i in range(len(vals)):
							f.write('%f\n' %vals[i].data)
# ------------------------------------------------------------------------------
