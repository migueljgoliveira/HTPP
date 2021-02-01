# ------------------------------------------------------------------------------
# -------------------------------------------------------------- IMPORT PACKAGES
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
from math import floor, ceil

# ------------------------------------------------------------- YIELD LOCUS NAME
def htpp_plot_yieldlocus_name(yldname,shear,table):
	name = ['YIELD LOCUS [']
	name.append('yield criteria: ' + yldname.upper() + ' /')
	shear = [str(s) for s in shear]
	shear = ', '.join(shear)
	name.append('shear: (' + shear + ')')
	name.append(']')
	name = ' '.join(name)

	table.append(name)

	return table

# ---------------------------------------------------------  YIELD LOCUS OPTIONS
def htpp_plot_yieldlocus_option(option):
	yldname = '\n'.join(s for s in option if 'yldname=' in s).replace(",", "").replace("\n", "")[9:-1].strip()
	shear = '\n'.join(s for s in option if 'shear=' in s).replace(",", "").replace("\n", "")[7:-1].split(';')
	shear = [float(s) for s in shear]

	return yldname,shear

# ------------------------------------------------------------------------------
# ------------------------------------------------------------------ YIELD LOCUS
# ------------------------------------------------------------------------------
def htpp_plot_yieldlocus(odb_name,option,pdf,size,table):
	plt.rc('text', usetex=True)
	plt.rc('font', family='serif',size=14)

	dir = 'htpp_output/' + odb_name + '/'

	yldname,shear = htpp_plot_yieldlocus_option(option)

	fig = plt.figure(num=1)
	ax = fig.add_subplot(111)

	al = 'center'
	fnt = 9

	for s12 in shear:
		strings = ['yieldlocus',yldname,str(s12)]
		fname = '_'.join(strings)
		yldlocus = np.loadtxt(dir + fname + '.dat',skiprows=1,delimiter=',')

		plt.plot([0,0],[-1.5,1.5],'k-',lw=0.5,zorder=0)
		plt.plot([-1.5,1.5],[0,0],'k-',lw=0.5,zorder=0)

		plt.plot(yldlocus[:,2],yldlocus[:,3],'-',color=(0,0.3,0.85,1.0), lw=1.5,zorder=100,rasterized=True)

		ax.set_aspect('equal')

		pts = len(yldlocus[:,2])
		idx = int(round(pts/8.0)*5)

		props = dict(boxstyle='Square,pad=0.0',fc='w',ec='none')
		plt.text(yldlocus[idx,2],yldlocus[idx,3],str(s12),ha=al,va=al, fontsize=fnt,bbox=props,zorder=1000)

		plt.xlabel('$\sigma_{xx}/\sigma_0$')
		plt.ylabel('$\sigma_{yy}/\sigma_0$')
		plt.ylim(-1.5,1.5)
		plt.xlim(-1.5,1.5)

	plt.close()

	box = mpl.transforms.Bbox(size[0])
	pdf.savefig(fig,dpi=200,bbox_inches=box)

	table = htpp_plot_yieldlocus_name(yldname,shear,table)

	return pdf,table
# ------------------------------------------------------------------------------
