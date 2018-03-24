# -*- coding: utf-8 -*-
"""
Main flask process
"""
from flask import Flask, url_for, send_from_directory, request
import time
import logging, os
import requests
from utils import add_to_pipeline

app = Flask(__name__)
REQUESTS_SESSION = requests.Session()
file_handler = logging.FileHandler('server.log')
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
PROJECT_HOME = os.path.dirname(os.path.realpath(__file__))
UPLOAD_FOLDER = '{}/images'.format(PROJECT_HOME)
TEMP_FOLDER = '{}/temp_images'.format(PROJECT_HOME)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['TEMP_FOLDER'] = TEMP_FOLDER

def create_new_folder(local_dir):
    newpath = local_dir
    if not os.path.exists(newpath):
        os.makedirs(newpath)
    return newpath

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET'])
def index():
    """
    Handle http request to root
    """
    return "Hello!"

@app.route('/upload', methods = ['POST'])
def api_root():
    app.logger.info(PROJECT_HOME)
    try:
        img = request.files['image']
        if request.method == 'POST' and img and allowed_file(img.filename):
            app.logger.info(app.config['UPLOAD_FOLDER'])
            img = request.files['image']
            create_new_folder(app.config['UPLOAD_FOLDER'])
            create_new_folder(app.config['TEMP_FOLDER'])
            file_name = str(time.time()).replace('.', '') + "_" + img.filename.replace('/','')
            saved_path = os.path.join(app.config['UPLOAD_FOLDER'], file_name)
            app.logger.info("saving {}".format(saved_path))
            img.save(saved_path)
            add_to_pipeline(app.config['UPLOAD_FOLDER'], app.config['TEMP_FOLDER'], file_name)
            return ("Image uploaded successfully", 200, {})
        else:
            return ("No image sent", 401, {})
    except Exception as e:
        app.logger.info(e)
        return ("Error occured:- "+str(e), 400, {})

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8080, use_reloader=False)
