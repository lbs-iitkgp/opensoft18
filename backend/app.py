# -*- coding: utf-8 -*-
"""
Main flask process
"""
from flask import Flask, url_for, send_file, send_from_directory, request, Response, jsonify
from flask_cors import CORS
import base64
import time
import logging, os
import requests
from flask_socketio import SocketIO, emit

from utils import add_to_pipeline, continue_pipeline, finish_pipeline, do_download, do_nlp

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app)

REQUESTS_SESSION = requests.Session()
file_handler = logging.FileHandler('server.log')
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.DEBUG)

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
PROJECT_HOME = os.path.dirname(os.path.realpath(__file__))
UPLOAD_FOLDER = '{}/input_images'.format(PROJECT_HOME)
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

# def stream_output(upload_folder, temp_folder, file_name):
#     for output_index, output_object in enumerate(add_to_pipeline(upload_folder, temp_folder, file_name)):
#         if output_index == 0 or output_index == 1:
#             with open(output_object, "rb") as image_file:
#                 encoded_image = base64.b64encode(image_file.read())
#             yield encoded_image
#         else:
#             yield output_object

@app.route('/', methods=['GET'])
def index():
    """
    Handle http request to root
    """
    return "Hello!"

@app.route('/upload', methods = ['POST'])
def api_root():
    app.logger.info(PROJECT_HOME)
    # try:
    img = request.files['image']
    print(img)
    if request.method == 'POST' and img and allowed_file(img.filename):
        app.logger.info(app.config['UPLOAD_FOLDER'])
        img = request.files['image']
        create_new_folder(app.config['UPLOAD_FOLDER'])
        create_new_folder(app.config['TEMP_FOLDER'])
        file_name = str(time.time()).replace('.', '') + "_" + img.filename.replace('/','')
        saved_path = os.path.join(app.config['UPLOAD_FOLDER'], file_name)
        app.logger.info("saving {}".format(saved_path))
        img.save(saved_path)
        # return Response(stream_output(app.config['UPLOAD_FOLDER'], app.config['TEMP_FOLDER'], file_name))
        bbox_image, all_text = add_to_pipeline(app.config['UPLOAD_FOLDER'], app.config['TEMP_FOLDER'], file_name, socketio)
        with open(bbox_image, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read())
        return jsonify(
            image=encoded_image.decode("utf-8"),
            image_name=file_name,
            all_text=all_text
        )
    else:
        return Response("No image sent", status=401)
    # except Exception as e:
    #     app.logger.info(e)
    #     return Response("Error occured:- "+str(e), status=400)

@app.route('/continue/<string:image_id>', methods = ['GET'])
def api_continue(image_id):
    app.logger.info(PROJECT_HOME)
    # try:
    replaced_image, fresh_image, lexigram_json, dosage_json = continue_pipeline(app.config['UPLOAD_FOLDER'], app.config['TEMP_FOLDER'], image_id, socketio)
    with open(replaced_image, "rb") as image_file:
        encoded_replaced_image = base64.b64encode(image_file.read())
    with open(fresh_image, "rb") as image_file:
        encoded_fresh_image = base64.b64encode(image_file.read())
    return jsonify(
        replaced_image=encoded_replaced_image.decode("utf-8"),
        fresh_image=encoded_fresh_image.decode("utf-8"),
        image_name=image_id,
        lexigram_data=lexigram_json,
        dosage_data=dosage_json
    )    
    # except Exception as e:
    #     print(e)
    #     app.logger.info(e)
    #     return ("Error occured:- "+str(e), 400, {})

@app.route('/finish/<string:image_id>', methods = ['GET'])
def api_finish(image_id):
    app.logger.info(PROJECT_HOME)
    # try:
    final_json = finish_pipeline(app.config['UPLOAD_FOLDER'], app.config['TEMP_FOLDER'], image_id, socketio)
    return jsonify(
        image_name=image_id
    )
    # except Exception as e:
    #     app.logger.info(e)
    #     return ("Error occured:- "+str(e), 400, {})

@app.route('/donlp/<string:image_id>', methods = ['GET'])
def donlp(image_id):
    app.logger.info(PROJECT_HOME)
    # try:
    nlp_result = do_nlp(app.config['UPLOAD_FOLDER'], app.config['TEMP_FOLDER'], image_id, socketio)
    return jsonify(
        image_name=image_id,
        nlp_result=nlp_result
    )
    # except Exception as e:
    #     app.logger.info(e)
    #     return ("Error occured:- "+str(e), 400, {})

@app.route('/download/<string:image_id>/<int:download_type>', methods = ['GET'])
def download_asset(image_id, download_type):
    app.logger.info(PROJECT_HOME)
    try:
        download_path = do_download(app.config['UPLOAD_FOLDER'], app.config['TEMP_FOLDER'], image_id, download_type)
        return send_file(download_path)
    except Exception as e:
        app.logger.info(e)
        return ("Error occured:- "+str(e), 400, {})

def heavy():  # we can put our entire pipeline here
	time.sleep(2)
	emit('final', "heavy done..final image is here")


@socketio.on('sending', namespace='/test')
def handle(data):
	emit('success','connect hogaya '+str(data))
	heavy()   # time consuming function here

if __name__ == "__main__":
    # app.run(debug=True, host='0.0.0.0', port=8080, use_reloader=False)
    socketio.run(app,debug=True, host='0.0.0.0', port=8080, use_reloader=False)
