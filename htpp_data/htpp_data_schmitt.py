# ------------------------------------------------------------------------------
# -------------------------------------------------------------- IMPORT PACKAGES
from odbAccess import *
from abaqusConstants import *
import numpy as np
from numpy.linalg import norm
from textRepr import prettyPrint

# ------------------------------------------------------- SCHMITT FACTOR OPTIONS
def htpp_data_schmitt_option(odb,option):
	step = '\n'.join(s for s in option if 'step=' in s).replace(",", "").replace("\n", "")[6:-1].strip().split(';')
	step = [int(s) for s in step]
	elem_set = '\n'.join(s for s in option if 'elemSet=' in s).replace(",", "").replace("\n", "")[9:-1].split(';')

	return step,elem_set

# ----------------------------------------------------------- SCHMITT FACTOR AUX
def htpp_data_schmitt_aux(vals):
	dim = len(vals.data)
	if dim <= 4:
		strain = np.zeros((2,2))
		strain[0,0] = vals.data[0]
		strain[1,1] = vals.data[1]
		strain[0,1] = vals.data[2]/2.0
		strain[1,0] = strain[0,1]
	elif dim > 4:
		strain = np.zeros((3,3))
		strain[0,0] = vals.data[0]
		strain[1,1] = vals.data[1]
		strain[2,2] = vals.data[2]
		strain[0,1] = vals.data[3]/2.0
		strain[1,0] = strain[0,1]
		strain[0,2] = vals.data[4]/2.0
		strain[2,0] = strain[0,2]
		strain[1,2] = vals.data[5]/2.0
		strain[2,1] = strain[1,2]

	return strain

