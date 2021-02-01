# ------------------------------------------------------------------------------
# -------------------------------------------------------------- IMPORT PACKAGES
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
from math import floor, ceil

# -------------------------------------------------------------- ANISOTROPY NAME
def htpp_plot_anisotropy_name(yldname,num,table):
	if num == 1:
		name = ['ANISOTROPY - YIELD STRESS [']
	elif num == 2:
		name = ['ANISOTROPY - R VALUES [']
	name.append('yield criteria: '  + yldname.upper())
	name.append(']')
	name = ' '.join(name)

	table.append(name)

	return table

# ----------------------------------------------------------- ANISOTROPY OPTIONS
def htpp_plot_anisotropy_option(option):
	yldname = '\n'.join(s for s in option if 'yldname=' in s).replace(",", "").replace("\n", "")[9:-1].strip()

	return yldname

# --------------------------------------------------------------- ANISOTROPY AUX
def htpp_plot_anisotropy_aux(yldlocus,n):

	fig = plt.figure(num=n)
	ax = fig.add_subplot(111)

	pts = len(yldlocus[:,0])
	angles = np.linspace(0.0,90.0,pts)

	if n == 1:
		yLims = [floor(min(yldlocus[:,1])*10)/10.0,  ceil(max(yldlocus[:,1])*10)/10.0]
		plt.plot(angles,yldlocus[:,1],'-',color=(0,0.3,0.85,1.0), lw=1.5,zorder=100,rasterized=True)
		plt.ylabel('Normalized yield stress')
	elif n == 2:
		yLims = [floor(min(yldlocus[:,2])*10)/10.0,  ceil(max(yldlocus[:,2])*10)/10.0]
		plt.plot(angles,yldlocus[:,2],'-',color=(0,0.3,0.85,1.0), lw=1.5,zorder=100,rasterized=True)
		plt.ylabel('r value')

	plt.ylim(yLims[0],yLims[1])
	plt.xlabel('Angle from RD [$^\circ$]')
	plt.xlim(0.0,90.0)
	plt.xticks(np.linspace(0,90,7))

	plt.close()

	return fig

# ------------------------------------------------------------------------------
# ------------------------------------------------------------------- ANISOTROPY
# ------------------------------------------------------------------------------
def htpp_plot_anisotropy(odb_name,option,pdf,size,table):
	plt.rc('text', usetex=True)
	plt.rc('font', family='serif',size=14)

	dir = 'htpp_output/' + odb_name + '/'

	yldname = htpp_plot_anisotropy_option(option)

	strings = ['yieldaniso',yldname]
	fname = dir + '_'.join(strings)+ '.dat'
	yldaniso = np.loadtxt(fname,skiprows=1,delimiter=',')

	for n in range(2):
		fig = htpp_plot_anisotropy_aux(yldaniso,n+1)
		box = mpl.transforms.Bbox(size[0])
		pdf.savefig(fig,dpi=200,bbox_inches=box)

		table = htpp_plot_anisotropy_name(yldname,n+1,table)

	return pdf,table
# ------------------------------------------------------------------------------
