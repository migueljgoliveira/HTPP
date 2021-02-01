# ------------------------------------------------------------------------------
# -------------------------------------------------------------- IMPORT PACKAGES
import numpy as np
import os
import math

# ------------------------------------------------------------------------------
# ---------------------------------------------------------- IMPORT COEFFICIENTS
# ------------------------------------------------------------------------------
def htpp_yfunc_yld2004_param(odb_name):
	cp1 = np.zeros((6,6))
	cp2 = np.zeros((6,6))

	path = os.getcwd()[:-4] + '/'
	with open(path + odb_name + '.coe','r') as f:
		params = f.readlines()

	cp = []
	for param in params:
		cp.append(float(param.strip().split(' ')[0]))

	if len(cp) != 20:
		print('Error: number of parameters incorrect.')
		exit()

	s0 = cp[0]

	cp1[0,1] = -cp[1]
	cp1[0,2] = -cp[2]
	cp1[1,0] = -cp[3]
	cp1[1,2] = -cp[4]
	cp1[2,0] = -cp[5]
	cp1[2,1] = -cp[6]
	cp1[3,3] = cp[9]
	cp1[4,4] = cp[8]
	cp1[5,5] = cp[7]
	cp2[0,1] = -cp[10]
	cp2[0,2] = -cp[11]
	cp2[1,0] = -cp[12]
	cp2[1,2] = -cp[13]
	cp2[2,0] = -cp[14]
	cp2[2,1] = -cp[15]
	cp2[3,3] = cp[18]
	cp2[4,4] = cp[17]
	cp2[5,5] = cp[16]
	a = cp[19]

	return cp1,cp2,a,s0

# ------------------------------------------------------------------------------
# ------------------------------------------------------- CALCULATE D(PSP)/D(HP)
# ------------------------------------------------------------------------------
def htpp_yfunc_yld2004_dpsdhp(i,psp,hp,dpsdhp):
	dummy = (psp[i]**2)-2.0*hp[0]*psp[i]-hp[1]
	dpsdhp[i,0] = (psp[i]**2)/dummy
	dpsdhp[i,1] = psp[i]/dummy
	dpsdhp[i,2] = 2.0/(3.0*dummy)

	return dpsdhp

