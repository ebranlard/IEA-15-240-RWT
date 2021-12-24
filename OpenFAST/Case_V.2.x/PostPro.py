import os
import glob
import pandas as pd
import numpy as np
import scipy as sp
import scipy.interpolate
# Welib https://github.com/ebranlard/welib
import welib
import welib.fast.fastlib as fastlib
import welib.tools.clean_exceptions
from welib.weio.fast_input_deck import *
from welib.weio.fast_input_file import *


def interp_extrap1d(xi,xp,yp):
    xp=np.asarray(xp)
    yp=np.asarray(yp)
    interpolator = sp.interpolate.interp1d(xp, yp)

    def pointwise(x):
        if x < xp[0]:
            return yp[0]+(x-xp[0])*(yp[1]-yp[0])/(xp[1]-xp[0])
        elif x > xp[-1]:
            return yp[-1]+(x-xp[-1])*(yp[-1]-yp[-2])/(xp[-1]-xp[-2])
        else:
            return interpolator(x)

    return np.array(list(map(pointwise, np.asarray(xi))))


# --------------------------------------------------------------------------------}
# ---  
# --------------------------------------------------------------------------------{
def PostProAD(dfRadAD, dfRad=None, i=1):
#     print(dfRadAD.columns.values)
    # --- LiftingLine Aero Outputs
    ColMap=dict()
    ColMap['r']                   = 'r_[m]'
    ColMap['Veff1.{}'.format(i)]  = 'B1Vrel_[m/s]'
    ColMap['alpha1.{}'.format(i)] = 'B1Alpha_[deg]'
    ColMap['ui1.{}'.format(i)]    = 'B1Vindx_[m/s]'
    ColMap['utan1.{}'.format(i)]  = 'B1Vindy_[m/s]'
    ColMap['cn1.{}'.format(i)]    = 'B1Cn_[-]'
    ColMap['ct1.{}'.format(i)]    = 'B1Ct_[-]'
    dfLL = fastlib.remap_df(dfRadAD, ColMap, bColKeepNewOnly=True, inPlace=True)
    # --- LiftingLine Loads
    ColMap=dict()
    ColMap['r']                     = 'r'
    ColMap['Fn_c1.{}'.format(i)]    = 'B1Fn_[N/m]'
    ColMap['Ft_c1.{}'.format(i)]    = 'B1Ft_[N/m]'
    ColMap['Fn_r1.{}'.format(i)]    = 'B1Fx_[N/m]'
    ColMap['Ft_r1.{}'.format(i)]    = 'B1Fy_[N/m]'
    ColMap['Defl_flap.{}'.format(i)] = '0 * {r}'
    ColMap['Defl_edge.{}'.format(i)] = '0 * {r}'
    ColMap['Defl_tors.{}'.format(i)] = '0 * {r}'
    dfFD = fastlib.remap_df(dfRadAD.copy(), ColMap, bColKeepNewOnly=True, inPlace=False)
    # ---
    if dfRad is not None:
        print(dfRad.columns.values)
        if 'B1TDx_[m]' in dfRad.columns.values:
            # --- ED
            r_ED = dfRad['r_[m]']
            r_AD = dfLL['r']
            dx = interp_extrap1d(r_AD, r_ED, dfRad['B1TDx_[m]']) # using scipy for extra
            dy =-interp_extrap1d(r_AD, r_ED, dfRad['B1TDy_[m]'])
            dt = interp_extrap1d(r_AD, r_ED, dfRad['B1RDz_[deg]'])
        else:
            # --- BD
            r_BD = dfRad['r_[m]'].values
            r_AD = dfLL['r'].values
            print('r_BD',r_BD)
            print('r_AD',r_AD)
            dx = interp_extrap1d(r_AD, r_BD, dfRad['B1TDxr_[m]'])
            dy =-interp_extrap1d(r_AD, r_BD, dfRad['B1TDyr_[m]'])
            # TODO TODO This needs to be converted from rotation parameters to true rotations
            # Also, torsional definition needs to be agreed upon
            dt = interp_extrap1d(r_AD, r_BD, dfRad['B1RDzr_[-]'])*180/np.pi 
        dfFD['Defl_flap.{}'.format(i)]=dx
        dfFD['Defl_edge.{}'.format(i)]=dy
        dfFD['Defl_tors.{}'.format(i)]=dt

    return dfLL, dfFD



# --- Main Parameters
OutDir    = '_Results/'
SimDir    = './'

Case      = 1
avgMethod = 'periods'
avgParam  = 2

suffix='-ED'
# suffix='-BD'
# suffix='-ED-VC'
# Cases = [ 'V.2.1', 'V.2.2' ]
Cases = [ 'V.2.2', 'V.2.1' ]


for case in Cases:
    basename = os.path.join(SimDir,'Main_'+case+suffix)
    # NOT for case 1, BD or ED doesn't matter
    #out_ext = '.out' if ('-VC' in suffix) or ('-BD' in suffix) else '.outb'
    out_ext = '.out' if ('-BD' in suffix) else '.outb'
    if case=='V.2.1' and suffix=='-BD':
        basename = os.path.join(SimDir,'Main_'+case+'-ED')
        out_ext = '.outb'

    print('>>>', basename)
    dfRadED, dfRadAD, dfRadBD, df1 = fastlib.spanwisePostPro(basename+'.fst', avgMethod=avgMethod, avgParam=avgParam, out_ext=out_ext)

    dfAvg= fastlib.averageDF(df1,avgMethod=avgMethod,avgParam=avgParam)
    if '2.1' in case:
        Thrust1= dfAvg['RotThrust_[kN]'].values[0]*1000
        Torque1= dfAvg['RotTorq_[kN-m]'].values[0]*1000
        dfLL1, dfFD1 = PostProAD(dfRadAD, dfRadED, i=1)
        #print(dfLL1.columns)
    else:
        Thrust2= dfAvg['RotThrust_[kN]'].values[0]*1000
        Torque2= dfAvg['RotTorq_[kN-m]'].values[0]*1000
        if '-BD' in suffix:
            dfLL2, dfFD2 = PostProAD(dfRadAD, dfRadBD, i=2)
        else:
            dfLL2, dfFD2 = PostProAD(dfRadAD, dfRadED, i=2)
        #print(dfLL2.columns)


dfLL2 = dfLL2.drop(columns = ['r'])
dfFD2 = dfFD2.drop(columns = ['r'])
dfLL  = pd.concat([dfLL1, dfLL2], axis = 1)
dfFD  = pd.concat([dfFD1, dfFD2], axis = 1)
sThrust='\n'+'Thrust            \t'+'\t'.join(['{:17.5f}'.format(Thrust1)]*6) +'\t'.join(['{:17.5f}'.format(Thrust2)]*6)+'\n'
sTorque=     'Torque            \t'+'\t'.join(['{:17.5f}'.format(Torque1)]*6) +'\t'.join(['{:17.5f}'.format(Torque2)]*6)

sHeader='\t'.join(['{:17.17s}'.format(c) for c in list(dfFD.columns.values)])
print(sThrust)
print(sTorque)

np.savetxt(os.path.join(OutDir,'CaseV.2'+suffix+'_LiftingLine.csv'),dfLL.values, delimiter='\t',fmt='%17.5f', header='\t'.join(list(dfLL.columns.values)))
np.savetxt(os.path.join(OutDir,'CaseV.2'+suffix+'_Loads.csv')      ,dfFD.values, delimiter='\t',fmt='%17.5f', header=sHeader+sThrust+sTorque)
