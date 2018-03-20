import sys
import cv2
import pre_process as pp


class coordinate:
    x = 0
    y = 0

    def __init__(self, x, y):
        self.x = x
        self.y = y

class boundingBox:
    bound_text = ''
    tl = coordinate(0,0)
    tr = coordinate(0,0)
    br = coordinate(0,0)
    bl = coordinate(0,0)

    # write __init__ function

def preprocess(input_image):
    """
    pre-processes the image and converts to gray-scale
    :param input_image: path to the image to be processed
    :return: out_image: processed image in cv2 format
    """
    pp.notescan_main(input_image)
    out_image = cv2.imread("output.png")
    return out_image

def get_azure_ocr(input_image):
    azure_json = {}
    return azure_json

def parse_azure_json(azure_json):
    # Check for validity of returned output
    # return a list of all bounding boxes with the respective contained text
    # Use the bounding box class to do the same
    return []

def get_parallel_boxes(bounding_boxes):
    list_of_boxes = []
    return list_of_boxes

def get_lexigram(bounding_boxes):
    lexigram_json = {}
    return lexigram_json

def fix_spelling(bounding_box):
    # return bounding box
    return bounding_box

def replace_image_with_text(input_image, list_of_bounding_boxes):
    in_image = cv2.imread(input_image)
    out_image = in_image
    return out_image

if __name__ == '__main__':
    print("Hello!")
