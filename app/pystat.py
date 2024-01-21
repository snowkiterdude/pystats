#!/usr/bin/env python3
""" pystats - return system stats """


# TODO add logging remove print statements


import os
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
from src.stat_requests import StatRequests

stats = Stats()
app = Flask(__name__)


def put_request(remote_addr, user_agent, url):
    """ put http request data to sqlite data base """
    with StatRequests() as stat_requests:
        stat_requests.put_request(remote_addr, user_agent, url)


@app.route("/")
def home():
    """home - output html"""
    if request.args.get("fast") == "true":
        return render_template("home.html", stats=stats.get_stats(True))
    put_request(request.remote_addr, request.user_agent, request.url)
    return render_template("home.html", stats=stats.get_stats(False))


@app.route("/json")
def json_out():
    """json - ouput json"""
    put_request(request.remote_addr, request.user_agent, request.url)
    return jsonify(stats.get_stats())


@app.route("/yaml")
def yaml_out():
    """yaml - output yaml"""
    response = make_response(yaml.dump(stats.get_stats(), indent=2), 200)
    response.mimetype = "text/plain"
    put_request(request.remote_addr, request.user_agent, request.url)
    return response


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


if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=8080)
