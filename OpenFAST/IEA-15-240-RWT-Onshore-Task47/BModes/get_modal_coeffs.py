
import os
import numpy as np
import matplotlib.pyplot as plt
import sys
sys.path.append("C:/Work/_libs/_External/WEIS/")
from weis.aeroelasticse.FAST_reader import InputReader_OpenFAST
from weis.aeroelasticse.FAST_writer import InputWriter_OpenFAST

run_dir = os.path.dirname( os.path.realpath(__file__) ) + os.sep
# blade_file = os.path.join(run_dir, 'BModes_blade.out')
ed_blade_file = os.path.join(run_dir, '..', 'OpenFAST_3p0', 'ElastoDyn_Blade.dat') # Will be overriden
ed_tower_file = os.path.join(run_dir, '../IEA-15-240-RWT-Onshore_ElastoDyn_tower.dat') # Will be overrident
tower_file = os.path.join(run_dir, 'BModes_tower.out')
n_modes = 20
n_nodes = 62
plots = True
blade = False
tower = True

def get_modal_coefficients(x, y, deg=[2, 3, 4, 5, 6]):
    # Normalize x input
    xn = (x - x.min()) / (x.max() - x.min())
    # Get coefficients to 6th order polynomial
    p6 = np.polynomial.polynomial.polyfit(xn, y, deg)
    return p6

if blade:
    f = open(blade_file)
    freqs = np.zeros(20)
    mode_shapes_blade = np.zeros((n_modes,n_nodes,6))
    counter=0
    while 1:
        row_string = f.readline()
        freq_id = row_string.find('freq = ')
        if freq_id > 0:
            freqs[counter] = float(row_string[freq_id+7:freq_id+19])
            f.readline()
            f.readline()
            f.readline()
            for i in range(n_nodes):
                row_data = f.readline()
                mode_shapes_blade[counter, i, :] = row_data.split()
            counter += 1
        if counter == 3:
            break

    # 1st flap, 1st edge, 2nd flap
    p6_1f = get_modal_coefficients(mode_shapes_blade[0, :, 0], mode_shapes_blade[0, :, 1])
    p6_1e = get_modal_coefficients(mode_shapes_blade[1, :, 0], mode_shapes_blade[1, :, 3])
    p6_2f = get_modal_coefficients(mode_shapes_blade[2, :, 0], mode_shapes_blade[2, :, 1])

    p6_1f /= np.sum(p6_1f)
    p6_1e /= np.sum(p6_1e)
    p6_2f /= np.sum(p6_2f)

    x=np.linspace(0., 1., 100)
    y_1f=x**2. * p6_1f[2] + x**3. * p6_1f[3] + x**4. * p6_1f[4] + x**5. * p6_1f[5] + x**6. * p6_1f[6]
    y_1e=x**2. * p6_1e[2] + x**3. * p6_1e[3] + x**4. * p6_1e[4] + x**5. * p6_1e[5] + x**6. * p6_1e[6]
    y_2f=x**2. * p6_2f[2] + x**3. * p6_2f[3] + x**4. * p6_2f[4] + x**5. * p6_2f[5] + x**6. * p6_2f[6]

    print('1st Flap', p6_1f[2:])
    print('1st Edge', p6_1e[2:])
    print('2nd Flap', p6_2f[2:])

    fast = InputReader_OpenFAST()
    fast.read_ElastoDynBlade(ed_blade_file)
    fast.fst_vt['ElastoDynBlade']['BldFl1Sh'] = p6_1f[2:]
    fast.fst_vt['ElastoDynBlade']['BldFl2Sh'] = p6_2f[2:]
    fast.fst_vt['ElastoDynBlade']['BldEdgSh'] = p6_1e[2:]
    fast_out = InputWriter_OpenFAST()
    fast_out.FAST_runDirectory = os.path.dirname(ed_blade_file)
    fast_out.FAST_namingOut = 'new'
    fast_out.fst_vt = fast.fst_vt
    fast_out.write_ElastoDynBlade()

