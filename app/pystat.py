#!/usr/bin/env python3
""" 
pystats: Flask app to get system metrics on page load with request
logging for testing K8s Load Balancers, Statefulsets, and
Persistent Volumes or custom prometheus metrics endpoint.
"""
import os
import atexit
import yaml
from flask import (
    Flask,
    jsonify,
    make_response,
    render_template,
    request,
    send_from_directory,
)
from waitress import serve
from src.stats import Stats
from src.logger import get_logger
from src.cli import parse_cfg
from src.requests import Requests


LOG = get_logger()
CFG = parse_cfg()
STATS = Stats()
REQS = Requests(CFG.db_path)
app = Flask(__name__)


@app.route("/")
def stats():
    """stats - node stats"""
    REQS.put_request(request.remote_addr, request.user_agent, request.url)
    fast = True if request.args.get("fast") == "true" else False
    return render_template(
        "stats.html",
        stats=STATS.get_stats(fast),
        req_total=REQS.get_req_total(),
    )


@app.route("/servers")
def servers():
    REQS.put_request(request.remote_addr, request.user_agent, request.url)
    """ servers - pystats servers """
    url_pn_start = request.args.get("pnstart", 1, int)
    url_pn_count = request.args.get("pncount", 10, int)
    return render_template(
        "servers.html",
        srv_tbl=REQS.get_srvs(url_pn_start, url_pn_count),
        pn_start=url_pn_start,
        pn_count=url_pn_count,
        req_total=REQS.get_srv_total(),
    )


@app.route("/requests")
def requests():
    REQS.put_request(request.remote_addr, request.user_agent, request.url)
    """ requests - pystats requests """
    url_pn_start = request.args.get("pnstart", 1, int)
    url_pn_count = request.args.get("pncount", 10, int)
    return render_template(
        "requests.html",
        req_tbl=REQS.get_requests(url_pn_start, url_pn_count),
        pn_start=url_pn_start,
        pn_count=url_pn_count,
        req_total=REQS.get_req_total(),
    )


@app.route("/json")
def json_out():
    """json - output json"""
    REQS.put_request(request.remote_addr, request.user_agent, request.url)
    return jsonify(STATS.get_stats())


@app.route("/yaml")
def yaml_out():
    """yaml - output yaml"""
    response = make_response(yaml.dump(STATS.get_stats(), indent=2), 200)
    response.mimetype = "text/plain"
    REQS.put_request(request.remote_addr, request.user_agent, request.url)
    return response


@app.errorhandler(404)
def not_found(err):
    """404 page"""
    REQS.put_request(request.remote_addr, request.user_agent, request.url)
    return render_template("404.html", error=err)


@app.route("/favicon.ico")
def favicon():
    """favicon image"""
    return send_from_directory(
        os.path.join(app.root_path, "static/images"),
        "favicon.ico",
        mimetype="image/vnd.microsoft.icon",
    )


@app.route("/favicon.jpeg")
def fav_image():
    """favicon image large"""
    return send_from_directory(
        os.path.join(app.root_path, "static/images"),
        "favicon.jpeg",
        mimetype="image/vnd.microsoft.icon",
    )


def on_shutdown():
    """ exit message """
    LOG.debug("Exiting... Server_ID: %s", REQS.get_srv_id())


if __name__ == "__main__":
    LOG.debug("Starting... Server_ID: %s", REQS.get_srv_id())
    atexit.register(on_shutdown)
    serve(app, host=CFG.srv_socket_ip, port=CFG.srv_socket_port)
