# ------------------------------------------------------------------------------
# -------------------------------------------------------------- IMPORT PACKAGES
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.patches as mpt
from matplotlib.legend_handler import HandlerBase, HandlerPatch
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
from math import floor, ceil, pi, tan, sin, cos
from scipy.interpolate import BSpline, splrep

# -------------------------------------------------------------- HANDLER ELLIPSE
class HandlerEllipse(HandlerPatch):
	def create_artists(self,legend,orig_handle,xdescent,ydescent,width,  height,fontsize,trans):
		x, y = 23.5, 3.25
		wid = 15.95
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
		width = 12.0
		x,y = 17.5, -2.8
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

# ------------------------------------------------------------. STRAIN PLOT NAME
def htpp_plot_strain_name(set,step,frame,num,table):
	name = ['STRAIN [']
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

# --------------------------------------------------------------- STRAIN OPTIONS
def htpp_plot_strain_option(option):
	step = '\n'.join(s for s in option if 'step=' in s).replace(",", "").replace("\n", "")[6:-1].strip().split(';')
	step = [int(s) for s in step]
	frame = '\n'.join(s for s in option if 'frame=' in s).replace(",", "").replace("\n", "")[7:-1].strip().split(';')
	frame = [int(i) for i in frame]
	elem_set = '\n'.join(s for s in option if 'elemSet=' in s).replace(",", "").replace("\n", "")[9:-1].split(';')
	lims = '\n'.join(s for s in option if 'lims=' in s).replace("\n" , "")[6:-1].split(';')
	tmp = []
	if lims[0] != '':
		for lim in lims:
			l = lim[1:-1].split(',')
			tmp.append([float(l[0]),float(l[1])])
	lims = tmp
	txt = '\n'.join(s for s in option if 'text=' in s).replace("\n","")[6:-1].split(',')
	if txt[0] == '':
		txt = []
	num = '\n'.join(s for s in option if 'num=' in s).replace(",", "").replace("\n", "")[5:-1].split(';')
	num = [float(n) for n in num]

	return step,frame,elem_set,lims,txt,num

