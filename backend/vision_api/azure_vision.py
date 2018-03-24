from PIL import Image
from io import BytesIO
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import time
import numpy

import os
from os.path import join, dirname
from dotenv import load_dotenv
load_dotenv(join(dirname(__file__), '.env'))

import requests
import operator
from sys import argv


VISION_BASE_URL = "https://westcentralus.api.cognitive.microsoft.com/vision/v1.0/"
VISION_ANALYZE_URL = VISION_BASE_URL + "analyze"
TEXT_RECOGNITION_URL = VISION_BASE_URL + "RecognizeText"
VISION_API_KEY = os.getenv('VISION_API_KEY')


def fetch_response(image_url):
  '''
  FIXME: Add support to local images, and uploads in Flask
  '''
  return(requests.post(TEXT_RECOGNITION_URL, headers={'Ocp-Apim-Subscription-Key': VISION_API_KEY}, params={'handwriting' : True}, json={'url': image_url}))

def vision_analysis(image_url):
  response = fetch_response(image_url)
  operation_url = response.headers["Operation-Location"]

  analysis = {}
  while not "recognitionResult" in analysis:
    response_final = requests.get(response.headers["Operation-Location"], headers={'Ocp-Apim-Subscription-Key': VISION_API_KEY})
    analysis       = response_final.json()
    time.sleep(1)

  polygons = [(line["boundingBox"], line["text"]) for line in analysis["recognitionResult"]["lines"]]

  plt.figure(figsize=(15,15))

  image  = Image.open(BytesIO(requests.get(image_url).content))
  ax     = plt.imshow(image)

  # FIXME
  # - Font size should be dynamically chosen for each bounding box
  # - Rather than superimposing on the original image, parts of original image inside the bounding box can just be removed.

  for polygon in polygons:
    vertices = [(polygon[0][i], polygon[0][i+1]) for i in range(0,len(polygon[0]),2)]
    text     = polygon[1]
    patch    = Polygon(vertices, closed=True,fill=False, linewidth=2, color='y')
    ax.axes.add_patch(patch)
    plt.text(vertices[0][0], vertices[0][1], text, fontsize=10, va="top")
  _ = plt.axis("off")

  plt.savefig('output.png')

if __name__ == "__main__":
  '''
  1. Get key for spell check from https://azure.microsoft.com/en-in/try/cognitive-services
     and save it in a .env file, like the one shown in .env_example file.
  2. Run this script like, `python3 azure_vision.py https://i.imgur.com/GuoPp8q.jpg`.
  '''
  image_url = argv[1] # For example, "https://i.imgur.com/GuoPp8q.jpg"
  vision_analysis(image_url)
