# -*- coding: utf-8 -*-
"""
Main flask process
"""
from flask import Flask, jsonify
import requests

APP = Flask(__name__)
REQUESTS_SESSION = requests.Session()

@APP.route('/', methods=['GET'])
def index():
    """
    Handle http request to root
    """
    return "Hello!"

if __name__ == "__main__":
    APP.run(debug=True, host='0.0.0.0', port=5010, use_reloader=False)
