# ------------------------------------------------------------------------------
# -------------------------------------------------------------- IMPORT PACKAGES
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.patches as mpt
from matplotlib.legend_handler import HandlerBase
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
from math import floor, ceil, radians, pi

# ------------------------------------------------------------ HANDLER COLOR MAP
class HandlerColormap(HandlerBase):
	def __init__(self,cmap,num,n,**kw):
		HandlerBase.__init__(self, **kw)
		self.cmap = cmap
		self.num = num
		self.n = n

	def create_artists(self,legend,orig_handle,xdescent,ydescent,width, height,fontsize,trans):
		stripes = []
		if self.n == 0:
			self.num = 1
		for i in range(self.num):
			coord = [xdescent+i*width/self.num,ydescent]
			wid = width/self.num
			if self.n == 0:
				s = mpt.Rectangle(coord,wid,height,transform=trans, fc=(0.75,0.75,0.75,1.0))
			elif self.n == 1:
				s = mpt.Rectangle(coord,wid,height,transform=trans, fc=self.cmap((2*i+1)/(2*self.num)))

			stripes.append(s)

		return stripes

# ----------------------------------------------------------- ROTATION PLOT NAME
def htpp_plot_rotation_name(set,step,frame,num,table):
	name = ['ROTATION [']
	set = set.replace('_','\_')
	name.append('set: '  + set.upper() + ' /')
	name.append('step: ' + str(step) + ' /')
	name.append('frame: '+ str(frame))
	if num == 2:
		name.append('/ colormap: PEEQ')

	name.append(']')
	name = ' '.join(name)

	table.append(name)

	return table
# ------------------------------------------------------- ROTATION ANGLE OPTIONS
def htpp_plot_rotation_option(option):
	step = '\n'.join(s for s in option if 'step=' in s).replace(",", "").replace("\n", "")[6:-1].strip().split(';')
	step = [int(s) for s in step]
	frame = '\n'.join(s for s in option if 'frame=' in s).replace(",", "").replace("\n", "")[7:-1].strip().split(';')
	frame = [int(i) for i in frame]
	elem_set = '\n'.join(s for s in option if 'elemSet=' in s).replace(",", "").replace("\n", "")[9:-1].split(';')
	num = '\n'.join(s for s in option if 'num=' in s).replace(",", "").replace("\n", "")[5:-1].split(';')
	num = [float(n) for n in num]
	lims = '\n'.join(s for s in option if 'lims=' in s).replace("\n" , "")[6:-1].split(';')
	tmp = []
	if lims[0] != '':
		for lim in lims:
			l = lim[1:-1].split(',')
			tmp = [float(l[0]),float(l[1]),float(l[2])]
	lims = tmp

	return step,frame,elem_set,lims,num

# --------------------------------------------------------- ROTATION ANGLE AUX 2
def htpp_plot_rotation_aux2(bin_elas,bin_plas,peeq,obs,lims,n):

	blue = (0,0.3,0.85,1.0)
	grey = (0.75,0.75,0.75,1.0)
	black_02 = (0,0,0,0.2)
	cjet = mpl.cm.get_cmap('jet', 12)
	al = 'center'
	fnt = 14
	rast = True

	ang = np.arange(0.5,90,1)

	fig = plt.figure(num=n,dpi=300)
	ax = fig.add_subplot(111)

	tot = [0.0 for i in range(90)]

	if n == 1 or n == 2:
		bin_elas_norm = [ 100.0*x/obs for x in bin_elas]

		bars = plt.bar(ang,bin_elas_norm,bottom=tot,width=1.0,color=(198.0/255.0,200.0/255.0,184.0/255.0,1.0),edgecolor='none',rasterized=True)

		tot = [x + y for x, y in zip(tot, bin_elas_norm)]

	if lims:
		plt.ylim(0,lims[1])
	else:
		plt.ylim(0,ceil(max(tot)))

	if n == 3:
		obs = obs - sum(bin_elas)

	for i in range(0,len(bin_plas[0])):
		tmp = bin_plas[:,i]
		bin_plas_norm = [ 100.0*x/obs for x in tmp]
		if n == 1:
			bars = plt.bar(ang,bin_plas_norm,bottom=tot,width=1.0,color=(198.0/255.0,200.0/255.0,184.0/255.0,1.0),edgecolor='none',rasterized=rast)
		elif n == 2 or n == 3:
			bars = plt.bar(ang,bin_plas_norm,bottom=tot,width=1.0, color=cjet(i),edgecolor='none',rasterized=rast)
		tot = [x + y for x, y in zip(tot,bin_plas_norm)]
		if lims:
			plt.ylim(0,lims[1])
		else:
			plt.ylim(0,ceil(max(tot)))

	if lims:
		ymax = lims[1]
	else:
		ymax = ceil(max(tot))

	if n == 2 or n == 3:
		sm = plt.cm.ScalarMappable(cmap=cjet,norm=plt.Normalize(vmin=0, vmax=max(peeq)))
		sm._A = []
		tks = np.linspace(0.0,max(peeq),13)
		clb = plt.colorbar(sm,ticks=tks)
		clb.solids.set_rasterized(rast)
		clb.set_label(r'$\bar \epsilon ^\mathrm{p}$ [-]',labelpad=-23,y=1.11, rotation=0)
		clb.set_ticklabels(['%.2f'%round(i,2) for i in tks])

	lbs = ['elastic','plastic']
	if n == 1:
		pl = mpt.Rectangle((0,0),1,1,color=blue,rasterized=True)
		el = mpt.Rectangle((0,0),1,1,color=blue,rasterized=True)
		# leg = plt.legend([el,pl],lbs,loc=0,frameon=False, fontsize=fnt)
	elif n == 2 or n == 3:
		cmaps = [plt.cm.jet, plt.cm.jet]
		hdls = [mpt.Rectangle((0,0),1,1,rasterized=rast) for _ in cmaps]
		hdl_map = dict(zip(hdls,                 [HandlerColormap(cmaps[i],12,i) for i in range(2)]))
		# plt.legend(handles=hdls,labels=lbs,handler_map=hdl_map,fontsize=fnt, loc=0,frameon=False)

	plt.xlabel('$\gamma$ $[^\circ]$')
	ax.set_ylabel('Density [\%]')
	ax.yaxis.set_label_coords(-0.11, 0.5)
	plt.xlim(0,90)
	plt.xticks(np.linspace(0,90,7))

	if lims:
		plt.yticks(np.arange(lims[0],lims[1]+lims[2],lims[2]))
	else:
		if (ymax % 2) != 0:
			ymax = ymax + 1
		for i in range(ymax-1,0,-1):
			a = ymax % i
			if a == 0:
				dy = ymax/i
				break
		plt.yticks(np.arange(0,ymax+dy,dy))

	plt.close()

	return fig

