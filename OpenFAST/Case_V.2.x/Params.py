import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
# Local 
from welib.fast.olaf import *
from welib.dyninflow.DynamicInflow import tau1_oye


U0=7.5
RPM=5.33
R = 120.97

a_bar = 0.3083

print('DBEMT tau1: ', tau1_oye(a_bar, R, U0))



OLAFParams(RPM, deltaPsiDeg=6, nNWrot=7, nFWrot=2, nFWrotFree=1, nPerRot=None, totalRot=None, show=True)




if __name__ == '__main__':
    pass
