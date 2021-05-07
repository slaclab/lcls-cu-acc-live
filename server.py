from lume_epics.epics_server import Server
from model import AccModel

if __name__ == '__main__':
    print("Starting channel access server...")
    server = Server(
        AccModel,
        "test",
        protocols = ["ca"],
    )

    server.start(monitor=True)
    print("Server stopped.")