# ------------------------------------------------------------------------------
# --------------------------------------------------------------- SCHMITT FACTOR
# ------------------------------------------------------------------------------
def htpp_data_schmitt(odb,ioi,option,section,odb_name):
	step,elem_set = htpp_data_schmitt_option(odb,option)

	step_names = odb.steps.keys()

	soi = ioi.elementSets[' ALL ELEMENTS']
	pos = INTEGRATION_POINT

	# ----------------------------------------------------------- PLASTIC STRAIN
	name = 'PE'
	desc = 'Plastic strain components at integration points'
	dir = 'htpp_output/' + odb_name + '/'

	secs = 1
	if len(section) > 0:
		secs = len(section)

	sT = odb.steps[step_names[0]]
	odb_data = sT.frames[0].fieldOutputs['LE']
	if len(section) == 0:
		vals=odb_data.getSubset(region=soi,position=pos).values
	else:
		sp = section[-1]
		vals=odb_data.getSubset(region=soi,position=pos,sectionPoint=sp).values

	dim = len(vals[0].data)

	for l in step:
		sT = odb.steps[step_names[l-1]]
		for k in range(len(sT.frames)):
			fRa = sT.frames[k]
			field_keys = fRa.fieldOutputs.keys()
			if name not in field_keys:
				if dim > 4:
					invs = (MAX_PRINCIPAL,MID_PRINCIPAL,MIN_PRINCIPAL)
					new_field = fRa.FieldOutput(name=name,description=desc, type=TENSOR_3D_FULL,isEngineeringTensor=True, validInvariants=invs)
				elif dim <= 4:
					invs = (MAX_PRINCIPAL,MID_PRINCIPAL,MIN_PRINCIPAL, MAX_INPLANE_PRINCIPAL,MIN_INPLANE_PRINCIPAL, OUTOFPLANE_PRINCIPAL)
					new_field = fRa.FieldOutput(name=name,description=desc, type=TENSOR_2D_PLANAR,isEngineeringTensor=True, validInvariants=invs)
				odb_data = []
				if dim > 4:
					form = '%f , %f , %f , %f , %f , %f\n'
					for i in range(6):
						var = 'SDV' + str(i+2)
						odb_data.append(fRa.fieldOutputs[var])
				elif dim <= 4:
					form = '%f , %f , 0.0 , %f\n'
					for i in range(3):
						var = 'SDV' + str(i+2)
						odb_data.append(fRa.fieldOutputs[var])

				for j in range(secs):
					vals = []
					for i in odb_data:
						if len(section) == 0:
							vals.append(i.getSubset(region=soi, position=pos).values)
						else:
							sp = section[j]
							vals.append(i.getSubset(region=soi,position=pos, sectionPoint=sp).values)

					if len(vals[0]) > 0:
						with open(dir + 'PE.dat','w') as file:
							for i in range(len(vals[0])):
								if dim > 4:
									file.write(form  %(vals[0][i].data,vals[1][i].data, vals[2][i].data,vals[3][i].data, vals[4][i].data,vals[5][i].data))
								elif dim <= 4:
									file.write(form %(vals[0][i].data,vals[1][i].data, vals[2][i].data))

						with open(dir + 'PE.dat','r') as f:
							pe = [tuple(map(float, i.split(' , '))) for i in f]


						if len(section) == 0:
							new_field.addData(position=pos,set=soi,data=pe)
						else:
							new_field.addData(position=pos,set=soi, sectionPoint=sp,data=pe)
						os.remove(dir + 'PE.dat')
					else:
						pass
	odb.save()

	# ----------------------------------------------------------- SCHMITT FACTOR
	name = 'SCHMITT FACTOR'
	desc = 'Strain path change angle based on schmitt factor'

	for l in step:
		sT = odb.steps[step_names[l-1]]
		for k in range(len(sT.frames)):
			fRa = sT.frames[k]
			field_keys = fRa.fieldOutputs.keys()
			if name not in field_keys:
				new_field = fRa.FieldOutput(name=name,description=desc, type=SCALAR)
				path = 1.0e0
				for j in range(secs):
					if k != 0 and k != 1:
						fr0 = sT.frames[k-2].fieldOutputs['PE']
						fr1 = sT.frames[k-1].fieldOutputs['PE']
						fr2 = sT.frames[k].fieldOutputs['PE']
					else:
						fr0 = sT.frames[k].fieldOutputs['PE']
						fr1 = sT.frames[k].fieldOutputs['PE']
						fr2 = sT.frames[k].fieldOutputs['PE']

					if len(section) == 0:
						data_e0 = fr0.getSubset(region=soi,position=pos)
						data_e1 = fr1.getSubset(region=soi,position=pos)
						data_e2 = fr2.getSubset(region=soi,position=pos)
					else:
						sp = section[j]
						data_e0 = fr0.getSubset(region=soi,position=pos, sectionPoint=sp)
						data_e1 = fr1.getSubset(region=soi,position=pos, sectionPoint=sp)
						data_e2 = fr2.getSubset(region=soi,position=pos, sectionPoint=sp)
					if len(data_e0.values) > 0:
						with open(dir + 'SCHMITT.dat','w') as f:
							if k != 0 and k != 1:
								for i in range(len(data_e0.values)):
									e0=htpp_data_schmitt_aux(data_e0.values[i])
									e1=htpp_data_schmitt_aux(data_e1.values[i])
									e2=htpp_data_schmitt_aux(data_e2.values[i])
									e1_dot = e1 - e0
									e2_dot = e2 - e1
									num = np.tensordot(e1_dot,e2_dot,2)
									den = norm(e1_dot)*norm(e2_dot)
									if den == 0.0:
										path = 1.0e0
									else:
										path = num/den
									f.write('%.3f\n' %path)
							else:
								for i in range(len(data_e0.values)):
									f.write('%.3f\n' %path)

						with open(dir + 'SCHMITT.dat','r') as f:
						    schmitt=[tuple(map(float,i.split(' '))) for i in f]

						if len(section) == 0:
							new_field.addData(position=pos,set=soi,data=schmitt)
						else:
							new_field.addData(position=pos,set=soi, sectionPoint=sp,data=schmitt)
						os.remove(dir + 'SCHMITT.dat')
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
				for f in range(len(sT.frames)):
					fRa = sT.frames[f]
					odb_data = fRa.fieldOutputs[name]
					if len(section) == 0:
						vals=odb_data.getSubset(region=soi,position=pos).values
					else:
						vals = odb_data.getSubset(region=soi,position=pos, sectionPoint=section[-1]).values
					strings = ['schmitt',set.lower(),'s'+str(l),'f'+str(f)]
					fname = dir + '_'.join(strings) + '.dat'
					with open(fname,'w') as f:
						for i in range(len(vals)):
							f.write('%f\n' %vals[i].data)

# ------------------------------------------------------------------------------