# ------------------------------------------------------------------- STRAIN AUX
def htpp_plot_strain_aux(strain,peeq,rot,lims,txt,n,odb_name):

	s_elas = strain[peeq == 0.0,:]
	s_plas = strain[peeq != 0.0,:]

	if n == 2:
		p_elas = peeq[peeq == 0.0]
		p_plas = peeq[peeq != 0.0]
	elif n ==3:
		rot_elas = rot[peeq == 0.0]
		rot_plas = rot[peeq != 0.0]

	if lims:
		xlims,ylims = lims[0],lims[-1]
	else:
		ylims = [0.0,ceil((max(strain[:,0])*10))/10]
		if abs(min(strain[:,1])) > abs(max(strain[:,1])):
			lim_X = floor(min(strain[:,1])*10)/10
			xlims = [lim_X,-lim_X]
		else:
			lim_X = ceil(max(strain[:,1])*10)/10
			xlims = [-lim_X,-lim_X]

	tmp    = min(ylims[1],abs(xlims[0]))
	shear  = [[0,-tmp],[0,tmp]]
	tens   = [[0,-tmp],[0,tmp*2.0]]
	comp   = [[0,-tmp],[0,tmp/2.0]]

	tmpBi  = min(ylims[1],xlims[1])
	eqBiax =[[0,tmpBi],[0,tmpBi]]

	fig = plt.figure(num=n,dpi=300)
	ax = fig.add_subplot(111)

	blue = (0,0.3,0.85,1.0)
	grey = (0.75,0.75,0.75,1.0)
	black_02 = (0,0,0,0.2)
	al = 'center'
	fnt = 14
	rast = True
	siz = 2

	box = dict(boxstyle='Square,pad=0.05',fc='w',ec='w')
	p = [0.8,0.85,0.85,0.95,0.6]
	if txt:
		p = [float(t) for t in txt]

	name = 'uniaxial\ncompression'
	plt.plot(comp[0],comp[1],'k-',lw=0.5,zorder=0)
	# plt.text(-p[0]*tmp,p[0]*tmp/2,name,ha=al,va=al,ma=al,fontsize=fnt,bbox=box)

	name = 'shear'
	plt.plot(shear[0],shear[1],'k-',lw=0.5,zorder=5)
	# plt.text(-tmp*p[1],tmp*p[1],name,ha=al,va=al,fontsize=fnt,bbox=box,zorder=9)

	name = 'uniaxial\ntension'
	plt.plot(tens[0],tens[1],'k-',lw=0.5,zorder=0)
	# plt.text(-0.15,2*tmp*p[2],name,ha=al,va=al,ma=al,fontsize=fnt,bbox=box)

	name = 'plane strain\ntension'
	plt.plot([0,0],ylims,'k-',lw=0.5,zorder=0)
	# plt.text(0,ylims[1]*p[3],name,ha=al,va=al,ma=al,fontsize=fnt,bbox=box)

	name = 'equibiaxial\ntension'
	plt.plot(eqBiax[0],eqBiax[1],'k-',lw=0.5,zorder=0)
	# plt.text(p[4]*tmpBi,p[4]*tmpBi,name,ha=al,va=al,ma=al,fontsize=fnt,bbox=box)

	lbs = ['elastic','plastic']
	if n == 1:
		pl = plt.scatter(s_plas[:,1],s_plas[:,0],s=siz,color=blue, edgecolors=black_02,linewidths=0.1,zorder=100,rasterized=rast)
		el = plt.scatter(s_elas[:,1],s_elas[:,0],s=siz-1,color=grey, edgecolors='none',linewidths=0.2,zorder=200,rasterized=rast)

		leg = ax.legend([el,pl],lbs,loc=4,frameon=False, fontsize=fnt,markerscale=3.0,handletextpad=0.1)
		leg.legendHandles[0].set_edgecolor(grey)
		leg.legendHandles[1].set_edgecolor(blue)

	elif n == 2:
		cjet = mpl.cm.get_cmap('jet', 12)
		pl = plt.scatter(s_plas[:,1],s_plas[:,0],s=siz,c=p_plas,cmap=cjet, edgecolors=black_02,linewidths=0.1,zorder=100,rasterized=rast)

		sm = plt.cm.ScalarMappable(cmap=cjet, norm=plt.Normalize(vmin=0,vmax=max(peeq)))
		sm._A = []
		tks = np.linspace(0.0,max(peeq),13)
		clb = plt.colorbar(sm,ticks=tks)
		clb.solids.set_rasterized(True)
		clb.set_label(r'$\bar \epsilon ^\mathrm{p}$ [-]',labelpad=-23,y=1.11, rotation=0)
		clb.set_ticklabels(['%.2f'%round(i,2) for i in tks])

		el = plt.scatter(s_elas[:,1],s_elas[:,0],s=0.5,color=grey, edgecolors='none',linewidths=0.2,zorder=200,rasterized=rast)

		# cmap = plt.cm.jet
		# hdls = [mpt.Rectangle((0,0),0.5,1,rasterized=True) for _ in lbs]
		# hdl_map = dict(zip(hdls,                     [HandlerColormap(cmap,12,i) for i in range(2)]))
		# leg1 = ax.legend(handles=hdls,labels=lbs,handler_map=hdl_map, fontsize=fnt,loc=4,frameon=False)
		#
		# for text in leg1.get_texts():
		# 	text.set_color("w")
		#
		# c = [mpt.Circle((0.5, 0.5),1.0,fc='none',ec='w',lw=4.0) for _ in lbs]
		# hdl_map = {mpt.Circle:HandlerEllipse()}
		# leg2 = plt.legend(c,lbs,handler_map=hdl_map,loc=4,frameon=False, fontsize=fnt)
		# ax.add_artist(leg1)

	elif n == 3:
		cjet = mpl.cm.get_cmap('jet', 12)
		pl = plt.scatter(s_plas[:,1],s_plas[:,0],s=siz,c=rot_plas,cmap=cjet, edgecolors=black_02,linewidths=0.1,zorder=200,rasterized=rast, norm=mpl.colors.Normalize(vmin=0.0,vmax=90.0))

		tks = np.linspace(0.0,90.0,13)
		clb = plt.colorbar(ticks=tks)
		clb.solids.set_rasterized(rast)
		clb.set_label(r'$\gamma$ [$^\circ$]', labelpad=-25, y=1.11, rotation=0)
		clb.set_ticklabels(['%.1f'%i for i in tks])

		el = plt.scatter(s_elas[:,1],s_elas[:,0],s=0.5,color=grey, edgecolors='none',linewidths=0.2,zorder=200,rasterized=rast)

		cmap = plt.cm.jet
		hdls = [mpt.Rectangle((0,0),0.5,1,rasterized=True) for _ in lbs]
		hdl_map = dict(zip(hdls,                     [HandlerColormap(cmap,12,i) for i in range(2)]))
		leg1 = ax.legend(handles=hdls,labels=lbs,handler_map=hdl_map, fontsize=fnt,loc=4,frameon=False)

		for text in leg1.get_texts():
			text.set_color("w")

		c = [mpt.Circle((0.5, 0.5),1.0,fc='none',ec='w',lw=4.0) for _ in lbs]
		hdl_map = {mpt.Circle:HandlerEllipse()}
		leg2 = plt.legend(c,lbs,handler_map=hdl_map,loc=4,frameon=False, fontsize=fnt)
		ax.add_artist(leg1)


	nCu,nAl,nDp = 0.1,0.227,0.194
	d,x,t1,a = 0.865,-0.0881,0.06,65.0/180.0*pi
	t = nCu+0.03
	xCu  = [0,t1,t]
	yCu = [nCu, tan(a)*t1, t]
	xx = np.arange(0,t,0.0001)
	t, c, k = splrep(xCu, yCu, s=0, k=2)
	yy = BSpline(t, c, k)

	mat = odb_name.split('_')
	mat = mat[-1]

	fnt = 14
	box = dict(boxstyle='Square,pad=0.1',fc='w',ec='w')

	if mat == 'Cu':
		plt.plot([0,x],[nCu,-d*x+nCu],c='k',lw=0.75,zorder=50)
		plt.plot(xx,yy,c='k',zorder=50,lw=0.75)
	elif mat == 'DP600':
		x = -0.1709
		plt.plot([0,x],[nDp,-d*x+nDp],c='k',zorder=50,lw=0.75)
		r1 = nDp/nCu
		plt.plot(xx*r1,yy(xx)*r1,c='k',zorder=50,lw=0.75)
		# plt.text(0.045,0.22,'FLC',ha=al,va=al,ma=al,fontsize=fnt,bbox=box, zorder=300)
	elif mat == 'AA2090-T3':
		x = -0.2;
		Al1 = plt.plot([0,x],[nAl,-d*x+nAl],c='k',zorder=50,lw=0.75)
		r2 = nAl/nCu
		plt.plot(xx*r2,yy(xx)*r2,c='k',zorder=50,lw=0.75)
		# plt.text(0.045,0.22,'FLC',ha=al,va=al,ma=al,fontsize=fnt,bbox=box, zorder=300)

	for k, spine in ax.spines.items():
		spine.set_zorder(1000)

	plt.xlabel('$\epsilon_2$ [-]')
	plt.ylabel('$\epsilon_1$ [-]')
	plt.ylim(ylims[0],ylims[1])
	plt.xlim(xlims[0],xlims[1])
	plt.yticks(np.arange(0.0,ylims[1]+0.1,0.1))
	plt.xticks(np.arange(xlims[0],xlims[1]+0.05,0.05))

	plt.close()

	return fig

