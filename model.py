from pytao import Tao
import numpy as np
import json
from typing import List
from importlib.resources import files
from lcls_live.datamaps import get_datamaps
from lume_model.variables import ScalarInputVariable, ArrayInputVariable, ArrayOutputVariable, InputVariable, OutputVariable

TAO_OUTKEYS = """ele.name
ele.ix_ele
ele.ix_branch
ele.a.beta
ele.a.alpha
ele.a.eta
ele.a.etap
ele.a.gamma
ele.a.phi
ele.b.beta
ele.b.alpha
ele.b.eta
ele.b.etap
ele.b.gamma
ele.b.phi
ele.x.eta
ele.x.etap
ele.y.eta
ele.y.etap
ele.s
ele.l
ele.e_tot
ele.p0c
ele.mat6
ele.vec0
""".split()

def get_tao(ALL_DATAMAPS, pvdata):
    lines = []
    for dm in ALL_DATAMAPS:
        lines += dm.as_tao(pvdata)
    return lines

class AccModel:
    def __init__(self):
        # Basic model with options
        INIT = f'-init $LCLS_LATTICE/bmad/models/cu_hxr/tao.init -slice OTR2:END -noplot'

        self.tao = Tao(INIT)

        # filter klystrons
        klystron_names = self.tao.lat_list('overlay::K*', 'ele.name', flags='-no_slaves')
        self.dms = get_datamaps(["klystron", "quad", "linac", "tao_energy_measurements", "subboosters", "beginning_OTR2"], klystron_names=klystron_names)

        with files('lcls_live.data.pvs').joinpath('PVDATA-2021-04-21T08:10:25.000000-07:00.json') as data_path:
            with open(data_path) as data_file:
                pvdata = json.load(data_file)  

        cmds = get_tao(self.dms, pvdata)
        output = self.run_tao(cmds)

        #build input variables
        self.input_variables = {}
        for dm in self.dms:
            for pv in dm.pvlist:
                if isinstance(pvdata[pv], (float, int, type(None))):
                    self.input_variables[pv] = ScalarInputVariable(name=pv, range=[-np.inf, np.inf], default=pvdata[pv])

                elif isinstance(pvdata[pv], (list)):
                    self.input_variables[pv] = ArrayInputVariable(name=pv, default=np.array(pvdata[pv]))

                else: 
                    print(f"NOT FOUND {pv}, {pvdata[pv]}")


        self.output_variables = {}
        for key in TAO_OUTKEYS:
            if key == "ele.name":
                self.output_variables[key] = ArrayOutputVariable(name=key, value_type="string")

            else:
                self.output_variables[key] = ArrayOutputVariable(name=key)


    def run_tao(self, cmds):
        init_cmds = """
        place floor energy
        !set global plot_on = F
        set global lattice_calc_on = F
        set lattice model=design ! Reset the lattice
        set ele quad::* field_master = T
        """.split('\n')

        final_cmds = """
        set global lattice_calc_on = T
        !set global plot_on = T
        """.split('\n')

        for cmd in init_cmds:
            self.tao.cmd(cmd)

        for cmd in cmds:
            self.tao.cmd(cmd)

        for cmd in final_cmds:
            self.tao.cmd(cmd)

        output = {k:self.tao.lat_list('*', k) for k in TAO_OUTKEYS}

        n = len(output["ele.name"])
        output["ele.mat6"] = output["ele.mat6"].reshape(len(output["ele.mat6"])//36, 6, 6)
        output["ele.vec0"] = output["ele.vec0"].reshape(len(output["ele.vec0"])//6, 6)

        return output


    def evaluate(self, input_variables: List[InputVariable]) -> List[OutputVariable]:
        self.input_variables = input_variables
        pvdata = {variable.name: variable.value for variable in input_variables}

        cmds = get_tao(self.dms, pvdata)
        output = self.run_tao(cmds)

        for variable in self.output_variables.values():
            variable.value = np.array(output[variable.name])

        return self.output_variables.values()

if __name__ == "__main__":
    from lume_model.utils import save_variables
    model = AccModel()
    save_variables(model.input_variables, model.output_variables, "model_variables.pickle")