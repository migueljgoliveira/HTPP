# -----------------------------------------------------------------------------
# ------------------------------------------------------------- IMPORT PACKAGES
from odbAccess import *
from abaqusConstants import *
import os
import shutil
import sys
import math
from textRepr import prettyPrint

# -----------------------------------------------------------------------------
# -------------------------------------------------------------------- ADD PATH
sys.path.insert(0, os.getcwd() + '/htpp_data')

# -----------------------------------------------------------------------------
# ---------------------------------------------------------------- IMPORT FILES
from htpp_data_strain import htpp_data_strain
from htpp_data_stress import htpp_data_stress
from htpp_data_peeq import htpp_data_peeq
from htpp_data_rotation import htpp_data_rotation
from htpp_data_triaxiality_lode import htpp_data_triaxiality_lode
from htpp_data_schmitt import htpp_data_schmitt
from htpp_data_force import htpp_data_force
from htpp_data_evol import htpp_data_evol

# -----------------------------------------------------------------------------
# ------------------------------------------------------------------------ MAIN
# -----------------------------------------------------------------------------
def htpp_data():
    # ----------------------------------------------------- FIND SETTINGS FILES
    path = os.getcwd()[:-4]
    files = []
    for file in os.listdir(path):
        if file.endswith('.htpp'):
            files.append(file)

    for file in files:
        # ----------------------------------------- OPEN AND READ SETTINGS FILE
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
                odbFile = line[-1][6:-2]
                name = odbFile
            elif '*DATA' in line[0].upper():
                data_begin = i
            elif '*ENDDATA' in line[0].upper():
                data_end = i
            i += 1

        # ------------------------------------------------ EXTRACT DATA OPTIONS
        data_options = data_settings[data_begin:data_end]
        all_data = []
        for line in data_options:
            if '**STRAIN' in line[0].upper():
                all_data.append(line)
            elif '**STRESS' in line[0].upper():
                all_data.append(line)
            elif '**ROTATION' in line[0].upper():
                all_data.append(line)
            elif '**PEEQ' in line[0].upper():
                all_data.append(line)
            elif '**TRIAXIALITYLODE' in line[0].upper():
                all_data.append(line)
            elif '**SCHMITT' in line[0].upper():
                all_data.append(line)
            elif '**FORCE' in line[0].upper():
                all_data.append(line)
            elif '**EVOL' in line[0].upper():
                all_data.append(line)

        # ----------------------------------- OPEN ODB AND CREATE OUTPUT FOLDER
        if len(all_data) > 0:
            try:
                path = os.getcwd()[:-4]
                odb = openOdb(path + name + '.odb', readOnly=False)
            except Exception as e:
                print('Error: openOdb ' + name +'.odb')
                return

            path = os.getcwd()
            if os.path.isdir(path + '/htpp_output/' + name):
                shutil.rmtree(path + '/htpp_output/' + name)
            os.mkdir(path + '/htpp_output/' + name)
        else:
            return

        ioi = odb.rootAssembly
        sName = odb.sectionCategories.keys()[-1]
        section = odb.sectionCategories[sName].sectionPoints

        # ----------------------------------------------- CALL DATA SUBROUTINES
        if len(all_data) > 0:
            tlen = 20.0
            st = int(round(tlen / len(all_data)))
            stri = "> HTPP DATA  "
            sys.stdout.write(stri+"[%s]    %d%s  (%s)"%(" "*int(tlen), 0,'%',name))
            sys.stdout.flush()
            n = 1
            for option in all_data:
                opt = option[0]
                if opt == '**STRAIN':
                    htpp_data_strain(odb,ioi,option,section,name)
                elif opt == '**STRESS':
                    htpp_data_stress(odb,ioi,option,section,name)
                elif opt == '**ROTATION':
                    htpp_data_rotation(odb,ioi,option,section,name)
                elif opt == '**PEEQ':
                    htpp_data_peeq(odb,ioi,option,section,name)
                elif opt == '**TRIAXIALITYLODE':
                    htpp_data_triaxiality_lode(odb,ioi,option,section,name)
                elif opt == '**SCHMITT':
                    htpp_data_schmitt(odb,ioi,option,section,name)
                elif opt == '**FORCE':
                    htpp_data_force(odb,ioi,option,section,name)
                elif opt == '**EVOL':
                    htpp_data_evol(odb,ioi,option,section,name)

                per = 100.0 * float(st * n) / float(tlen)
                bars = st * n
                form = "[%s%s] ~ %d%s  (%s)"
                if per >= 100.0:
                    per = 100.0
                    bars = int(tlen)
                    form = "[%s%s]  %d%s  (%s)"
                sys.stdout.write("\r"+stri+form %("-"*bars," "*(int(tlen)-bars),per,'%',name))
                sys.stdout.flush()
                n += 1
            sys.stdout.write("\r"+stri+"[%s]  %d%s  (%s)\n"%("-"*int(tlen),100,'%',name))

        # -------------------------------------------------- SAVE ODB AND CLOSE
        odb.save()
        odb.close()

# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
if __name__ == '__main__':
    htpp_data()