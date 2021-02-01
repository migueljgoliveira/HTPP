# ------------------------------------------------------------------------------
# -------------------------------------------------------------- IMPORT PACKAGES
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.patches as mpt
from matplotlib.legend_handler import HandlerBase, HandlerPatch
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
from math import floor, ceil, sqrt, cos
from scipy.interpolate import CubicSpline

# -------------------------------------------------------------- HANDLER ELLIPSE
class HandlerEllipse(HandlerPatch):
	def create_artists(self,legend,orig_handle,xdescent,ydescent,width,  height,fontsize,trans):
		x, y = 15.3, 2.35
		wid = 8.85
		center = (x,y)
		p = mpt.Ellipse(xy=center,width=wid,height=wid)
		self.update_prop(p,orig_handle,legend)
		p.set_transform(trans)

		return [p]

# ------------------------------------------------------------ HANDLER COLOR MAP
class HandlerColormap(HandlerBase):
	def __init__(self,cmap,num,n,**kw):
		HandlerBase.__init__(self, **kw)
		self.cmap = cmap
		self.num = num
		self.n = n

	def create_artists(self,legend,orig_handle,xdescent,ydescent,width, height,fontsize,trans):
		grey = (0.75,0.75,0.75,1.0)
		stripes = []
		width = 6.9
		x,y = 11.85, -1.1
		if self.n == 0:
			self.num = 1
		for i in range(self.num):
			coord = [x+i*width/self.num,y]
			wid = width/self.num
			if self.n == 0:
				s = mpt.Rectangle(coord,wid,width,transform=trans,fc=grey)
			elif self.n == 1:
				s = mpt.Rectangle(coord,wid,width,transform=trans, fc=self.cmap((2*i+1)/(2*self.num)))

			stripes.append(s)

		return stripes

# ---------------------------------------------- TRIAXIALITY AND LODE ANGLE NAME
def htpp_plot_triaxility_lode_name(set,step,frame,num,table):
	name = ['TRIAX/LODE [']
	set = set.replace('_','\_')
	name.append('set: '  + set.upper() + ' /')
	name.append('step: ' + str(step) + ' /')
	name.append('frame: '+ str(frame))
	if num == 2:
		name.append('/ colormap: ROTATION')

	name.append(']')
	name = ' '.join(name)
	table.append(name)

	return table

# ------------------------------------------- TRIAXIALITY AND LODE ANGLE OPTIONS
def htpp_plot_triaxility_lode_option(option):
	step = '\n'.join(s for s in option if 'step=' in s).replace(",", "").replace("\n", "")[6:-1].strip().split(';')
	step = [int(s) for s in step]
	frame = '\n'.join(s for s in option if 'frame=' in s).replace(",", "").replace("\n", "")[7:-1].strip().split(';')
	frame = [int(i) for i in frame]
	elem_set = '\n'.join(s for s in option if 'elemSet=' in s).replace(",", "").replace("\n", "")[9:-1].split(';')
	num = '\n'.join(s for s in option if 'num=' in s).replace(",", "").replace("\n", "")[5:-1].split(';')
	num = [float(n) for n in num]

	return step,frame,elem_set,num

