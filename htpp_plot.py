# ------------------------------------------------------------------------------
# -------------------------------------------------------------- IMPORT PACKAGES
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
import os
import sys
import math

# ------------------------------------------------------------------------------
# --------------------------------------------------------------------- ADD PATH
sys.path.insert(0, os.getcwd() + '/htpp_plot')
sys.path.insert(0, os.getcwd() + '/htpp_output')
sys.path.insert(0, os.getcwd() + '/htpp_graphic')

# ------------------------------------------------------------------------------
# ----------------------------------------------------------------- IMPORT FILES
from htpp_plot_strain import htpp_plot_strain
from htpp_plot_stress import htpp_plot_stress
from htpp_plot_rotation import htpp_plot_rotation
from htpp_plot_triaxility_lode import htpp_plot_triaxility_lode
from htpp_plot_yieldlocus import htpp_plot_yieldlocus
from htpp_plot_anisotropy import htpp_plot_anisotropy
from htpp_plot_force import htpp_plot_force

# ------------------------------------------------------------------------------
# ------------------------------------------------------------ TABLE OF CONTENTS
# ------------------------------------------------------------------------------
def http_plot_pdf(pdf,table):
	cte = 0.3
	pages = len(table)
	ysize = pages*cte
	fig = plt.figure(figsize=(6.1,ysize))
	ax = fig.add_subplot(111)

	plt.ylim(0,pages+2)
	plt.ylim(0,1.0)

	title = 'TABLE OF CONTENTS'
	plt.text(-0.1,pages+1.5,title,size=12,ha='left',va='center')

	for i in range(pages):
		tmp = str(i+1)+' - '+table[i]
		f = (pages-0.7) - i*1.0
		plt.text(-0.05,f,tmp,size=9,ha='left',va='center')

	ax.set_ylim(0,pages+2)

	ax.axis("off")

	pdf.savefig(fig)
	plt.close()

	return pdf

#
# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------- MAIN
# ------------------------------------------------------------------------------
def htpp_plot():
	# ------------------------------------------------------ FIND SETTINGS FILES
	path = os.getcwd()[:-4]
	files = []
	for file in os.listdir(path):
		if file.endswith('.htpp'):
			files.append(file)

	for file in files:
		# ------------------------------------------ OPEN AND READ SETTINGS FILE
		data_settings = []
		try:
			path = os.getcwd()[:-4]
			with open(path + file, 'r') as f:
				for line in f:
					if len(line.split()) > 0:
						if line.split()[0][0:2][0:2] == '\\*':
							continue
						else:
							data_settings.append(line.split(", "))
		except Exception as e:
			print('Error: ' + file)
			return

		i = 1
		for line in data_settings:
			if '*ODB' in line[0].upper():
				odb_file = line[-1][6:-2]
				name = odb_file
			elif '*PLOT' in line[0].upper():
				plot_begin = i
			elif '*ENDPLOT' in line[0].upper():
				plot_end = i
			i+=1

		dir = 'htpp_output/' + name + '/'

		# ------------------------------------------------- EXTRACT DATA OPTIONS
		data_options = data_settings[plot_begin:plot_end]
		all_data = []
		for line in data_options:
			if '**STRAIN' in line[0].upper():
				all_data.append(line)
			elif '**STRESS' in line[0].upper():
				all_data.append(line)
			elif '**ROTATION' in line[0].upper():
				all_data.append(line)
			elif '**TRIAXIALITYLODE' in line[0].upper():
				all_data.append(line)
			elif '**YIELDLOCUS' in line[0].upper():
				all_data.append(line)
			elif '**ANISOTROPY' in line[0].upper():
				all_data.append(line)
			elif '**FORCE' in line[0].upper():
				all_data.append(line)

		size = [[[-0.1,-0.2],[6.0,4.6]],[[0.05,-0.1],[5.725,4.675]],[[0.05,-0.1],[5.725,4.675]]]

		# ------------------------------------------------ CALL DATA SUBROUTINES
		if len(all_data) > 0:
			pdf = PdfPages(dir + name +'.pdf')
			table = []
			tlen = 20.0
			st = int(round(tlen/len(all_data)))
			stri = "> HTPP PLOT  "
			sys.stdout.write(stri+"[%s]    %d%s  (%s)"%(" "*int(tlen), 0,'%',name))
			sys.stdout.flush()
			n = 1
			for option in all_data:
				opt = option[0]
				if opt == '**STRAIN':
					pdf,table = htpp_plot_strain(name,option,pdf,size,table)
				elif opt == '**STRESS':
					pdf,table = htpp_plot_stress(name,option,pdf,size,table)
				elif opt == '**ROTATION':
					pdf,table = htpp_plot_rotation(name,option,pdf,size,table)
				elif opt == '**TRIAXIALITYLODE':
					pdf,table= htpp_plot_triaxility_lode(name,option,pdf,size, table)
				elif opt == '**YIELDLOCUS':
					pdf,table = htpp_plot_yieldlocus(name,option,pdf,size,table)
				elif opt == '**ANISOTROPY':
					pdf,table = htpp_plot_anisotropy(name,option,pdf,size,table)
				elif opt == '**FORCE':
					pdf,table = htpp_plot_force(name,option,pdf,size,table)

				per = 100.0*float(st*n)/float(tlen)
				bars = st*n
				form = "[%s%s] ~ %d%s  (%s)"
				if per >= 100.0:
					per = 100.0
					bars = int(tlen)
					form = "[%s%s]  %d%s  (%s)"
				sys.stdout.write("\r"+stri+form % ("-"*bars," "*(int(tlen)-bars),per,'%',name))
				sys.stdout.flush()
				n+=1
			sys.stdout.write("\r"+stri+"[%s]  %d%s  (%s)\n" % ("-"*int(tlen),100,'%',name))

			pdf = http_plot_pdf(pdf,table)

			d = pdf.infodict()
			d['Title'] = name
			d['Author'] = 'M.G. Oliveira'
			d['Creator'] = 'HTPP - Heterogeneous Tests Post-Processing'
			d['Producer'] = 'Python'

			pdf.close()

# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
if __name__ == '__main__':
	htpp_plot()
# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
