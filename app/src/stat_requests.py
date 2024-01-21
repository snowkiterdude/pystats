""" manage a requests log sqlite database """

import sqlite3
import os
import socket
import time
import platform


class StatRequests:
    """manage a requests log sqlite database"""

    def __init__(self, db_path="requests.db"):
        """Initialize db class"""
        self.con = sqlite3.connect(db_path)
        self.cur = self.con.cursor()
        self.con.execute("PRAGMA foreign_keys = 1")
        self.con.execute(
            """CREATE TABLE IF NOT EXISTS servers(
                ServerID INTEGER PRIMARY KEY AUTOINCREMENT,
                Hostname TEXT NOT NULL,
                IP TEXT  NOT NULL,
                Platform TEXT
            )"""
        )
        self.con.execute(
            """CREATE TABLE IF NOT EXISTS requests(
                RequestID INTEGER PRIMARY KEY AUTOINCREMENT,
                Epoch REAL NOT NULL,
                RemoteAddress TEXT,
                RemoteUserAgent TEXT,
                RequestURL TEXT,
                ServerID INTEGER,
                FOREIGN KEY(ServerID) REFERENCES servers(ServerID)
            )"""
        )
        self._add_server()
        if not self.server_id:
            raise NoServerID("Could not set Server ID")

    def __enter__(self):
        return self

    def __exit__(self, ext_type, exc_value, traceback):
        self.cur.close()
        if isinstance(exc_value, Exception):
            self.con.rollback()
        else:
            self.con.commit()
        self.con.close()

    def _add_server(self):
        host_data = {
            "hostname": str(os.uname()[1]),
            "ip": str(socket.gethostbyname(socket.gethostname())),
            "platform": str(platform.platform()),
        }
        self.cur.execute(
            "SELECT ServerID from servers WHERE Hostname=:hostname AND IP=:ip",
            host_data,
        )
        our_id = self.cur.fetchone()
        if not our_id:
            self.cur.execute(
                "INSERT INTO servers (Hostname, IP, Platform) VALUES (:hostname, :ip, :platform)",
                host_data,
            )
            self.con.commit()
            self.cur.execute(
                "SELECT ServerID from servers WHERE Hostname=:hostname AND IP=:ip",
                host_data,
            )
            our_id = self.cur.fetchone()
        self.server_id = our_id[0]

    def put_request(self, remote_addr, remote_user_agent, request_url):
        """ write request data to the sqlite date base """
        req_data = {
            "epoch": float(round(time.time(), 4)),
            "remote_address": str(remote_addr),
            "remote_user_agent": str(remote_user_agent),
            "request_url": str(request_url),
            "server_id": int(self.server_id),
        }
        self.cur.execute(
            """INSERT INTO requests (
                Epoch, RemoteAddress, RemoteUserAgent, RequestURL, ServerID
            ) VALUES (
                :epoch, :remote_address, :remote_user_agent, :request_url, :server_id
            )""",
            req_data,
        )
        self.con.commit()


class NoServerID(Exception):
    """ Exection in case we can not set the FOREIGN KEY linking the requests to a server id """


# cur.execute("SELECT * FROM servers")
# print(f"servers: {cur.fetchall()}")

# cur.execute("SELECT * FROM requests")
# print(f"requests: {cur.fetchall()}")
