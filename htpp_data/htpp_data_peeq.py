# ------------------------------------------------------------------------------
# -------------------------------------------------------------- IMPORT PACKAGES
from odbAccess import *
from abaqusConstants import *
import numpy as np
import sys
from textRepr import prettyPrint

# ----------------------------------------------------------------- PEEQ OPTIONS
def htpp_data_peeq_option(odb,option):
	step = '\n'.join(s for s in option if 'step=' in s).replace(",", "").replace("\n", "")[6:-1].strip().split(';')
	step = [int(s) for s in step]
	frame = '\n'.join(s for s in option if 'frame=' in s).replace(",", "").replace("\n", "")[7:-1].strip().split(';')
	frame = [int(i) for i in frame]
	elem_set = '\n'.join(s for s in option if 'elemSet=' in s).replace(",", "").replace("\n", "")[9:-1].split(';')

	return step,frame,elem_set

# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------- PEEQ
# ------------------------------------------------------------------------------
def htpp_data_peeq(odb,ioi,option,section,odb_name):
	step,frame,elem_set = htpp_data_peeq_option(odb,option)

	step_names = odb.steps.keys()

	soi = ioi.elementSets[' ALL ELEMENTS']
	pos = INTEGRATION_POINT

	name = 'PEEQ'
	desc = 'Equivalent plastic strain at integration points'
	dir = 'htpp_output/' + odb_name + '/'

	secs = 1
	if len(section) > 0:
		secs = len(section)

	for l in step:
		sT = odb.steps[step_names[l-1]]
		for k in range(len(sT.frames)):
			fRa = sT.frames[k]
			field_keys = fRa.fieldOutputs.keys()
			if name not in field_keys:
				odb_data = fRa.fieldOutputs['SDV1']
				new_field = fRa.FieldOutput(name=name,description=desc, type=SCALAR)
				for j in range(secs):
					if len(section) == 0:
						vals = odb_data.getSubset(region=soi,position=pos).values
					else:
						sp = section[j]
						vals = odb_data.getSubset(region=soi,position=pos, sectionPoint=sp).values
					if len(vals) > 0:
						with open(dir + 'PEEQ.dat','w') as file:
							for i in range(len(vals)):
								file.write('%f\n' %vals[i].data)

						with open(dir + 'PEEQ.dat','r') as f:
						    peeq = [tuple(map(float, i.split(' '))) for i in f]

						if len(section) == 0:
							new_field.addData(position=pos,set=soi,data=peeq)
						else:
							new_field.addData(position=pos,set=soi, sectionPoint=sp, data=peeq)
						os.remove(dir+'PEEQ.dat')
					else:
						pass
	odb.save()

	# --------------------------------------------------------------- WRITE DATA

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
						vals = odb_data.getSubset(region=soi,position=pos).values
					else:
						vals = odb_data.getSubset(region=soi,position=pos, sectionPoint=section[-1]).values
					strings = ['peeq',set.lower(),'s'+str(l),'f'+str(f)]
					fname = dir+'_'.join(strings)+'.dat'
					with open(fname,'w') as f:
						for i in range(len(vals)):
							f.write('%f\n' %vals[i].data)
# ------------------------------------------------------------------------------
