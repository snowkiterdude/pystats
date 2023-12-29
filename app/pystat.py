#!/usr/bin/env python3
""" pystats - return system stats """
import yaml
from flask import Flask, jsonify, make_response, render_template, request
from waitress import serve
from src.stats import Stats

stats = Stats()
app = Flask(__name__)

@app.route("/")
def home():
    """home - output html"""
    if request.args.get('fast') == "true":
        return render_template("home.html", stats=stats.get_stats(True))
    return render_template("home.html", stats=stats.get_stats(False))

@app.route("/json")
def json_out():
    """json - ouput json"""
    return jsonify(stats.get_stats())


@app.route("/yaml")
def yaml_out():
    """yaml - output yaml"""
    response = make_response(yaml.dump(stats.get_stats(), indent=2), 200)
    response.mimetype = "text/plain"
    return response


if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=8080)





# python:3.10.13-alpine3.19
# apk add build-base linux-headers
# python -m pip install psutil



