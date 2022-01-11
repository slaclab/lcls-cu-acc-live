from pkg_resources import resource_filename

VARIABLE_FILE = resource_filename(
    "lcls_cu_acc_live.files", "variables.yml"
)

EPICS_CONFIG_FILE = resource_filename(
    "lcls_cu_acc_live.files", "epics_config.yml"
)
