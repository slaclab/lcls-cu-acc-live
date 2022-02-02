from lume_epics.epics_server import Server
from lcls_cu_acc_live.model import AccModel
from lume_model.utils import variables_from_yaml
from lume_epics.utils import config_from_yaml
import argparse
import logging
from lcls_cu_acc_live import VARIABLE_FILE, EPICS_CONFIG_FILE


parser = argparse.ArgumentParser()

parser.add_argument(
    "-log",
    "--log",
    default="warning",
    help=("Provide logging level. " "Example --log debug', default='warning'"),
)

options = parser.parse_args()
levels = {
    'critical': logging.CRITICAL,
    'error': logging.ERROR,
    'warn': logging.WARNING,
    'warning': logging.WARNING,
    'info': logging.INFO,
    'debug': logging.DEBUG,
}
level = levels.get(options.log.lower())
if level is None:
    raise ValueError(
        f"log level given: {options.log}"
        f" -- must be one of: {' | '.join(levels.keys())}"
    )

logging.basicConfig(level=level)
logger = logging.getLogger(__name__)
logger.setLevel("INFO")


def main():
    logger.info("Starting server...")

    with open(VARIABLE_FILE, "r") as f:
        input_variables, output_variables = variables_from_yaml(f)

    with open(EPICS_CONFIG_FILE, "r") as f:
        epics_config = config_from_yaml(f)

    server = Server(AccModel, epics_config, model_kwargs={
            "input_variables": input_variables,
            "output_variables": output_variables,
        },)

    server.start(monitor=True)
    logger.info("Server stopped.")


if __name__ == '__main__':
    main()