# ------------------------------------------------------------------------------
# --------------------------------------------- CALCULATE 1ST ORDER DIFFERENTIAL
# ------------------------------------------------------------------------------
def htpp_yfunc_yld2004_dseds2(ctp1, ctp2,sp1,sp2,psp1,psp2,hp1,hp2,cetpq1,cetpq2,dc,a,f):

	eps2 = 1.0e-15
	delta = np.identity(3)
	ami = 1.0/a
	dfadpsp1 = np.zeros(3)
	dfadpsp2 = np.zeros(3)
	for i in range(0,3):
		for j in range(0,3):
			dfadpsp1[i] = dfadpsp1[i]+(psp1[i]-psp2[j])*abs(psp1[i]-psp2[j])**(a-2.0)
			dfadpsp2[i] = dfadpsp2[i]+(psp1[j]-psp2[i])*abs(psp1[j]-psp2[i])**(a-2.0)
		dfadpsp1[i] = a*dfadpsp1[i]
		dfadpsp2[i] = -a*dfadpsp2[i]

	dpsdhp1 = np.zeros((3,3))
	dpsdhp2 = np.zeros((3,3))
	dfadhp1 = np.zeros(3)
	dfadhp2 = np.zeros(3)
	# --------------------------------------------------------- theta'<>0 & <>pi
	if abs(cetpq1-1.0)>=eps2 and abs(cetpq1+1.0)>=eps2:
		for i in range(0,3):
			dpsdhp1 = htpp_yfunc_yld2004_dpsdhp(i,psp1,hp1,dpsdhp1)
	# ----------------------------------------------------------------- theta'=0
	elif abs(cetpq1-1.0)<eps2:
		i = 0
		dpsdhp1 = htpp_yfunc_yld2004_dpsdhp(i,psp1,hp1,dpsdhp1)
		for i in range(1,3):
			for j in range(0,3):
				dpsdhp1[i,j] = -0.5*(dpsdhp1[0,j]-3.0*delta[0,j])
	# ---------------------------------------------------------------- theta'=pi
	else:
		i = 2
		dpsdhp1 = htpp_yfunc_yld2004_dpsdhp(i,psp1,hp1,dpsdhp1)
		for i in range(0,2):
			for j in range(0,3):
				dpsdhp1[i,j] = -0.5*(dpsdhp1[2,j]-3.0*delta[0,j])

	# --------------------------------------------------------- theta'<>0 & <>pi
	if abs(cetpq2-1.0)>= eps2 and abs(cetpq2+1.0)>=eps2:
		for i in range(0,3):
			dpsdhp2 = htpp_yfunc_yld2004_dpsdhp(i,psp2,hp2,dpsdhp2)
	# ----------------------------------------------------------------- theta'=0
	elif abs(cetpq2-1.0)<eps2:
		i = 0
		dpsdhp2 = htpp_yfunc_yld2004_dpsdhp(i,psp2,hp2,dpsdhp2)
		for i in range(1,3):
			for j in range(0,3):
				dpsdhp2[i,j] = -0.5*(dpsdhp2[0,j]-3.0*delta[0,j])
	# ---------------------------------------------------------------- theta'=pi
	else:
		i = 2
		dpsdhp2 = htpp_yfunc_yld2004_dpsdhp(i,psp2,hp2,dpsdhp2)
		for i in range(0,2):
			for j in range(0,3):
				dpsdhp2[i,j] = -0.5*(dpsdhp2[2,j]-3.0*delta[0,j])

	for i in range(0,3):
		for j in range(0,3):
			dfadhp1[i] = dfadhp1[i]+dfadpsp1[j]*dpsdhp1[j,i]
			dfadhp2[i] = dfadhp2[i]+dfadpsp2[j]*dpsdhp2[j,i]

	# -------------------------------------------------------------- d(hp)/d(sp)
	dhdsp1 = np.zeros((3,6))
	dhdsp2 = np.zeros((3,6))
	j = [1,2,0]
	k = [2,0,1]
	l = [5,4,3]
	for i in range(0,3):
		dhdsp1[0,i] = 1.0/3.0
		dhdsp2[0,i] = 1.0/3.0
		dhdsp1[1,i] = -1.0/3.0*(sp1[j[i]]+sp1[k[i]])
		dhdsp2[1,i] = -1.0/3.0*(sp2[j[i]]+sp2[k[i]])
		dhdsp1[2,i] = 1.0/2.0*(sp1[j[i]]*sp1[k[i]]-sp1[l[i]]**2)
		dhdsp2[2,i] = 1.0/2.0*(sp2[j[i]]*sp2[k[i]]-sp2[l[i]]**2)
	k = [0,0,0,2,1,0]
	l = [0,0,0,4,5,3]
	m = [0,0,0,5,3,4]
	for i in range(3,6):
		dhdsp1[1,i] = 2.0/3.0*sp1[i]
		dhdsp2[1,i] = 2.0/3.0*sp2[i]
		dhdsp1[2,i] = sp1[l[i]]*sp1[m[i]]-sp1[k[i]]*sp1[i]
		dhdsp2[2,i] = sp2[l[i]]*sp2[m[i]]-sp2[k[i]]*sp2[i]
	# --------------------------------------------------------------- d(sp)/d(s)
	dsdsp1 = np.zeros((6,6))
	dsdsp2 = np.zeros((6,6))
	for i in range(0,6):
		for j in range(0,6):
			dsdsp1[i,j] = ctp1[i,j]
			dsdsp2[i,j] = ctp2[i,j]

	# -------------------------------------------------------------- d(fai)/d(s)
	dfads = np.zeros(6)
	xx1 = np.zeros((3,6))
	xx2 = np.zeros((3,6))
	for l in range(0,6):
		for j in range(0,3):
			for k in range(0,6):
				xx1[j,l] = xx1[j,l]+dhdsp1[j,k]*dsdsp1[k,l]
				xx2[j,l] = xx2[j,l]+dhdsp2[j,k]*dsdsp2[k,l]
			dfads[l] = dfads[l]+dfadhp1[j]*xx1[j,l]+dfadhp2[j]*xx2[j,l]

	# --------------------------------------------------------------- d(se)/d(s)
	dseds = np.zeros(6)
	dsedfa=f**(ami-1.0)/a/dc**ami
	for i in range(0,6):
		dseds[i] = dsedfa*dfads[i]

	return dseds

# ------------------------------------------------------------------------------
# --------------------------------------------------- CALCULATE YIELD FUNCTION 2
# ------------------------------------------------------------------------------
def htpp_yfunc_yld2004_sub(sp):
	hp = np.zeros(3)
	hp[0] = (sp[0]+sp[1]+sp[2])/3.0
	hp[1] = (sp[4]**2+sp[5]**2+sp[3]**2-sp[1]*sp[2]-sp[2]*sp[0]-sp[0]*sp[1])/3.0
	hp[2] = (2*sp[4]*sp[5]*sp[3]+sp[0]*sp[1]*sp[2]-sp[0]*sp[5]**2-sp[1]*sp[4]**2-sp[2]*sp[3]**2)/2.0

	hpq = math.sqrt(hp[0]**2+hp[1]**2+hp[2]**2)
	psp = np.zeros(3)
	if hpq > 1.0e-16:
		cep = hp[0]**2+hp[1]
		ceq = (2*hp[0]**3+3*hp[0]*hp[1]+2*hp[2])/2.0
		cetpq = ceq/cep**(3.0/2.0)
		if cetpq > 1.0:
			cetpq = 1.0
		elif cetpq < -1.0:
			cetpq = -1.0
		cet = math.acos(cetpq)

		psp[0] = 2*math.sqrt(cep)*math.cos(cet/3.0)+hp[0]
		psp[1] = 2*math.sqrt(cep)*math.cos((cet+4.0*math.pi)/3.0)+hp[0]
		psp[2] = 2*math.sqrt(cep)*math.cos((cet+2.0*math.pi)/3.0)+hp[0]
	else:
		cetpq = 0.0

	return psp,cetpq,hp

