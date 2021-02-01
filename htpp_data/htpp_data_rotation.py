# ------------------------------------------------------------------------------
# -------------------------------------------------------------- IMPORT PACKAGES
from odbAccess import *
from abaqusConstants import *
import numpy as np
import math
from textRepr import prettyPrint

# ------------------------------------------------------------- ROTATION OPTIONS
def htpp_data_rotation_option(odb,option):
	step = '\n'.join(s for s in option if 'step=' in s).replace(",", "").replace("\n", "")[6:-1].strip().split(';')
	step = [int(s) for s in step]
	frame = '\n'.join(s for s in option if 'frame=' in s).replace(",", "").replace("\n", "")[7:-1].strip().split(';')
	frame = [int(i) for i in frame]
	elem_set = '\n'.join(s for s in option if 'elemSet=' in s).replace(",", "").replace("\n", "")[9:-1].split(';')

	return step,frame,elem_set

# ----------------------------------------------------------------- ROTATION AUX
def htpp_data_rotation_aux(vals,i):
	dim = len(vals[i].data)
	if dim <= 4:
		S11 = vals[i].data[0]
		S22 = vals[i].data[1]
		S33 = 0.0
		S12 = vals[i].data[3]
		S13 = 0.0
		S23 = 0.0
	elif dim > 4:
		S11 = vals[i].data[0]
		S22 = vals[i].data[1]
		S33 = vals[i].data[2]
		S12 = vals[i].data[3]
		S13 = vals[i].data[4]
		S23 = vals[i].data[5]

	if S11 - S22 == 0.0:
		ang = 45.0
	else:
		S = [[S11,S12,S13],[S12,S22,S23],[S13,S23,S33]]
		w, v = np.linalg.eig(S)
		S1 = max(w[0:2])
		S2 = min(w[0:2])
		PMC = ((S11-S22)/abs(S11-S22))*((abs(S1)-abs(S2))/abs(abs(S1)-abs(S2)))
		beta = 0.5*math.atan(2.0*S12/(S11-S22))*180.0/math.pi
		gamma = 45.0*(1.0-PMC)+PMC*abs(beta)

	return gamma

# ------------------------------------------------------------------------------
# --------------------------------------------------------------------- ROTATION
# ------------------------------------------------------------------------------
def htpp_data_rotation(odb,ioi,option,section,odb_name):
	step,frame,elem_set = htpp_data_rotation_option(odb,option)

	step_names = odb.steps.keys()

	soi = ioi.elementSets[' ALL ELEMENTS']
	pos = INTEGRATION_POINT

	name = 'ROTATION ANGLE'
	desc = 'Rotation angle between dominant principal stress base and material frame'
	dir = 'htpp_output/' + odb_name + '/'

	secs = 1
	if len(section) > 0:
		secs = len(section)
	for l in step:
		sT = odb.steps[step_names[l-1]]
		for k in range(len(sT.frames)):
			field_keys = sT.frames[k].fieldOutputs.keys()
			if name not in field_keys:
				fRa = sT.frames[k]
				odb_data = fRa.fieldOutputs['S']
				new_field = fRa.FieldOutput(name=name,description=desc,type=SCALAR)
				for j in range(secs):
					if len(section) == 0:
						vals = odb_data.getSubset(region=soi, position=pos).values
					else:
						sp = section[j]
						vals = odb_data.getSubset(region=soi,position=pos, sectionPoint=sp).values
					if len(vals) > 0:
						ang = 0.0
						with open(dir + 'ROTATION.dat','w') as file:
							for i in range(len(vals)):
								if k != 0:
									ang = htpp_data_rotation_aux(vals,i)
								file.write('%f\n' %ang)

						with open(dir + 'ROTATION.dat','r') as f:
						    angle = [tuple(map(float, i.split(' '))) for i in f]

						if len(section) == 0:
							new_field.addData(position=pos,set=soi,data=angle)
						else:
							new_field.addData(position=pos,set=soi, sectionPoint=sp, data=angle)
						os.remove(dir+'ROTATION.dat')
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
						vals = odb_data.getSubset(region=soi, position=pos).values
					else:
						vals = odb_data.getSubset(region=soi,position=pos, sectionPoint=section[-1]).values
					strings = ['rotation',set.lower(),'s'+str(l),'f'+str(f)]
					fname = dir + '_'.join(strings) + '.dat'
					with open(fname,'w') as f:
						for i in range(len(vals)):
							f.write('%f\n' %vals[i].data)

# ------------------------------------------------------------------------------