if tower:
    f = open(tower_file)
    freqs = np.zeros(20)
    mode_shapes_tower = np.zeros((n_modes,n_nodes,6))
    counter=0
    while 1:
        row_string = f.readline()
        freq_id = row_string.find('freq = ')
        if freq_id > 0:
            freqs[counter] = float(row_string[freq_id+7:freq_id+19])
            f.readline()
            f.readline()
            f.readline()
            for i in range(n_nodes):
                row_data = f.readline()
                mode_shapes_tower[counter, i, :] = row_data.split()
            counter += 1
        if counter == 4:
            break

    # 1st FA, 1st SS, 2nd FA, 2nd SS
    p6_1fa = get_modal_coefficients(mode_shapes_tower[1, :, 0], mode_shapes_tower[1, :, 3])
    p6_1ss = get_modal_coefficients(mode_shapes_tower[0, :, 0], mode_shapes_tower[0, :, 1])
    p6_2fa = get_modal_coefficients(mode_shapes_tower[3, :, 0], mode_shapes_tower[3, :, 3])
    p6_2ss = get_modal_coefficients(mode_shapes_tower[2, :, 0], mode_shapes_tower[2, :, 1])

    p6_1fa /= np.sum(p6_1fa)
    p6_1ss /= np.sum(p6_1ss)
    p6_2ss /= np.sum(p6_2ss)
    p6_2fa /= np.sum(p6_2fa)

    x=np.linspace(0., 1., 100)
    y_1fa=x**2. * p6_1fa[2] + x**3. * p6_1fa[3] + x**4. * p6_1fa[4] + x**5. * p6_1fa[5] + x**6. * p6_1fa[6]
    y_1ss=x**2. * p6_1ss[2] + x**3. * p6_1ss[3] + x**4. * p6_1ss[4] + x**5. * p6_1ss[5] + x**6. * p6_1ss[6]
    y_2ss=x**2. * p6_2ss[2] + x**3. * p6_2ss[3] + x**4. * p6_2ss[4] + x**5. * p6_2ss[5] + x**6. * p6_2ss[6]
    y_2fa=x**2. * p6_2fa[2] + x**3. * p6_2fa[3] + x**4. * p6_2fa[4] + x**5. * p6_2fa[5] + x**6. * p6_2fa[6]

    print('1st FA', p6_1fa[2:])
    print('1st SS', p6_1ss[2:])
    print('2nd SS', p6_2ss[2:])
    print('2nd FA', p6_2fa[2:])

    print(np.sum(p6_1fa[2:]))
    print(np.sum(p6_1ss[2:]))
    print(np.sum(p6_2ss[2:]))
    print(np.sum(p6_2fa[2:]))

    fast = InputReader_OpenFAST()
    fast.read_ElastoDynTower(ed_tower_file)
    fast.fst_vt['ElastoDynTower']['TwFAM1Sh'] = p6_1fa[2:]
    fast.fst_vt['ElastoDynTower']['TwFAM2Sh'] = p6_2fa[2:]
    fast.fst_vt['ElastoDynTower']['TwSSM1Sh'] = p6_1ss[2:]
    fast.fst_vt['ElastoDynTower']['TwSSM2Sh'] = p6_2ss[2:]
    fast_out = InputWriter_OpenFAST()
    fast_out.FAST_runDirectory = os.path.dirname(ed_tower_file)
    fast_out.FAST_namingOut = 'new'
    fast_out.fst_vt = fast.fst_vt
    fast_out.write_ElastoDynTower()

if plots:
    if blade:
        f, ax = plt.subplots(3, 1, figsize=(5.3, 8))
        ax[0].plot(mode_shapes_blade[0, :, 0], mode_shapes_blade[0, :, 1]/mode_shapes_blade[0, -1, 1], label="BModes")
        ax[0].plot(x, y_1f/y_1f[-1], '--', label="Poly")
        ax[0].grid(color=[0.8, 0.8, 0.8], linestyle="--")
        ax[0].legend()
        ax[0].set_ylabel("1st Flap", fontweight="bold")
        ax[0].set_title("Blade Modes", fontweight="bold")
        ax[1].plot(mode_shapes_blade[1, :, 0], mode_shapes_blade[1, :, 3]/mode_shapes_blade[1, -1, 3], label="BModes")
        ax[1].plot(x, y_1e/y_1e[-1], '--', label="Poly")
        ax[1].grid(color=[0.8, 0.8, 0.8], linestyle="--")
        ax[1].legend()
        ax[1].set_ylabel("1st Edge", fontweight="bold")
        ax[2].plot(mode_shapes_blade[2, :, 0], mode_shapes_blade[2, :, 1]/mode_shapes_blade[2, -1, 1], label="BModes")
        ax[2].plot(x, y_2f/y_2f[-1], '--', label="Poly")
        ax[2].grid(color=[0.8, 0.8, 0.8], linestyle="--")
        ax[2].legend()
        ax[2].set_ylabel("2nd Flap", fontweight="bold")
        plt.show()
        plt.close()
    if tower:
        f, ax = plt.subplots(4, 1, figsize=(5.3, 8))
        ax[0].plot(mode_shapes_tower[0, :, 0], mode_shapes_tower[0, :, 3]/mode_shapes_tower[0, -1, 3], label="BModes")
        ax[0].plot(x, y_1fa/y_1fa[-1], '--', label="Poly")
        ax[0].grid(color=[0.8, 0.8, 0.8], linestyle="--")
        ax[0].legend()
        ax[0].set_ylabel("1st FA", fontweight="bold")
        ax[0].set_title("Tower Modes", fontweight="bold")
        ax[1].plot(mode_shapes_tower[1, :, 0], mode_shapes_tower[1, :, 1]/mode_shapes_tower[1, -1, 1], label="BModes")
        ax[1].plot(x, y_1ss/y_1ss[-1], '--', label="Poly")
        ax[1].grid(color=[0.8, 0.8, 0.8], linestyle="--")
        ax[1].legend()
        ax[1].set_ylabel("1st SS", fontweight="bold")
        ax[2].plot(mode_shapes_tower[2, :, 0], mode_shapes_tower[2, :, 1]/mode_shapes_tower[2, -1, 1], label="BModes")
        ax[2].plot(x, y_2ss, '--', label="Poly")
        ax[2].grid(color=[0.8, 0.8, 0.8], linestyle="--")
        ax[2].legend()
        ax[2].set_ylabel("2nd SS", fontweight="bold")
        ax[3].plot(mode_shapes_tower[3, :, 0], mode_shapes_tower[3, :, 3]/mode_shapes_tower[3, -1, 3], label="BModes")
        ax[3].plot(x, y_2fa, '--', label="Poly")
        ax[3].grid(color=[0.8, 0.8, 0.8], linestyle="--")
        ax[3].legend()
        ax[3].set_ylabel("2nd FA", fontweight="bold")
        plt.show()
        plt.close()

