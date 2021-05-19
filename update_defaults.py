from lcls_live.archiver import lcls_archiver_restore
from lume_model.utils import variables_from_yaml
from pkg_resources import resource_filename
from lume_model.utils import load_variables, save_variables
import os 
import json

os.environ['http_proxy']='socks5h://localhost:8080'
os.environ['HTTPS_PROXY']='socks5h://localhost:8080'
os.environ['ALL_PROXY']='socks5h://localhost:8080'


variable_filename = resource_filename("lcls_cu_acc_live.files", "model_variables.pickle")
input_variables, output_variables = load_variables(variable_filename)

input_pvs = [var for var in input_variables] 
output_pvs = [var for var in output_variables]


# input pvs
pvs = lcls_archiver_restore(input_pvs, '2021-04-21T08:10:25.000000-07:00')
with open("lcls_cu_acc_live/data/PVDATA-2021-04-21T08:10:25.000000-07:00.json", "w") as f:
    json.dump(pvs, f)


for pv, value in pvs.items():
    input_variables[pv].default = value

save_variables(input_variables, output_variables, "lcls_cu_acc_live/files/model_variables.pickle")