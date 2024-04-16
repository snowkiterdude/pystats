""" argument parsing """
import argparse
import os


## help message strings
MOD_DESC = """
pystats: Flask app to get system metrics on page load with request
logging for testing K8s Load Balancers, Statefulsets, and
Persistent Volumes or custom prometheus metrics endpoint.
"""
DB_PATH = """
The full file path to your sqlite file for the requests database.
DEFAULT: /var/lib/pystats/requests.db
"""
CREATE_PATH = """
Flag to create the parent directory path to the db file or not
allowing auto creation of a DB file.
DEFAULT: False
"""
WEB_HOST = """
The IP or Hostname for the flask web socket.
DEFAULT: 0.0.0.0
"""
WEB_PORT = """
The TCP Port for the flask web socket.
DEFAULT: 8080
"""


def parse_cfg():
    """Arguments via argparse"""
    parser = argparse.ArgumentParser(
        description=MOD_DESC,
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "--db-file",
        "-f",
        dest="db_path",
        help=DB_PATH,
        type=str,
        default="/var/lib/pystats/requests.db",
    )
    parser.add_argument(
        "--create-path",
        "-c",
        dest="crate_path",
        help=CREATE_PATH,
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "--web-host",
        dest="srv_socket_ip",
        help=WEB_HOST,
        type=str,
        default="0.0.0.0",
    )
    parser.add_argument(
        "--web-port",
        dest="srv_socket_port",
        help=WEB_PORT,
        type=str,
        default="8080",
    )

    cfg = parser.parse_args()
    if cfg.crate_path:
        db_dir = os.path.dirname(cfg.db_path)
        if not os.path.exists(db_dir):
            os.makedirs(db_dir)
    return cfg
