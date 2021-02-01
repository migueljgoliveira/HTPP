# ------------------------------------------------------------------------------
# -------------------------------------------------------------- IMPORT PACKAGES
import os
import shutil
import sys
import math
import numpy as np

# ------------------------------------------------------------------------------
# --------------------------------------------------------------------- ADD PATH
sys.path.insert(0, os.getcwd() + '/htpp_yfunc')
sys.path.insert(0, os.getcwd() + '/htpp_yfunc/htpp_yfunc_criteria')

# ------------------------------------------------------------------------------
# ----------------------------------------------------------------- IMPORT FILES
from htpp_yfunc_yieldlocus import htpp_yfunc_yieldlocus
from htpp_yfunc_anisotropy import htpp_yfunc_anisotropy

# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------- MAIN
# ------------------------------------------------------------------------------
def htpp_yfunc():
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
			elif '*YFUNC' in line[0].upper():
				data_begin = i
			elif '*ENDYFUNC' in line[0].upper():
				data_end = i
			i+=1
		# ------------------------------------------------- EXTRACT DATA OPTIONS
		data_options = data_settings[data_begin:data_end]
		all_data = []
		for line in data_options:
			if '**YIELDLOCUS' in line[0].upper():
				all_data.append(line)
			elif '**ANISOTROPY' in line[0].upper():
				all_data.append(line)

		# ------------------------------------------------ CALL DATA SUBROUTINES
		if len(all_data) > 0:
			tlen = 20.0
			st = int(round(tlen/len(all_data)))
			stri = "> HTPP YFUNC "
			sys.stdout.write(stri+"[%s]    %d%s  (%s)"%(" "*int(tlen), 0,'%',name))
			sys.stdout.flush()
			n = 1
			for option in all_data:
				opt = option[0]
				if opt == '**YIELDLOCUS':
					htpp_yfunc_yieldlocus(option,name)
				elif opt == '**ANISOTROPY':
					htpp_yfunc_anisotropy(option,name)

				per = 100.0*float(st*n)/float(tlen)
				bars = st*n
				form = "[%s%s] ~ %d%s  (%s)"
				if per >= 100.0:
					per = 100.0
					bars = int(tlen)
					form = "[%s%s]  %d%s  (%s)"
				sys.stdout.write("\r"+stri+form %("-"*bars," "*(int(tlen)-bars),per,'%',name))
				sys.stdout.flush()
				n+=1

			sys.stdout.write("\r"+stri+"[%s]  %d%s  (%s)\n"%("-"*int(tlen), 100,'%',name))

# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
if __name__ == '__main__':
	htpp_yfunc()
# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
