""" Requests """
import sqlite3
import os
import socket
import platform
import time
from contextlib import closing
from .logger import get_logger


class Requests:
    """Class to maintain the server and requests tables"""

    def __init__(self, db_path):
        """Initialize db class"""
        self.log = get_logger()
        self.db_path = db_path
        self.db_active = self._db_init()
        self.server_id = self._add_server()

    def _db_init(self):
        """ initialize the database"""
        try:
            with closing(sqlite3.connect(self.db_path)) as con:
                con.execute("PRAGMA foreign_keys = 1")
                con.commit()
                with closing(con.cursor()) as cur:
                    cur.execute(
                        """CREATE TABLE IF NOT EXISTS servers(
                            ServerID INTEGER PRIMARY KEY AUTOINCREMENT,
                            Hostname TEXT NOT NULL,
                            IP TEXT  NOT NULL,
                            Platform TEXT
                        )"""
                    )
                    cur.execute(
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
                    return True
        except TypeError:
            self.log.warning("Could not connect to DB: %s", self.db_path)
        return False

    def _add_server(self):
        """add a entry to the servers table for this instance of pystats"""
        if not self.db_active:
            self.log.warning("AddServer: No DB Connection")
            return 0
        with closing(sqlite3.connect(self.db_path)) as con:
            with closing(con.cursor()) as cur:
                host_data = {
                    "host": str(os.uname()[1]),
                    "ip": str(socket.gethostbyname(socket.gethostname())),
                    "arc": str(platform.platform()),
                }
                cur.execute(
                    "SELECT ServerID from servers WHERE Hostname=:host AND IP=:ip",
                    host_data,
                )
                our_id = cur.fetchone()
                if not our_id:
                    cur.execute(
                        "INSERT INTO servers (Hostname, IP, Platform) VALUES (:host, :ip, :arc)",
                        host_data,
                    )
                    con.commit()
                    cur.execute(
                        "SELECT ServerID from servers WHERE Hostname=:host AND IP=:ip",
                        host_data,
                    )
                    our_id = cur.fetchone()
        return int(our_id[0])

    def put_request(self, remote_addr, remote_user_agent, request_url):
        """write request data to the sqlite date base"""
        if not self.db_active:
            msg = "put request: No DB Connection:"
            msg += " remote_addr {remote_addr},"
            msg += " remote_user_agent {remote_user_agent},"
            msg += " request_url {request_url}"
            self.log.warning(msg)
            return False
        with closing(sqlite3.connect(self.db_path)) as con:
            with closing(con.cursor()) as cur:
                req_data = {
                    "epoch": float(round(time.time(), 4)),
                    "remote_address": str(remote_addr),
                    "remote_user_agent": str(remote_user_agent),
                    "request_url": str(request_url),
                    "server_id": int(self.server_id),
                }
                cur.execute(
                    """INSERT INTO requests (
                        Epoch, RemoteAddress, RemoteUserAgent, RequestURL, ServerID
                    ) VALUES (
                        :epoch, :remote_address, :remote_user_agent, :request_url, :server_id
                    )""",
                    req_data,
                )
                con.commit()
        return True

    def get_srv_id(self):
        """get the server id for this instance of pystats"""
        return self.server_id

    def get_req_total(self):
        """get the total number of requests"""
        if not self.db_active:
            self.log.warning("get_req_total: No DB Connection")
            return None
        with closing(sqlite3.connect(self.db_path)) as con:
            with closing(con.cursor()) as cur:
                cur.execute(
                    "SELECT RequestID FROM requests ORDER BY RequestID DESC LIMIT 1"
                )
                return int(cur.fetchone()[0])

    def get_srv_total(self):
        """get total number of servers"""
        if not self.db_active:
            self.log.warning("get_srv_total: No DB Connection")
            return None
        with closing(sqlite3.connect(self.db_path)) as con:
            with closing(con.cursor()) as cur:
                cur.execute(
                    "SELECT ServerID FROM servers ORDER BY ServerID DESC LIMIT 1"
                )
                return int(cur.fetchone()[0])

    def _parse_min_max(self, pn_start, pn_count, req_total):
        """ get the min and max ids for pagination and sanitize for integers """
        min = int(pn_start)
        min = min if min > 0 else 1
        max_min = int(req_total) - int(pn_count -1 )
        min = min if min <= max_min else max_min
        max = min + int(pn_count - 1)
        return (min, max)

    def get_srvs(self, pn_start=1, pn_count=10):
        """ get all the servers: list of tuple """
        srvs_tbl = []
        min, max = self._parse_min_max(pn_start, pn_count, self.get_srv_total())
        if not self.db_active:
            self.log.warning("get_srvs: No DB Connection")
            return None
        with closing(sqlite3.connect(self.db_path)) as con:
            with closing(con.cursor()) as cur:
                sql = f"""
                    SELECT ServerID,Hostname,IP,Platform
                    FROM servers
                    WHERE ServerID BETWEEN {min} AND {max}
                    ORDER BY ServerID ASC
                """
                data = cur.execute(sql).fetchall()
        for row in data:
            srv_id = int(row[0])
            with closing(sqlite3.connect(self.db_path)) as con:
                with closing(con.cursor()) as cur:
                    sql = f"""
                        SELECT COUNT(ServerID)
                        FROM requests
                        WHERE ServerID = {srv_id}
                    """
                    srv_req_tot = cur.execute(sql).fetchone()[0]
            # ServerID,srv_req_tot,Hostname,IP,Platform
            new_rec = (srv_id,srv_req_tot,str(row[1]),str(row[2]),str(row[3]))
            srvs_tbl.append(new_rec)
        return srvs_tbl

    def get_requests(self, pn_start=1, pn_count=10):
        """ get all the requests: list of tuple """
        min, max = self._parse_min_max(pn_start, pn_count, self.get_req_total())
        if not self.db_active:
            self.log.warning("get_requests: No DB Connection")
            return None
        with closing(sqlite3.connect(self.db_path)) as con:
            with closing(con.cursor()) as cur:
                sql = f"""
                    SELECT RequestID,Epoch,RemoteAddress,RemoteUserAgent,RequestURL,ServerID
                    FROM requests
                    WHERE RequestID BETWEEN {min} AND {max}
                    ORDER BY RequestID ASC
                """
                return cur.execute(sql).fetchall()
