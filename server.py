from lume_epics.epics_server import Server
from model import AccModel

if __name__ == '__main__':
    server = Server(
        AccModel,
        "BMAD",
        protocols = ["ca", "pva"]
    )

    server.start(monitor=True)