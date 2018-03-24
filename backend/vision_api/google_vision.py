import io
import os
import pickle

# Imports the Google Cloud client library
from google.cloud import vision
from google.cloud.vision import types

from utilities.digicon_classes import image_location

# Instantiates a client
CLIENT = vision.ImageAnnotatorClient()
# google_sample.pkl stores the returned types.AnnotateImageResponse object for frontend/src/samples/1.jpg
# Saves us unnecessary calls to the API while testing
with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'google_sample.pkl'), 'rb') as input:
    SAMPLE_RESPONSE = pickle.load(input)

def parse_google_ocr(ocr_response):
    print(type(ocr_response))
    return ocr_response

def get_google_ocr(input_image):
    # The name of the image file to annotate
    file_name = os.path.join(os.path.join(input_image.images_path, input_image.image_name))

    # Loads the image into memory
    with io.open(file_name, 'rb') as image_file:
        content = image_file.read()

    image = types.Image(content=content)

    # Performs text detection on the image file
    # response = CLIENT.document_text_detection(image=image)
    # with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'google_sample.pkl'), 'wb') as output:
    #     pickle.dump(response, output, pickle.HIGHEST_PROTOCOL)
    response = SAMPLE_RESPONSE
    ocr_data = parse_google_ocr(response.full_text_annotation)
    return ocr_data

if __name__ == '__main__':
    print("hello from google_vision!")
