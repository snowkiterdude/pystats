#!/usr/bin/env python3
""" pystats - return system stats """
import yaml
from flask import Flask, jsonify, make_response
from waitress import serve
from src.stats_html import StatsHtml

HTML = StatsHtml()
app = Flask(__name__)


@app.route("/")
def home():
    """home - output html"""
    return HTML.get_html()


@app.route("/json")
def json_out():
    """json - ouput json"""
    return jsonify(HTML.get_stats())


@app.route("/yaml")
def yaml_out():
    """yaml - output yaml"""
    response = make_response(yaml.dump(HTML.get_stats(), indent=2), 200)
    response.mimetype = "text/plain"
    return response


if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=8080)