# ------------------------------------------------------------------------------
# ----------------------------------------------------------------------- STRAIN
# ------------------------------------------------------------------------------
def htpp_plot_strain(odb_name,option,pdf,size,table):
	plt.rc('text', usetex=True)
	plt.rc('font', family='serif',size=18)

	dir = 'htpp_output/' + odb_name + '/'

	step,frame,elem_set,lims,txt,num = htpp_plot_strain_option(option)

	for set in elem_set:
		for l in step:
			for f in frame:
				for n in num:
					strings = ['strain',set.lower(),'s'+str(l),'f'+str(f)]
					fname = dir + '_'.join(strings) + '.dat'
					strain = np.loadtxt(fname,skiprows=1,delimiter=',')

					strings = ['peeq',set.lower(),'s'+str(l),'f'+str(f)]
					fname = dir + '_'.join(strings) + '.dat'
					peeq = np.loadtxt(fname)

					strings = ['rotation',set.lower(),'s'+str(l),'f'+str(f)]
					fname = dir + '_'.join(strings) + '.dat'
					rot = np.loadtxt(fname)

					fig = htpp_plot_strain_aux(strain,peeq,rot,lims,txt,n, odb_name)

					box = mpl.transforms.Bbox(size[int(n)-1])
					pdf.savefig(fig,dpi=500,bbox_inches=box)

					table = htpp_plot_strain_name(set,l,f,n,table)

	return pdf,table
# ------------------------------------------------------------------------------
