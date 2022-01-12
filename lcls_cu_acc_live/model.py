from pytao import Tao
import numpy as np
import json
import yaml
import logging
from typing import List
from pkg_resources import resource_filename
from lcls_live.datamaps import get_datamaps
from lcls_live.datamaps.klystron import KlystronDataMap
from lume_model.variables import (
    InputVariable,
    OutputVariable,
)
from lume_model.models import SurrogateModel

logger = logging.getLogger(__name__)


DEFAULT_PVDATA_FILE = resource_filename(
    "lcls_cu_acc_live.data", "PVDATA-2021-04-21T08:10:25.000000-07:00.json"
)

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
    for dm in ALL_DATAMAPS.values():
        lines += dm.as_tao(pvdata)
    return lines


class AccModel(SurrogateModel):
    def __init__(self, pv_defaults: str = DEFAULT_PVDATA_FILE, input_variables={}, output_variables={}):
        # Basic model with options
        INIT = '-init $LCLS_LATTICE/bmad/models/cu_hxr/tao.init -slice OTR2:END -noplot'

        self.tao = Tao(INIT)
        self.dms = get_datamaps("cu_hxr")
        self.input_variables = input_variables
        self.output_variables = output_variables

        pvdata = {}
        for input_variable_name, input_variable in input_variables.items():
            pvdata[input_variable_name] = input_variable.default

        #initialize
        cmds = get_tao(self.dms, pvdata)
        self.init_tao(cmds)


    @classmethod
    def build_variable_file(self, pv_defaults, variable_filename, config_filename):
        # Basic model with options
        INIT = '-init $LCLS_LATTICE/bmad/models/cu_hxr/tao.init -slice OTR2:END -noplot'

        tao = Tao(INIT)

        dms = get_datamaps("cu_hxr")
        pv_default_file = pv_defaults

        if pv_defaults:
            with open(pv_defaults) as data_file:
                pvdata = json.load(data_file)

        with open(pv_default_file, "r") as data_file:
            pvdata = json.load(data_file)

        # CREATE VARIABLE FILE

        data = {"input_variables": {}, "output_variables": {}}
        pvs = {"input_variables": {}, "output_variables": {}}

        # build input variables
        for dm in dms:
            for pv in dm.pvlist:
                value = pvdata.get(pv)
                if value is None:
                    value = 0

                if isinstance(value, (float, int, type(None))):
                    data["input_variables"][pv] = {"name": pv, "range": [-np.inf, np.inf], "default":value, "type": "scalar"}

                elif isinstance(value, (list)):
                    data["input_variables"][pv] = {"name": pv,"default":value, "type": "array"}

                pvs["input_variables"][pv] = {"pvname": pv, "serve": False, "protocol": "ca"}

        # update ouptuts
        self.output_variables = {}
        for key in TAO_OUTKEYS:
            if key == "ele.name":
                data["output_variables"][key] = {"name": key, "type": "array"}

            else:
                data["output_variables"][key] = {"name": key, "type": "array"}

            pvs["output_variables"][key] = {"pvname": key, "protocol": "pva"}

        with open(variable_filename, "w") as f:
            yaml.dump(data, f, default_flow_style=False) 

        with open(config_filename, "w") as f:
            yaml.dump(pvs, f, default_flow_style=False) 


    def execute_tao(self, cmd: str) -> None:
        """ Wrapper for Tao execution to handle exceptions.

        Args:
            cmd (str): Command to execute

        """
        try:
            self.tao.cmd(cmd)

        except RuntimeError as e:
            logger.warning(e)

    def init_tao(self, cmds: List[str]) -> dict:
        """ Execution of tao initialization.

        Args: 
            cmds (List[str]): List of commands to execute

        Returns:
            dict: Tao output

        """

        init_cmds = """
        set global lattice_calc_on = F
        set lattice model=design ! Reset the lattice
        set ele quad::* field_master = T
        """.split(
            '\n'
        )

        final_cmds = """
        set global lattice_calc_on = T
        !set global plot_on = T
        """.split(
            '\n'
        )

        for cmd in init_cmds:
            self.execute_tao(cmd)

        for cmd in cmds:
            self.execute_tao(cmd)

        for cmd in final_cmds:
            self.execute_tao(cmd)

        output = {k: self.tao.lat_list('*', k) for k in TAO_OUTKEYS}

        n = len(output["ele.name"])

        output["ele.mat6"] = output["ele.mat6"].reshape(
            len(output["ele.mat6"]) // 36, 6, 6
        )
        output["ele.vec0"] = output["ele.vec0"].reshape(len(output["ele.vec0"]) // 6, 6)
        return output

    def run_tao(self, cmds: List[str]) -> dict:
        """ Execution command for tao execution.

        Args: 
            cmds (List[str]): List of commands to execute

        Returns:
            dict: Tao output

        """

        init_cmds = """
        set global lattice_calc_on = F
        set lattice model=design ! Reset the lattice
        !set ele quad::* field_master = T
        """.split(
            '\n'
        )

        final_cmds = """
        set global lattice_calc_on = T
        !set global plot_on = T
        !sc
        """.split(
            '\n'
        )

        for cmd in init_cmds:
            self.execute_tao(cmd)

        for cmd in cmds:
            self.execute_tao(cmd)

        for cmd in final_cmds:
            self.execute_tao(cmd)

        output = {k: self.tao.lat_list('*', k) for k in TAO_OUTKEYS}

        n = len(output["ele.name"])
        output["ele.mat6"] = output["ele.mat6"].reshape(
            len(output["ele.mat6"]) // 36, 6, 6
        )
        output["ele.vec0"] = output["ele.vec0"].reshape(len(output["ele.vec0"]) // 6, 6)

        return output

    def evaluate(self, input_variables: List[InputVariable]) -> List[OutputVariable]:
        """ Implements the abstract base evaluate method to be executed by lume-epics server.

        Args:
            input_variables (List[InputVariable]): List of input variables to evaluate

        """

        for variable in input_variables:

            self.input_variables[variable.name] = variable

        cmds = []
        for dm in self.dms.values():
            pvdata = {variable.name: variable.value for variable in input_variables}

            # handle the Klystron extra pvs
            # these must be defined when getting commands from the klystron datamaps and might not be
            # provided in the update variables so access those stored
            if isinstance(dm, (KlystronDataMap,)):

                if dm.swrd_pvname:
                    pvdata[dm.swrd_pvname] = self.input_variables[dm.swrd_pvname].value

                if dm.enld_pvname:
                    pvdata[dm.enld_pvname] = self.input_variables[dm.enld_pvname].value

                if dm.phase_pvname:
                    pvdata[dm.phase_pvname] = self.input_variables[
                        dm.phase_pvname
                    ].value

                if dm.accelerate_pvname:
                    pvdata[dm.accelerate_pvname] = self.input_variables[
                        dm.accelerate_pvname
                    ].value

                if dm.pvlist & pvdata.keys():

                    # same here with fault pvs
                    if dm.has_fault_pvnames:
                        fault_pvs = [
                            self.input_variables[dm.swrd_pvname],
                            self.input_variables[dm.stat_pvname],
                            self.input_variables[dm.hdsc_pvname],
                            self.input_variables[dm.dsta_pvname],
                        ]
                        pvdata.update({pv.name: pv.value for pv in fault_pvs})

            cmds += dm.as_tao(pvdata)

        cmds = [cmd for cmd in cmds if "! Bad value" not in cmd]
        output = self.run_tao(cmds)

        # update output variables with the new values
        for variable in output:
            self.output_variables[variable].value = np.array(output[variable])

        return self.output_variables.values()


if __name__ == "__main__":
    # main method will generate the variable files
    import os

    root_dir = os.path.dirname(os.path.abspath(__file__))

    variable_filename= f"{root_dir}/files/variables.yml"
    epics_config_filename = f"{root_dir}/files/epics_config.yml"

    vars = AccModel.build_variable_file(DEFAULT_PVDATA_FILE, variable_filename, epics_config_filename)