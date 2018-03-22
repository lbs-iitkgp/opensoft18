# -*- coding: utf-8 -*-
"""
Main flask process
"""
from flask import Flask, url_for, send_from_directory, request, jsonify
from flask_cors import CORS
import requests
import utils
import imghdr
import time
import logging, os

APP = Flask(__name__)
CORS(APP)
REQUESTS_SESSION = requests.Session()
file_handler = logging.FileHandler('server.log')
APP.logger.addHandler(file_handler)
APP.logger.setLevel(logging.INFO)

PROJECT_HOME = os.path.dirname(os.path.realpath(__file__))
UPLOAD_FOLDER = '{}/image'.format(PROJECT_HOME)
APP.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def create_new_folder(local_dir):
    newpath = local_dir
    if not os.path.exists(newpath):
        os.makedirs(newpath)
    return newpath

@APP.route('/', methods=['GET'])
def index():
    """
    Handle http request to root
    """
    return "Hello!"

@APP.route('/upload', methods = ['POST'])
def api_root():
    APP.logger.info(PROJECT_HOME)
    if request.method == 'POST' and request.files['image']:
        APP.logger.info(APP.config['UPLOAD_FOLDER'])
        img = request.files['image']
        imgname = time.strftime("%Y%m%d-%H%M%S")
        x = imghdr.what(img)
        img_name=imgname+'.'+x
        create_new_folder(APP.config['UPLOAD_FOLDER'])
        saved_path = os.path.join(APP.config['UPLOAD_FOLDER'], img_name)
        APP.logger.info("saving {}".format(saved_path))
        img.save(saved_path)
        return send_from_directory(APP.config['UPLOAD_FOLDER'],img_name, as_attachment=True)
    else:
        return {'error': 'bad request'}

if __name__ == "__main__":
    APP.run(debug=True, host='0.0.0.0', port=8080, use_reloader=False)
