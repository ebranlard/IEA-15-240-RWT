""" 

Extra RNA from linearization with massless tower, rigid structure, free platform DOF


TO AUTOMATIZE:
 - FST file
     - TMax=0
     - Linearize=True, CalcSteady=False, LinTime=0, NLinTimes=1, LinOutputs=1, LinInputs=2
 - ED file: 
      - Set Ptfm DOF to True, rest to false
      - Set to 0: PtfmMass PtfmRIner PtfmPIner PtfmYIner
      - Maybe: set TowerBsHt=0 PtfmRefzt=0
      - Add to ElastoDyn output list: PtfmTAxt PtfmTAyt PtfmTAzt PtfmRAxt PtfmRAyt PtfmRAzt
 - Set tower massden to 0 in tower file
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from numpy.linalg import inv
# Local 
import welib.weio as weio
from welib.fast.linmodel import matToSIunits
from welib.yams.utils import identifyRigidBodyMM, translateInertiaMatrixFromCOG

np.set_printoptions(precision=5)
pd.set_option("precision", 5)

fstFile='Main.fst'
linFile='Main.1.lin'
EDFile='ED.dat'


# --- Read the linearization file
lin = weio.read(linFile)
ED  = weio.read(EDFile)
TwrHeight = ED['TowerHt']-ED['TowerBsHt']

# --- Read lin file and extract relevant part of the D matrix (Minv)
dfs = lin.toDataFrame()
# print(dfs.keys())
# print(lin.keys())
D   = lin['D']
dfD = dfs['D']
print(D)
print(D.shape)
print(dfD)

# --- Extract the relevant 6x6 matrix
print('------- Extract 6x6 matrix')
Cols  = ['PtfmFxN1_[N]', 'PtfmFyN1_[N]', 'PtfmFzN1_[N]', 'PtfmMxN1_[Nm]', 'PtfmMyN1_[Nm]', 'PtfmMzN1_[Nm]']
Lines = ['PtfmTAxt_[m/s^2]', 'PtfmTAyt_[m/s^2]', 'PtfmTAzt_[m/s^2]', 'PtfmRAxt_[deg/s^2]', 'PtfmRAyt_[deg/s^2]', 'PtfmRAzt_[deg/s^2]']

missingRows = [l for l in Lines if l not in dfD.index]
missingCols = [c for c in Cols  if c not in dfD.columns]
if len(missingRows)>0:
    raise Exception('The following rows are missing from outputs: {}'.format(missingRows))
if len(missingCols)>0:
    raise Exception('The following columns are missing from inputs: {}'.format(missingCols))
Minv = dfD[Cols].loc[Lines].copy()
print(Minv)

# --- Convert the units to SI units
print('------- Convert to SI units')
Minv=matToSIunits(Minv, 'D')
print(Minv)

# ---  Inverse the matrix
print('------- Inverse the matrix')
M=inv(Minv)

# --- Identify mass, inertia and position of center of mass, based on mass matrix 
m=M[0,0]
M[np.abs(M)<m*0.001]=0
np.set_printoptions(precision=4)
print(np.around(M,1))
mass, J_G, CM = identifyRigidBodyMM(M)

print('J_G')
print(J_G)
print('Mass',mass)
print('xCM',CM[0])
print('yCM',CM[1])
print('zCM',CM[2]-TwrHeight) # NOTE: the center of mass was calculated wrt tower base, we want it wrt tower top

TT_2_CM = np.array([CM[0], CM[1], CM[2]-TwrHeight])

# --- Translate inertia matrix to the tower to
J_TT = translateInertiaMatrixFromCOG(J_G, mass, r_GP=-TT_2_CM)
print('J_TT\n',J_TT)



if __name__ == '__main__':
    pass
