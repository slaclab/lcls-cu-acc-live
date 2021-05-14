from lume_epics.epics_server import Server
from model import AccModel
import argparse
import logging
parser = argparse.ArgumentParser()

parser.add_argument(
    "-log", 
    "--log", 
    default="warning",
    help=(
        "Provide logging level. "
        "Example --log debug', default='warning'"),
)

options = parser.parse_args()
levels = {
    'critical': logging.CRITICAL,
    'error': logging.ERROR,
    'warn': logging.WARNING,
    'warning': logging.WARNING,
    'info': logging.INFO,
    'debug': logging.DEBUG
}
level = levels.get(options.log.lower())
if level is None:
    raise ValueError(
        f"log level given: {options.log}"
        f" -- must be one of: {' | '.join(levels.keys())}")
logging.basicConfig(level=level)
logger = logging.getLogger("lume-epics")


def main():
    print("Starting server...")
    server = Server(
        AccModel,
        "test",
        protocols = ["ca"],
    )

    server.start(monitor=True)
    print("Server stopped.")




if __name__ == '__main__':
    main()
   
