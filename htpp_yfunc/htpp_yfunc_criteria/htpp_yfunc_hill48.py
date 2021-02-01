# ------------------------------------------------------------------------------
# -------------------------------------------------------------- IMPORT PACKAGES
import numpy as np
import os
import math

# ------------------------------------------------------------------------------
# ---------------------------------------------------------- IMPORT COEFFICIENTS
# ------------------------------------------------------------------------------
def htpp_yfunc_hill48_param(odb_name):
	c = np.zeros((6,6))

	path = os.getcwd()[:-4] + '/'
	with open(path + odb_name + '.coe','r') as f:
		params = f.readlines()

	cp = []
	for param in params:
		cp.append(float(param.strip().split(' ')[0]))

	if len(cp) != 7:
		print('Error: number of parameters incorrect.')
		exit()

	s0 = cp[0]

	pf = cp[1]
	pg = cp[2]
	ph = cp[3]
	pl = cp[4]
	pm = cp[5]
	pn = cp[6]

	c[0,0] = pg+ph
	c[0,1] = -ph
	c[0,2] = -pg
	c[1,0] = -ph
	c[1,1] = pf+ph
	c[1,2] = -pf
	c[2,0] = -pg
	c[3,1] = -pf
	c[2,2] = pf+pg
	c[3,3] = 2.0*pn
	c[4,4] = 2.0*pm
	c[5,5] = 2.0*pl
	c = c/(pg+ph)

	return c,s0

# ------------------------------------------------------------------------------
# ------------------------------------- CALCULATE YIELD FUNCTION FOR YIELD LOCUS
# ------------------------------------------------------------------------------
def htpp_yfunc_ylocus_hill48(x,s,c,s0):
	s = [s[0]*x, s[1]*x, 0, s[3] , 0 ,0]

	v = c.dot(s)
	phi = v.dot(s)

	if phi <= 0.0:
		phi = 0.0

	se = math.sqrt(phi) - s0

	return se

# ------------------------------------------------------------------------------
# ------------------------- CALCULATE YIELD FUNCTION FOR ANISOTROPY COEFFICIENTS
# ------------------------------------------------------------------------------
def htpp_yfunc_aniso_hill48(s,c):
	v = c.dot(s)
	phi = v.dot(s)

	if phi <= 0.0:
		phi = 0.0

	se = math.sqrt(phi)

	dseds = v/se

	return se,dseds

# ------------------------------------------------------------------------------
