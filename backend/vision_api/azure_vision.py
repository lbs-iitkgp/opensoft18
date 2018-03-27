import time
import json
import copy
import os
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

import requests
from sys import argv

from utilities.digicon_classes import coordinate, boundingBox, image_location

VISION_BASE_URL = "https://westcentralus.api.cognitive.microsoft.com/vision/v1.0/"
VISION_ANALYZE_URL = VISION_BASE_URL + "analyze"
TEXT_RECOGNITION_URL = VISION_BASE_URL + "RecognizeText"
VISION_API_KEY = os.getenv('VISION_API_KEY')

def fetch_response(input_image):
    image_data = open(input_image, 'rb').read()
    return(requests.post(
        TEXT_RECOGNITION_URL,
        headers = {
            'Ocp-Apim-Subscription-Key': VISION_API_KEY,
            'Content-Type': 'application/octet-stream'
        },
        params={'handwriting' : True},
        data=image_data
    ))

def parse_azure_ocr(azure_json):
    """
    extract data from json created by Azure
    :param azure_json: path to the json file
    :return llist: list of boundings boxes of words
    """
    data = azure_json
    sentence = data["recognitionResult"]["lines"]
    slen = len(sentence)

    # initialize
    c = coordinate(0, 0)
    bb = boundingBox(c, c, c, c, "", "W", [])
    bbl = boundingBox(c, c, c, c, "", "W", [])
    llist = []
    all_text = ''
    all_list = []
    for i in range(slen):
        line = sentence[i]["words"]
        line_box = sentence[i]["boundingBox"]
        bbl.bound_text = sentence[i]["text"]
        bbl.box_type = "L"
        bbl.bl = coordinate(line_box[0], line_box[1])
        bbl.br = coordinate(line_box[2], line_box[3])
        bbl.tr = coordinate(line_box[4], line_box[5])
        bbl.tl = coordinate(line_box[6], line_box[7])
        # llist.append(copy.deepcopy(bbl))
        llen = len(line)
        word_objects_list = []
        for j in range(llen):
            word_box = line[j]["boundingBox"]
            word = line[j]["text"]
            bb.box_type = "W"
            bb.bl = coordinate(word_box[0], word_box[1])
            bb.br = coordinate(word_box[2], word_box[3])
            bb.tr = coordinate(word_box[4], word_box[5])
            bb.tl = coordinate(word_box[6], word_box[7])
            bb.bound_text = word
            all_text = all_text + bb.bound_text + " "
            bb.bb_children = []
            word_objects_list.append(bb)
            all_list.append(bb)
            llist.append(copy.deepcopy(bb))
        bbl.bb_children = word_objects_list
        llist.append(copy.deepcopy(bbl))
    llist.insert(0, boundingBox(c, c, c, c, all_text, "A", all_list))
    return llist

def get_azure_ocr(input_image):
    if os.path.exists(os.path.join(input_image.temp_path, "white_" + input_image.image_name)):
        file_name = os.path.join(input_image.temp_path, "white_" + input_image.image_name)
    else:
        file_name = os.path.join(input_image.images_path, input_image.image_name)

    response = fetch_response(file_name)
    operation_url = response.headers["Operation-Location"]
    operation_id = operation_url.split('/')[-1]

    analysis = {}
    while not "recognitionResult" in analysis:
        response_final = requests.get(
            response.headers["Operation-Location"],
            headers={'Ocp-Apim-Subscription-Key': VISION_API_KEY},
            params={'operationId': operation_id}
        )
        analysis = response_final.json()
        time.sleep(1)
    ocr_data = parse_azure_ocr(analysis)
    return ocr_data

    # polygons = [(line["boundingBox"], line["text"]) for line in analysis["recognitionResult"]["lines"]]
    # plt.figure(figsize=(15,15))
    # image = Image.open(BytesIO(requests.get(file_name).content))
    # ax = plt.imshow(image)
    # for polygon in polygons:
    #     vertices = [(polygon[0][i], polygon[0][i+1]) for i in range(0,len(polygon[0]),2)]
    #     text = polygon[1]
    #     patch = Polygon(vertices, closed=True,fill=False, linewidth=2, color='y')
    #     ax.axes.add_patch(patch)
    #     plt.text(vertices[0][0], vertices[0][1], text, fontsize=10, va="top")
    # _ = plt.axis("off")
    # plt.savefig('output.png')

if __name__ == "__main__":
    '''
    1. Get key for spell check from https://azure.microsoft.com/en-in/try/cognitive-services
      and save it in a .env file, like the one shown in .env_example file.
    2. Run this script like, `python3 azure_vision.py <path-to-image>`.
    '''
    input_image = argv[1]
    get_azure_ocr(input_image)
