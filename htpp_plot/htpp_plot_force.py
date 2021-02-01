# ------------------------------------------------------------------------------
# -------------------------------------------------------------- IMPORT PACKAGES
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
from math import floor, ceil

# -------------------------------------------------------------- FORCE PLOT NAME
def htpp_plot_force_name(node_set,direc,step,table):
	name = ['FORCE [']
	sets = [s.replace('_','\_') for s in node_set]
	sets = ','.join(sets)
	direc = [str(s) for s in direc]
	dirs = ','.join(direc)
	name.append('set: '  + sets.upper() + ' /')
	name.append('dir: '  + dirs + ' /')
	name.append('step: ' + str(step))
	name.append(']')
	name = ' '.join(name)

	table.append(name)

	return table

# ---------------------------------------------------------------- FORCE OPTIONS
def htpp_plot_force_option(option):
	step = '\n'.join(s for s in option if 'step=' in s).replace(",", "").replace("\n", "")[6:-1].strip().split(';')
	step = [int(s) for s in step]
	node_set = '\n'.join(s for s in option if 'nodeSet=' in s).replace(",", "").replace("\n", "")[9:-1].split(';')
	direc = '\n'.join(s for s in option if 'direction=' in s).replace(",", "").replace("\n", "")[11:-1].strip().split(';')
	direc = [int(i) for i in direc]
	lb = '\n'.join(s for s in option if 'label=' in s).replace(",", "").replace("\n", "")[7:-1].strip().split(';')

	return step,node_set,direc,lb

# -------------------------------------------------------------------- FORCE AUX
def htpp_plot_force_aux(data,direc,lb):
	blue = (0,0.3,0.85,1.0)
	green = (0.0,0.6,0.0,1.0)
	red = (0.75,0.15,0.15,1.0)
	orange = (0.78,0.43,0.02,1.0)
	cols = [blue,green,red,orange]
	grey = (0.65,0.65,0.65,1.0)
	black_02 = (0,0,0,0.2)
	al = 'center'
	fnt = 9

	fig = plt.figure()
	ax = fig.add_subplot(111)
	plots = []
	i = 0
	for force_disp in data:
		force = force_disp[:,1]/1000
		disp = force_disp[:,0]
		p, = plt.plot(disp,force,'-o',lw=1.25,color=cols[i],zorder=200,ms=3, mfc='w',mec=cols[i])

		plots.append(p)
		i+=1

	for k, spine in ax.spines.items():
		spine.set_zorder(1000)


	lbs = []
	for i in range(len(plots)):
		lbs.append('$O'+str(lb[i])+'$')

	plt.legend(plots,lbs,frameon=False,loc=4)

	max_disp,max_force = [],[]
	min_disp,min_force = [],[]
	for x in data:
		max_disp.append(max(x[:,0]))
		max_force.append(max(x[:,1]))
		min_disp.append(min(x[:,0]))
		min_force.append(min(x[:,1]))

	if max(max_disp) % 1 >= 0.5:
		xMax = round(max(max_disp))
	else:
		xMax = round(max(max_disp)) + 0.5
	xlims = [floor(min(min_disp)),xMax]
	ylims = [floor(min(min_force)/1000),ceil(max(max_force)/1000)]

	plt.xlabel('Displacement [mm]')
	plt.ylabel('Force [kN]')
	plt.ylim(ylims[0],ylims[1])
	plt.xlim(xlims[0],xlims[1])

	plt.close()

	return fig

# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------ FORCE
# ------------------------------------------------------------------------------
def htpp_plot_force(odb_name,option,pdf,size,table):
	plt.rc('text', usetex=True)
	plt.rc('font', family='serif',size=14)

	dir = 'htpp_output/' + odb_name + '/'

	step,node_set,direc,lb = htpp_plot_force_option(option)

	for l in step:
		j = 0
		data = []
		for set in node_set:
			strings = ['force',set.lower(),'s'+str(l),'d'+str(direc[j])]
			fname = dir + '_'.join(strings) + '.dat'
			force_disp = np.loadtxt(fname,skiprows=1,delimiter=',')
			data.append(force_disp)
			j+=1

		fig = htpp_plot_force_aux(data,direc,lb)

		box = mpl.transforms.Bbox(size[0])
		pdf.savefig(fig,dpi=200,bbox_inches=box)

		table = htpp_plot_force_name(node_set,direc,l,table)

	return pdf,table
# ------------------------------------------------------------------------------