# ------------------------------------------------------------------------------
# ------------------------------ CALCULATE COEFFICIENT OF EQUIVALENT STRESS DC 2
# ------------------------------------------------------------------------------
def htpp_yfunc_yld2004_coef_sub(cp):
	aap = np.zeros(3)
	aap[0] = (cp[0,1]+cp[0,2]-2.0*cp[1,0]+cp[1,2]-2.0*cp[2,0]+cp[2,1])/9.0
	aap[1]=((2.0*cp[1,0]-cp[1,2])*(cp[2,1]-2.0*cp[2,0])+(2.0*cp[2,0]-cp[2,1])*(cp[0,1]+cp[0,2])+(cp[0,1]+cp[0,2])*(2.0*cp[1,0]-cp[1,2]))/27.0
	aap[2]=(cp[0,1]+cp[0,2])*(cp[1,2]-2.0*cp[1,0])*(cp[2,1]-2.0*cp[2,0])/54.0

	ppp = aap[0]**2+aap[1]
	qqp = (2*aap[0]**3 + 3*aap[0]*aap[1]+2*aap[2])/2.0
	ttp = math.acos(qqp/ppp**(3.0/2.0))

	bbp = np.zeros(3)
	bbp[0] = 2*math.sqrt(ppp)*math.cos(ttp/3.0)+aap[0]
	bbp[1] = 2*math.sqrt(ppp)*math.cos((ttp+4*math.pi)/3.0)+aap[0]
	bbp[2] = 2*math.sqrt(ppp)*math.cos((ttp+2*math.pi)/3.0)+aap[0]

	return bbp

# ------------------------------------------------------------------------------
# -------------------------------- CALCULATE COEFFICIENT OF EQUIVALENT STRESS DC
# ------------------------------------------------------------------------------
def htpp_yfunc_yld2004_coef(cp1,cp2,a):

	bbp1 = htpp_yfunc_yld2004_coef_sub(cp1)
	bbp2 = htpp_yfunc_yld2004_coef_sub(cp2)
	dc = 0.0
	for i in range(3):
		for j in range(3):
			dc += abs(bbp1[i]-bbp2[j])**a

	return dc

# ------------------------------------------------------------------------------
# ------------------------------------- CALCULATE YIELD FUNCTION FOR YIELD LOCUS
# ------------------------------------------------------------------------------
def htpp_yfunc_ylocus_yld2004(x,s,cp1,cp2,a,s0):
	s = [s[0]*x, s[1]*x, 0, s[3] , 0 ,0]
	cl = np.zeros((6,6))
	for i in range(3):
		for j in range(3):
			cl[i,j] = -1
			if i == j:
				cl[i,j] = 2

	for i in range(3,6):
		cl[i,i] = 3
	cl = cl/3.0

	dc = htpp_yfunc_yld2004_coef(cp1,cp2,a)

	ctp1 = cp1.dot(cl)
	ctp2 = cp2.dot(cl)
	sp1 = ctp1.dot(s)
	sp2 = ctp2.dot(s)

	psp1,cetpq1,hp1 = htpp_yfunc_yld2004_sub(sp1)
	psp2,cetpq2,hp2 = htpp_yfunc_yld2004_sub(sp2)

	f = 0.0
	for i in range(3):
		for j in range(3):
			f += abs(psp1[i]-psp2[j])**a
	se = (f/dc)**(1.0/a) - s0

	return se

# ------------------------------------------------------------------------------
# ------------------------- CALCULATE YIELD FUNCTION FOR ANISOTROPY COEFFICIENTS
# ------------------------------------------------------------------------------
def htpp_yfunc_aniso_yld2004(s,cp1,cp2,a):
	cl = np.zeros((6,6))
	for i in range(3):
		for j in range(3):
			cl[i,j] = -1
			if i == j:
				cl[i,j] = 2

	for i in range(3,6):
		cl[i,i] = 3
	cl = cl/3.0

	dc = htpp_yfunc_yld2004_coef(cp1,cp2,a)

	ctp1 = cp1.dot(cl)
	ctp2 = cp2.dot(cl)
	sp1 = ctp1.dot(s)
	sp2 = ctp2.dot(s)

	psp1,cetpq1,hp1 = htpp_yfunc_yld2004_sub(sp1)
	psp2,cetpq2,hp2 = htpp_yfunc_yld2004_sub(sp2)

	f = 0.0
	for i in range(3):
		for j in range(3):
			f += abs(psp1[i]-psp2[j])**a

	dseds = htpp_yfunc_yld2004_dseds2(ctp1,ctp2,sp1,sp2,psp1,psp2,hp1,hp2,cetpq1,cetpq2,dc,a,f)

	se = (f/dc)**(1.0/a)

	return se,dseds

# ------------------------------------------------------------------------------
