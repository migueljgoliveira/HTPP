# ------------------------------------------------------------------------------
# -------------------------------------------------------------- IMPORT PACKAGES
import os
import shutil
import sys
from math import sin, cos, pi, degrees
import numpy as np

# ------------------------------------------------------------------------------
# ----------------------------------------------------------------- IMPORT FILES
# -------------------------------------------------------------- Yield Functions
from htpp_yfunc_hill48 import htpp_yfunc_aniso_hill48, htpp_yfunc_hill48_param
from htpp_yfunc_yld2004 import htpp_yfunc_aniso_yld2004, htpp_yfunc_yld2004_param
from htpp_yfunc_yld2000_2d import htpp_yfunc_aniso_yld2000_2d, htpp_yfunc_yld2000_2d_param

# ------------------------------------------------------- YIELD ANISOTROPY AUX 2
def htpp_yfunc_anisotropy_aux2(ang,se,dseds,s0):
	s = s0/se
	num1 = dseds[0]*sin(ang)**2
	num2 = dseds[1]*cos(ang)**2
	if len(dseds) > 3:
		num3 = dseds[3]*sin(ang)*cos(ang)
	else:
		num3 = dseds[2]*sin(ang)*cos(ang)
	num = num3 - num1 - num2
	den = dseds[0] + dseds[1]
	r = num/den
	r = (se/den)-1

	return s,r

# ------------------------------------------------------- YIELD ANISOTROPY AUX 1
def htpp_yfunc_anisotropy_aux1(ang):
	xx = cos(ang)**2
	yy = sin(ang)**2
	xy = sin(ang)*cos(ang)
	s = [xx, yy, 0.0, xy, 0.0, 0.0]

	return s

# ------------------------------------------------------------------------------
# ------------------------------------------------------------- YIELD ANISOTROPY
# ------------------------------------------------------------------------------
def htpp_yfunc_anisotropy(option,odb_name):
	yldname = '\n'.join(s for s in option if 'yldname=' in s).replace(",", "").replace("\n", "")[9:-1].strip()

	dir = 'htpp_output/' + odb_name + '/'

	angle = np.linspace(0,pi/2,91)
	sAngles,rAngles = [],[]

#------------------------------------------------------------------------ hill48
	if yldname == 'hill48':
		c,s0 = htpp_yfunc_hill48_param(odb_name)
		for i in range(0,len(angle)):
				s = htpp_yfunc_anisotropy_aux1(angle[i])
				se,dseds = htpp_yfunc_aniso_hill48(s,c)
				sAng,rAng = htpp_yfunc_anisotropy_aux2(angle[i],se,dseds,s0)
				sAngles.append(sAng)
				rAngles.append(rAng)

#------------------------------------------------------------------- yld2004-18p
	elif yldname == 'yld2004-18p':
		cp1,cp2,a,s0 = htpp_yfunc_yld2004_param(odb_name)
		for i in range(0,len(angle)):
				s = htpp_yfunc_anisotropy_aux1(angle[i])
				se,dseds = htpp_yfunc_aniso_yld2004(s,cp1,cp2,a)
				sAng,rAng = htpp_yfunc_anisotropy_aux2(angle[i],se,dseds,s0)
				sAngles.append(sAng)
				rAngles.append(rAng)
#-------------------------------------------------------------------- yld2000-2d
	elif yldname == 'yld2000-2d':
		a,em,s0 = htpp_yfunc_yld2000_2d_param(odb_name)
		for i in range(0,len(angle)):
				s = htpp_yfunc_anisotropy_aux1(angle[i])
				se,dseds = htpp_yfunc_aniso_yld2000_2d(s,a,em)
				sAng,rAng = htpp_yfunc_anisotropy_aux2(angle[i],se,dseds,s0)
				sAngles.append(sAng)
				rAngles.append(rAng)
	else:
		return

# ------------------------------------------------------------------------------
	sAngles_norm = [x/s0 for x in sAngles]
	fname = 'yieldaniso_' + yldname
	with open(dir + fname + '.dat','w') as f:
		f.write('theta, Y_theta , Y_theta/Y_0, R_theta \n')
		for i in range(len(sAngles)):
			f.write('%.0f, %f , %f , %f \n' %(degrees(angle[i]),sAngles[i],sAngles_norm[i],rAngles[i]))

# ------------------------------------------------------------------------------
