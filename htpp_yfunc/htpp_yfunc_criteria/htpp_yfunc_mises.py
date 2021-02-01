# ------------------------------------------------------------------------------
# -------------------------------------------------------------- IMPORT PACKAGES
import numpy as np
import os
import math

# ------------------------------------------------------------------------------
# ---------------------------------------------------------- IMPORT COEFFICIENTS
# ------------------------------------------------------------------------------
def htpp_yfunc_mises_param(odb_name):
	path = os.getcwd()[:-4] + '/'
	with open(path + odb_name + '.coe','r') as f:
		params = f.readlines()

	cp = []
	for param in params:
		cp.append(float(param.strip().split(' ')[0]))

	if len(cp) != 1:
		print('Error: number of parameters incorrect.')
		exit()

	s0 = cp[0]

	return s0

# ------------------------------------------------------------------------------
# --------------------------------------------------- YIELD FUNCTION - VON MISES
# ------------------------------------------------------------------------------
def htpp_yfunc_mises(x,s,s0):
	s = [s[0]*x, s[1]*x, s[2], 0 , 0 ,0]
	c = np.zeros((6,6))
	for i in range(3):
		for j in range(3):
			c[i,j] = -0.5
		c[i,i] = 1
	for i in range(3,6):
		c[i,i] = 3

	v = c.dot(s)
	phi = v.dot(s)
	se = math.sqrt(phi) - s0

	return se

# ------------------------------------------------------------------------------