# --------------------------------------------------------- ROTATION ANGLE AUX 1
def htpp_plot_rotation_aux1(rotAngle,peeq):
	fig = plt.figure()
	ax = fig.add_subplot(111)

	h = plt.hist(rotAngle,90)
	count = h[0]
	A = np.array([rotAngle,peeq])
	B = A[:,np.argsort(A[0,:])]
	k = 0
	j = 0
	binsPeeq = np.linspace(0,max(peeq),13)
	freqBin_Plas = np.zeros((len(count),12))
	freqBin_Elas = np.zeros(len(count))
	for i in range(len(count)):
		j = j + int(count[i])
		temp = B[:,k:j]
		for n in range(12):
			cont = 0
			contEls = 0
			for m in range(int(count[i])):
				if temp[1,m] > binsPeeq[n] and temp[1,m] <= binsPeeq[n+1]:
					cont = cont + 1
				elif temp[1,m] == 0.0:
					contEls = contEls + 1
			freqBin_Plas[i,n] = int(cont)
			freqBin_Elas[i] = int(contEls)
		k = k + int(count[i])

	nObs = sum(count,1)

	plt.close()

	return freqBin_Elas,freqBin_Plas,nObs

# ------------------------------------------------------------------------------
# --------------------------------------------------------------- ROTATION ANGLE
# ------------------------------------------------------------------------------
def htpp_plot_rotation(odb_name,option,pdf,size,table):
	plt.rc('text', usetex=1)
	plt.rc('font', family='serif',size=18)

	size = [[[-0.1,-0.2],[6.0,4.6]],[[0.08,-0.1],[5.725,4.675]],[[0.08,-0.1],[5.725,4.675]]]

	dir = 'htpp_output/' + odb_name + '/'

	step,frame,elem_set,lims,num = htpp_plot_rotation_option(option)

	for set in elem_set:
		for l in step:
			for f in frame:
				for n in num:
					strings = ['rotation',set.lower(),'s'+str(l),'f'+str(f)]
					fname = dir + '_'.join(strings) + '.dat'
					rotAngle = np.loadtxt(fname)

					strings = ['peeq',set.lower(),'s'+str(l),'f'+str(f)]
					fname = dir + '_'.join(strings) + '.dat'
					peeq = np.loadtxt(fname)

					bin_elas,bin_plas,obs = htpp_plot_rotation_aux1(rotAngle ,peeq)

					fig = htpp_plot_rotation_aux2(bin_elas,bin_plas,peeq,obs, lims,n)

					box = mpl.transforms.Bbox(size[int(n)-1])
					pdf.savefig(fig,dpi=500,bbox_inches=box)

					table = htpp_plot_rotation_name(set,l,f,n,table)

	return pdf,table
# ------------------------------------------------------------------------------
