# -----------------------------------------------------------------------------
# ------------------------------------------------------------- IMPORT PACKAGES
from odbAccess import *
from abaqusConstants import *
import numpy as np
import os
from textRepr import prettyPrint

# -------------------------------------------------------------- STRAIN OPTIONS
def htpp_data_strain_option(odb,option):
	step = '\n'.join(s for s in option if 'step=' in s).replace(",", "").replace("\n", "")[6:-1].strip().split(';')
	step = [int(s) for s in step]
	frame = '\n'.join(s for s in option if 'frame=' in s).replace(",", "").replace("\n", "")[7:-1].strip().split(';')
	frame = [int(i) for i in frame]
	elem_set = '\n'.join(s for s in option if 'elemSet=' in s).replace(",", "").replace("\n", "")[9:-1].split(';')

	return step,frame,elem_set

# ------------------------------------------------------------------ STRAIN AUX
def htpp_data_strain_aux(vals):
	E1 = np.empty(len(vals))
	E2 = np.empty(len(vals))
	for i in range(len(vals)):
		dim = len(vals[i].data)
		if dim <= 4:
			E1[i] = vals[i].maxInPlanePrincipal
			E2[i] = vals[i].minInPlanePrincipal
		elif dim > 4:
			strain = np.zeros((3,3))
			strain[0,0] = vals[i].data[0]
			strain[1,1] = vals[i].data[1]
			strain[2,2] = vals[i].data[2]
			strain[0,1] = vals[i].data[3]/2.0
			strain[1,0] = strain[0,1]
			strain[0,2] = vals[i].data[4]/2.0
			strain[2,0] = strain[0,2]
			strain[1,2] = vals[i].data[5]/2.0
			strain[2,1] = strain[1,2]
			w, v = np.linalg.eig(strain)
			E1[i] = max(w[0:2])
			E2[i] = min(w[0:2])

	return E1,E2

# -----------------------------------------------------------------------------
# ---------------------------------------------------------------------- STRAIN
# -----------------------------------------------------------------------------
def htpp_data_strain(odb,ioi,option,section,odb_name):
	step,frame,elem_set = htpp_data_strain_option(odb,option)

	step_names = odb.steps.keys()

	soi = ioi.elementSets[' ALL ELEMENTS']
	pos = INTEGRATION_POINT

	name = 'STRAIN PATH'
	desc = 'Principal strain ratio'
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
				odb_data = fRa.fieldOutputs['LE']
				new_field = fRa.FieldOutput(name=name,description=desc, type=SCALAR)
				for j in range(secs):
					if len(section) == 0:
						vals = odb_data.getSubset(region=soi, position=pos).values
					else:
						sp = section[j]
						vals = odb_data.getSubset(region=soi,position=pos, sectionPoint=sp).values
					if len(vals) > 0:
						with open(dir + 'STRAINPATH.dat','w') as file:
							E1,E2 = htpp_data_strain_aux(vals)
							ratio = 0.0
							for i in range(len(vals)):
								if k != 0:
									ratio = E2[i]/E1[i]
								file.write('%f\n' %ratio)

						with open(dir + 'STRAINPATH.dat','r') as f:
						    path = [tuple(map(float, i.split(' '))) for i in f]

						if len(section) == 0:
							new_field.addData(position=pos,set=soi,data=path)
						else:
							new_field.addData(position=pos,set=soi, sectionPoint=sp, data=path)
						os.remove(dir+'STRAINPATH.dat')
					else:
						pass
	odb.save()

	# -------------------------------------------------------------- WRITE DATA
	pos = CENTROID
	for l in step:
		sT = odb.steps[step_names[l-1]]
		for set in elem_set:
			if set != '':
				soi = ioi.elementSets[set]
				for f in frame:
					fRa = sT.frames[f]
					odb_data = fRa.fieldOutputs['LE']
					if len(section) == 0:
						vals = odb_data.getSubset(region=soi, position=pos).values
					else:
						vals = odb_data.getSubset(region=soi,position=pos, sectionPoint=section[-1]).values
					E1,E2 = htpp_data_strain_aux(vals)
					strings = ['strain',set.lower(),'s'+str(l),'f'+str(f)]
					fname = '_'.join(strings)
					with open(dir + fname + '.dat','w') as file:
						file.write('E1 , E2\n')
						for i in range(len(vals)):
							file.write('%f , %f \n' %(E1[i],E2[i]))

# -----------------------------------------------------------------------------
