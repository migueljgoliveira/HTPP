# ------------------------------------------------------------------------------
# -------------------------------------------------------------- IMPORT PACKAGES
from odbAccess import *
from abaqusConstants import *
import numpy as np
import math
from textRepr import prettyPrint

# ---------------------------------------------------------- TRIAXIALITY OPTIONS
def htpp_data_triaxiality_lode_option(odb,option):
	step = '\n'.join(s for s in option if 'step=' in s).replace(",", "").replace("\n", "")[6:-1].strip().split(';')
	step = [int(s) for s in step]
	frame = '\n'.join(s for s in option if 'frame=' in s).replace(",", "").replace("\n", "")[7:-1].strip().split(';')
	frame = [int(i) for i in frame]
	elem_set = '\n'.join(s for s in option if 'elemSet=' in s).replace(",", "").replace("\n", "")[9:-1].split(';')

	return step,frame,elem_set

# ------------------------------------------------------------------------------
# --------------------------------------------------- TRIAXIALITY AND LODE ANGLE
# ------------------------------------------------------------------------------
def htpp_data_triaxiality_lode(odb,ioi,option,section,odb_name):

	step,frame,elem_set = htpp_data_triaxiality_lode_option(odb,option)

	step_names = odb.steps.keys()

	soi = ioi.elementSets[' ALL ELEMENTS']
	pos = INTEGRATION_POINT

	# -------------------------------------------------------------- TRIAXIALITY
	name1 = 'STRESS TRIAXIALITY'
	desc = 'Stress triaxiality'
	dir = 'htpp_output/' + odb_name + '/'

	secs = 1
	if len(section) > 0:
		secs = len(section)

	for l in step:
		sT = odb.steps[step_names[l-1]]
		for k in range(len(sT.frames)):
			fRa = sT.frames[k]
			field_keys = sT.frames[k].fieldOutputs.keys()
			if name1 not in field_keys:
				odb_data = fRa.fieldOutputs['S']
				new_field = fRa.FieldOutput(name=name1,description=desc,type=SCALAR)
				for j in range(secs):
					if len(section) == 0:
						vals = odb_data.getSubset(region=soi, position=pos).values
					else:
						sp = section[j]
						vals = odb_data.getSubset(region=soi,position=pos, sectionPoint=sp).values
					if len(vals) > 0:
						tri = 0.0
						with open(dir + 'TRIAXIALITY.dat','w') as file:
							for i in range(len(vals)):
								if k != 0:
									tri = -vals[i].press/vals[i].mises
								file.write('%f\n' %tri)

						with open(dir + 'TRIAXIALITY.dat','r') as f:
						    tri = [tuple(map(float, i.split(' '))) for i in f]

						if len(section) == 0:
							new_field.addData(position=pos,set=soi,data=tri)
						else:
							new_field.addData(position=pos,set=soi, sectionPoint=sp, data=tri)
						os.remove(dir+'TRIAXIALITY.dat')
					else:
						pass
	odb.save()

	# --------------------------------------------------------- NORM. LODE ANGLE
	name2 = 'NORM. LODE ANGLE'
	desc = 'Normalized Lode angle parameter'
	for l in step:
		sT = odb.steps[step_names[l-1]]
		for k in range(len(sT.frames)):
			fRa = sT.frames[k]
			field_keys = fRa.fieldOutputs.keys()
			if name2 not in field_keys:
				odb_data = fRa.fieldOutputs['S']
				new_field = fRa.FieldOutput(name=name2,description=desc,type=SCALAR)
				for j in range(secs):
					if len(section) == 0:
						vals = odb_data.getSubset(region=soi, position=pos).values
					else:
						sp = section[j]
						vals = odb_data.getSubset(region=soi,position=pos, sectionPoint=sp).values
					if len(vals) > 0:
						lodeangnorm = 0.0
						with open(dir + 'NORMLODEANGLE.dat','w') as file:
							for i in range(len(vals)):
								if k != 0:
									lodeparam = (vals[i].inv3/vals[i].mises)**3
									if lodeparam > 1.0:
										lodeparam = 1.0
									elif lodeparam < -1.0:
										lodeparam = -1.0
									lodeangnorm = 1.0-(2.0/math.pi)*math.acos(lodeparam)
								file.write('%f\n' %lodeangnorm)

						with open(dir + 'NORMLODEANGLE.dat','r') as f:
							lodeangnorm=[tuple(map(float,i.split(' '))) for i in f]

						if len(section) == 0:
							new_field.addData(position=pos,set=soi, data=lodeangnorm)
						else:
							new_field.addData(position=pos,set=soi, sectionPoint=sp, data=lodeangnorm)
						os.remove(dir+'NORMLODEANGLE.dat')
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
					odb_data1 = fRa.fieldOutputs[name1]
					odb_data2 = fRa.fieldOutputs[name2]
					if len(section) == 0:
						vals1 = odb_data1.getSubset(region=soi, position=pos).values
						vals2 = odb_data2.getSubset(region=soi, position=pos).values
					else:
						vals1 = odb_data1.getSubset(region=soi,position=pos, sectionPoint=section[-1]).values
						vals2 = odb_data2.getSubset(region=soi,position=pos, sectionPoint=section[-1]).values
					strings = ['triax_lode',set.lower(),'s'+str(l),'f'+str(f)]
					fname = dir + '_'.join(strings) + '.dat'
					with open(fname,'w') as file:
						file.write('triax , lode\n')
						for i in range(len(vals1)):
							file.write('%f , %f\n' %(vals1[i].data,vals2[i].data))
# ------------------------------------------------------------------------------
