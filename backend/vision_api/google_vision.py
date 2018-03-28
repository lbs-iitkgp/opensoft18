import io
import os
import pickle
from enum import Enum
import cv2

# Imports the Google Cloud client library
from google.cloud import vision
from google.cloud.vision import types

from utilities.digicon_classes import coordinate, boundingBox, image_location

class FeatureType(Enum):
    PAGE = 1
    BLOCK = 2
    PARA = 3
    WORD = 4
    SYMBOL = 5

# Instantiates a client
CLIENT = vision.ImageAnnotatorClient()
# google_sample.pkl stores the returned types.AnnotateImageResponse object for frontend/src/samples/1.jpg
# Saves us unnecessary calls to the API while testing
# with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'google_sample.pkl'), 'rb') as input:
#     SAMPLE_RESPONSE = pickle.load(input)

def parse_google_ocr(ocr_response):
    # Collect specified feature bounds by enumerating all document features
    sentence_bounds = []
    word_bounds = []
    all_text = ''
    temp_coordinate = coordinate(0, 0)
    for page in ocr_response.pages:
        for block in page.blocks:
            for paragraph in block.paragraphs:
                paragraph_bounds = []
                sentence_string = ''
                sentence_bbox = paragraph.bounding_box
                for word in paragraph.words:
                    word_string = ''
                    for symbol in word.symbols:
                        word_string += symbol.text
                    sentence_string = sentence_string + word_string + ' '
                    all_text = all_text + word_string + ' '
                    word_bbox = word.bounding_box
                    word_language = word.property.detected_languages[0].language_code
                    word_bbox_object = boundingBox(
                        coordinate(word_bbox.vertices[0].x, word_bbox.vertices[0].y),
                        coordinate(word_bbox.vertices[1].x, word_bbox.vertices[1].y),
                        coordinate(word_bbox.vertices[3].x, word_bbox.vertices[3].y),
                        coordinate(word_bbox.vertices[2].x, word_bbox.vertices[2].y),
                        word_string, 'W', []
                    )
                    word_bbox_object.language = str(word_language)
                    word_bounds.append(word_bbox_object)
                    paragraph_bounds.append(word_bbox_object)
                sentence_bbox_object = boundingBox(
                    coordinate(sentence_bbox.vertices[0].x, sentence_bbox.vertices[0].y),
                    coordinate(sentence_bbox.vertices[1].x, sentence_bbox.vertices[1].y),
                    coordinate(sentence_bbox.vertices[3].x, sentence_bbox.vertices[3].y),
                    coordinate(sentence_bbox.vertices[2].x, sentence_bbox.vertices[2].y),
                    sentence_string, 'L', paragraph_bounds
                )
                sentence_bounds.append(sentence_bbox_object)
    all_bound = boundingBox(temp_coordinate, temp_coordinate, temp_coordinate, temp_coordinate, all_text, 'A', word_bounds)
    return [all_bound] + word_bounds + sentence_bounds

def get_google_ocr(input_image):
    # The name of the image file to annotate
    if os.path.exists(os.path.join(input_image.temp_path, "white_" + input_image.image_name)):
        file_name = os.path.join(input_image.temp_path, "white_" + input_image.image_name)
    else:
        file_name = os.path.join(input_image.images_path, input_image.image_name)

    # cv2_file = cv2.imread(file_name)
    # cv2.imshow('OCR input image', cv2_file)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    # Loads the image into memory
    with io.open(file_name, 'rb') as image_file:
        content = image_file.read()

    image = types.Image(content=content)

    # Performs text detection on the image file
    response = CLIENT.document_text_detection(image=image)
    # with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'google_sample.pkl'), 'wb') as output:
    #     pickle.dump(response, output, pickle.HIGHEST_PROTOCOL)
    # response = SAMPLE_RESPONSE
    ocr_data = parse_google_ocr(response.full_text_annotation)
    return ocr_data

if __name__ == '__main__':
    print("hello from google_vision!")
