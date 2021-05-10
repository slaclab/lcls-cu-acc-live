from pytao import Tao
import json
from lcls_live.datamaps import get_datamaps
import time
import itertools
import matplotlib.pyplot as plt

pv_defaults="data/PVDATA-2021-04-21T08:10:25.000000-07:00.json"

# Basic model with options
INIT = '-init $LCLS_LATTICE/bmad/models/cu_hxr/tao.init -slice OTR2:END -noplot'

tao = Tao(INIT)

dms = get_datamaps("cu_hxr")

with open(pv_defaults) as data_file:
    pvdata = json.load(data_file)  

# make sure all pvs represented
for dm in dms:
    for pv in dm.pvlist:
        if pv not in pvdata:
            pvdata[pv] = 0
        if pvdata[pv] is None:
            pvdata[pv] = 0

def get_tao(dms, pvdata):
    lines = []
    for dm in dms:
        lines += dm.as_tao(pvdata)
    return lines

def run_tao(cmds):
    init_cmds = """
    set global lattice_calc_on = F
    set lattice model=design ! Reset the lattice
    !set ele quad::* field_master = T
    """.split('\n')

    final_cmds = """
    set global lattice_calc_on = T
    !set global plot_on = T
    !sc
    """.split('\n')

    for cmd in init_cmds:
        tao.cmd(cmd)

    for cmd in cmds:
        tao.cmd(cmd)

    for cmd in final_cmds:
        tao.cmd(cmd)

with open(pv_defaults) as data_file:
    pvdata = json.load(data_file)  

# Use dms as a marker of n commands
times = []
cmd_n = []
for i in range(len(dms)):
    use_dms = dms[:i]
    cmds = get_tao(use_dms, pvdata)
    start_time = time.time()
    run_tao(cmds)
    end_time=time.time()
    time_calc = end_time - start_time
    times.append(time_calc)
    cmd_n.append(len(cmds))

    print(f"n commands: {len(cmds)}")
    print(f"time: {time_calc}")

plt.plot(time, cmd_n)
plt.show()