# ----------------------------------------------- TRIAXIALITY AND LODE ANGLE AUX
def htpp_plot_triaxility_lode_aux(triax_lode,rotAngle,peeq,n):
	t_elas = triax_lode[peeq == 0.0,:]
	t_plas = triax_lode[peeq != 0.0,:]

	if n == 2:
		rot_elas = rotAngle[peeq == 0.0]
		rot_plas = rotAngle[peeq != 0.0]


	fig = plt.figure(num=n)
	ax = fig.add_subplot(111)

	plt.plot([-1,1],[-1/3,1/3],'k-',lw=0.5)
	x = [-1.0, 0.0, 1.0]
	y = [2.0/3.0,sqrt(3.0)/3.0,1.0/3.0]
	f = CubicSpline(x, y)
	xnew = np.linspace(-1, 1, num=100)
	plt.plot(xnew,f(xnew),'k-',lw=0.5)
	y = [-1.0/3.0,-sqrt(3.0)/3.0,-2.0/3.0]
	f = CubicSpline(x, y)
	xnew = np.linspace(-1, 1, num=100)
	plt.plot(xnew,f(xnew),'k-',lw=0.5)

	blue = (0,0.3,0.85,1.0)
	grey = (0.75,0.75,0.75,1.0)
	black_02 = (0,0,0,0.2)
	box = dict(boxstyle='Square,pad=0.05',fc='w',ec='w')
	al = 'center'
	fnt = 9

	name = 'axial symmetry,\ncompression'
	plt.plot([-1,-1],[-0.75,0.75],'k-',lw=0.5,zorder=0)
	plt.text(-1,0,name,ha=al,va=al,ma=al,bbox=box,fontsize=fnt)

	name = 'axial symmetry,\ntension'
	plt.plot([ 1, 1],[-0.75,0.75],'k-',lw=0.5,zorder=0)
	plt.text(1,0,name,ha=al,va=al,ma=al,bbox=box,fontsize=fnt)

	name = 'plane strain,\nshear'
	plt.plot([ 0, 0],[-0.75,0.75],'k-',lw=0.5,zorder=0)
	plt.text(0,0.4,name,ha=al,va=al,ma=al, bbox=box,fontsize=fnt)

	name = 'plane\nstress'
	plt.text(0.8,-0.66,name,ha=al,va=al,ma=al,bbox=box,fontsize=fnt+1)

	lbs = ['elastic','plastic']
	if n == 1:
		pl = plt.scatter(t_plas[:,1],t_plas[:,0],s=5,color=blue, edgecolors=black_02,linewidths=0.2,zorder=200,rasterized=True)
		el = plt.scatter(t_elas[:,1],t_elas[:,0],s=5,color=grey, edgecolors=black_02,linewidths=0.2,zorder=100,rasterized=True)

		leg = ax.legend([el,pl],lbs,loc=3,frameon=False,fontsize=fnt, markerscale=3.0,handletextpad=0.1,bbox_to_anchor=(0.1,0.01))
		leg.legendHandles[0].set_edgecolor(grey)
		leg.legendHandles[1].set_edgecolor(blue)

		plt.xlim(-1.3,1.3)

	elif n == 2:
		cmapjet = mpl.cm.get_cmap('jet',12)
		pl = plt.scatter(t_plas[:,1],t_plas[:,0],s=5,c=rot_plas,cmap=cmapjet, edgecolors=black_02,linewidths=0.2,zorder=200,rasterized=True)

		tks = np.linspace(0.0,90.0,13)
		clb = plt.colorbar(ticks=tks)
		clb.solids.set_rasterized(True)
		clb.set_label(r'$\gamma$ [$^\circ$]', labelpad=-22, y=1.1, rotation=0)
		clb.set_ticklabels(['%.1f'%i for i in tks])
		plt.xlim(-1.4,1.4)

		el = plt.scatter(t_elas[:,1],t_elas[:,0],s=5,color=grey, edgecolors=black_02,linewidths=0.2,zorder=100,rasterized=True)

		cmap = plt.cm.jet
		hdls = [mpt.Rectangle((0,0),0.5,1,rasterized=True) for _ in lbs]
		hdl_map = dict(zip(hdls,                     [HandlerColormap(cmap,12,i) for i in range(2)]))
		leg1 = ax.legend(handles=hdls,labels=lbs,handler_map=hdl_map, fontsize=fnt,loc=3,frameon=False,bbox_to_anchor=(0.1,0.01))

		for text in leg1.get_texts():
			text.set_color("w")

		c = [mpt.Circle((0.5, 0.5),1.0,fc='none',ec='w',lw=2.0) for _ in lbs]
		hdl_map = {mpt.Circle:HandlerEllipse()}
		leg2 = plt.legend(c,lbs,handler_map=hdl_map,loc=3,frameon=False, fontsize=fnt,bbox_to_anchor=(0.1,0.01))
		ax.add_artist(leg1)

	for k, spine in ax.spines.items():
	    spine.set_zorder(1000)

	plt.xlabel('$\\bar{\\theta}$ [-]')
	plt.ylabel('$\eta$ [-]')
	plt.ylim(-0.75,0.75)
	plt.yticks(np.linspace(-0.75,0.75,7))

	plt.close()

	return fig

# ------------------------------------------------------------------------------
# --------------------------------------------------- TRIAXIALITY AND LODE ANGLE
# ------------------------------------------------------------------------------
def htpp_plot_triaxility_lode(odb_name,option,pdf,size,table):
	plt.rc('text', usetex=True)
	plt.rc('font', family='serif',size=14)

	dir = 'htpp_output/' + odb_name + '/'

	step,frame,elem_set,num = htpp_plot_triaxility_lode_option(option)

	for set in elem_set:
		for l in step:
			for f in frame:
				for n in num:
					strings = ['triax_lode',set.lower(),'s'+str(l),'f'+str(f)]
					fname = dir + '_'.join(strings) + '.dat'
					triax_lode = np.loadtxt(fname,skiprows=1, delimiter=',')

					strings = ['peeq',set.lower(),'s'+str(l),'f'+str(f)]
					fname = dir + '_'.join(strings) + '.dat'
					peeq = np.loadtxt(fname)

					rotAngle = None
					if n == 2:
						strings = ['rotation',set.lower(),'s'+str(l),'f'+str(f)]
						fname = '_'.join(strings)
						rotAngle = np.loadtxt(dir + fname + '.dat')

					fig = htpp_plot_triaxility_lode_aux(triax_lode,rotAngle, peeq,n)

					box = mpl.transforms.Bbox(size[int(n)-1])
					pdf.savefig(fig,dpi=200,bbox_inches=box)

					table = htpp_plot_triaxility_lode_name(set,l,f,n,table)

	return pdf,table
# ------------------------------------------------------------------------------
