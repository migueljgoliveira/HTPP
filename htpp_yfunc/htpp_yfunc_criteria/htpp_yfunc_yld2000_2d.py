# ------------------------------------------------------------------------------
# -------------------------------------------------------------- IMPORT PACKAGES
import numpy as np
import os
import math

# ------------------------------------------------------------------------------
# ---------------------------------------------------------- IMPORT COEFFICIENTS
# ------------------------------------------------------------------------------
def htpp_yfunc_yld2000_2d_param(odb_name):
	path = os.getcwd()[:-4] + '/'
	with open(path + odb_name + '.coe','r') as f:
		params = f.readlines()

	cp = []
	for param in params:
		cp.append(float(param.strip().split(' ')[0]))

	if len(cp) != 10:
		print('Error: number of parameters incorrect.')
		exit()

	s0 = cp[0]
	em = cp[-1]

	cp.pop(0)
	cp.pop(-1)

	return cp,em,s0

# ------------------------------------------------------------------------------
# --------------------------------------------- CALCULATE 1ST ORDER DIFFERENTIAL
# ------------------------------------------------------------------------------
def htpp_yfunc_yld2004_dseds(am,em,q,phi,x,y,se):
	eps = 1.0e-16
	p = [1.0,-1.0]

	emi = 1.0/em

	# ----------------------------------------------------------------- dse/dphi
	dsedphi = np.zeros(2)
	for n in range(2):
		dsedphi[n] = (0.5**emi)*emi*q**(emi-1.0)

	# ------------------------------------------------------------------ dphi/dx
	n = 0
	a0 = x[n,0]-x[n,1]
	b0 = abs(a0)
	sgn0=0
	if b0 >= eps*se:
		sgn0 = a0/b0
	dphidx = np.zeros((2,2))
	dphidx[0,0] =  em*b0**(em-1.0)*sgn0
	dphidx[0,1] = -em*b0**(em-1.0)*sgn0

	n = 1
	a1 = 2.0*x[n,0]+x[n,1]
	a2 = x[n,0]+2.0*x[n,1]
	b1 = abs(a1)
	b2 = abs(a2)
	sgn1,sgn2 = 0.0,0.0
	if b1 >= eps*se:
		sgn1 = a1/b1
	if b2 >= eps*se:
		sgn2 = a2/b2

	dphidx[1,0] = em*( 2.0*b1**(em-1.0)*sgn1 + b2**(em-1.0)*sgn2 )
	dphidx[1,1] = em*( b1**(em-1.0)*sgn1 + 2.0*b2**(em-1.0)*sgn2 )

	dxdy = np.zeros((2,2,3))
	for n in range(2):
		a = math.sqrt((y[n,0]-y[n,1])**2 + 4*y[n,2]**2)
		if a >= eps*se:
			for j in range(2):
				dxdy[n,j,0] = 0.5*(1.0+p[j]*(y[n,0]-y[n,1])/a)
				dxdy[n,j,1] = 0.5*(1.0-p[j]*(y[n,0]-y[n,1])/a)
				dxdy[n,j,2] = 2.0*p[j]*y[n,2]/a
		else:
			for j in range(2):
				dxdy[n,j,0] = 0.5*(1.0+0.0)
				dxdy[n,j,1] = 0.5*(1.0-0.0)
				dxdy[n,j,2] = 2.0*0.0

	dyds = np.zeros((2,3,3))
	for n in range(2):
		for i in range(3):
			for j in range(3):
				dyds[n,i,j] = am[n,i,j]

	# --------------------------------------------------------------- d(se)/d(s)
	dseds = np.zeros(3)
	for n in range(2):
		for m in range(2):
			for k in range(3):
				for i in range(3):
					dseds[i] += dsedphi[n]*dphidx[n,m]*dxdy[n,m,k]*dyds[n,k,i]

	return dseds

# ------------------------------------------------------------------------------
# --------------------------------------- CALCULATE PHI VALUES OF YIELF FUNCTION
# ------------------------------------------------------------------------------
def htpp_yfunc_yld2000_2d_phi(am,em,s):
	p = [1.0,-1.0]

	y = np.zeros((2,3))
	for n in range(2):
		y[n] = am[n].dot(s)

	x = np.zeros((2,2))
	for n in range(2):
		a = math.sqrt((y[n,0]-y[n,1])**2 + 4*y[n,2]**2)
		for i in range(2):
			x[n,i] = 0.5*(y[n,0]+y[n,1]+p[i]*a)

	phi = np.zeros(2)
	phi[0] = abs(x[0,0]-x[0,1])**em
	phi[1] = abs(2*x[1,1]+x[1,0])**em + abs(2*x[1,0]+x[1,1])**em

	return phi,x,y

# ------------------------------------------------------------------------------
# --------------------------------------------- SET LINEAR TRANSFORMATION MATRIX
# ------------------------------------------------------------------------------
def htpp_yfunc_yld2000_2d_am(a):
	am = np.zeros((2,3,3))

	am[0,0,0] =  2.0*a[0]
	am[0,0,1] = -1.0*a[0]
	am[0,1,0] = -1.0*a[1]
	am[0,1,1] =  2.0*a[1]
	am[0,2,2] =  3.0*a[6]

	am[1,0,0] = -2.0*a[2]+2.0*a[3]+8.0*a[4]-2.0*a[5]
	am[1,0,1] =      a[2]-4.0*a[3]-4.0*a[4]+4.0*a[5]
	am[1,1,0] =  4.0*a[2]-4.0*a[3]-4.0*a[4]+    a[5]
	am[1,1,1] = -2.0*a[2]+8.0*a[3]+2.0*a[4]-2.0*a[5]
	am[1,2,2] =  9.0*a[7]

	am[0] = am[0]/3.0
	am[1] = am[1]/9.0

	return am

# ------------------------------------------------------------------------------
# ------------------------------------- CALCULATE YIELD FUNCTION FOR YIELD LOCUS
# ------------------------------------------------------------------------------
def htpp_yfunc_ylocus_yld2000_2d(x,s,a,em,s0):
	s = [s[0]*x, s[1], s[3]*x]

	am = htpp_yfunc_yld2000_2d_am(a)

	phi,x,y = htpp_yfunc_yld2000_2d_phi(am,em,s)

	q = phi[0] + phi[1]
	if q <= 0.0:
		q = 0.0
	se = (0.5*q)**(1.0/em) - s0

	return se

# ------------------------------------------------------------------------------
# ------------------------- CALCULATE YIELD FUNCTION FOR ANISOTROPY COEFFICIENTS
# ------------------------------------------------------------------------------
def htpp_yfunc_aniso_yld2000_2d(s,a,em):
	s = [s[0], s[1], s[3]]

	am = htpp_yfunc_yld2000_2d_am(a)
	phi,x,y = htpp_yfunc_yld2000_2d_phi(am,em,s)

	q = sum(phi)
	if q <= 0.0:
		q = 0.0

	se = (0.5*q)**(1.0/em)

	dseds = htpp_yfunc_yld2004_dseds(am,em,q,phi,x,y,se)

	return se,dseds

# ------------------------------------------------------------------------------
