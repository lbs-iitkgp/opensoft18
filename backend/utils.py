import sys
import time
import cv2
import json
import copy
import img2pdf
import pre_process as pp
import parse_name as pn


class coordinate:
    x = 0
    y = 0

    def __init__(self, x, y):
        self.x = x
        self.y = y


class boundingBox:
    bound_text = ''
    box_type = ''
    words = []
    tl = coordinate(0, 0)
    tr = coordinate(0, 0)
    br = coordinate(0, 0)
    bl = coordinate(0, 0)

    def __init__(self, tl, tr, bl, br, bound_text, box_type, words):

        """
        :param tl: coordinates of top left
        :param tr: coordinates of top right
        :param bl: coordinates of bottom left
        :param br: coordinates of bottom right
        :param bound_text: The text inside the box
        :param box_type: catagorize the boxx as line(L)/word(W)
        """

        self.tl = tl
        self.tr = tr
        self.br = br
        self.bl = bl
        self.bound_text = bound_text
        self.box_type = box_type
        self.words = words

    def __repr__(self):  # object definition
        return "<boundingBox box_type:{} bound_text:{} tl:({},{}) tr:({},{}) bl:({},{}) br:({},{}) words: {} >".format(self.box_type, self.bound_text, self.tl.x, self.tl.y, 
            self.tr.x, self.tr.y, self.bl.x, self.bl.y, self.br.x, self.br.y, self.words)

    def __str__(self):  # print statement
        return "box_type:{} \nbound_text:{} \ntl:({},{}) \ntr:({},{}) \nbl:({},{}) \nbr:({},{})\nwords: {}".format(self.box_type, self.bound_text, self.tl.x, self.tl.y, 
            self.tr.x, self.tr.y, self.bl.x, self.bl.y, self.br.x, self.br.y, self.words)


def preprocess(input_image):
    """
    pre-processes the image and converts to gray-scale
    :param input_image: path to the image to be processed
    :return: out_image: processed image in cv2 format
    """
    pp.notescan_main(input_image)
    out_image = cv2.imread("output.png")
    return out_image


def get_names(in_str):
    """
    calls extract from parse_name module
    :param in_str: input string
    :return: list containing names present in the input string
    """
    return pn.extract(in_str)


def get_azure_ocr(input_image):
    azure_json = {}
    return azure_json


def parse_azure_json(azure_json):
    """
    extract data from json created by Azure
    :param azure_json: path to the json file
    :return llist: list of boundings boxes of words
    """

    data = json.load(open(azure_json))
    sentence = data["recognitionResult"]["lines"]
    slen = len(sentence)

    # initialize
    c = coordinate(0, 0)
    bb = boundingBox(c, c, c, c, "", "L", [])
    bb_word = boundingBox(c, c, c, c, "", "W", []) 
    llist = []
    for i in range(slen):
        line = sentence[i]["words"]
        line_box = sentence[i]["boundingBox"]
        bb.bound_text = sentence[i]["text"]
        bb.box_type = "L"
        bb.bl = coordinate(line_box[0], line_box[1])
        bb.br = coordinate(line_box[2], line_box[3])
        bb.tr = coordinate(line_box[4], line_box[5])
        bb.tl = coordinate(line_box[6], line_box[7])
        llen = len(line)
        for j in range(llen):
            word_box = line[j]["boundingBox"]
            word = line[j]["text"]
            bb_word.box_type = "W"
            bb_word.bl = coordinate(word_box[0], word_box[1])
            bb_word.br = coordinate(word_box[2], word_box[3])
            bb_word.tr = coordinate(word_box[4], word_box[5])
            bb_word.tl = coordinate(word_box[6], word_box[7])
            bb_word.bound_text = word
            bb.words.append(copy.deepcopy(bb_word))
        llist.append(copy.deepcopy(bb))
    return llist


def img_to_pdf(image):  # name of the image as input
    pdf_bytes = img2pdf.convert([image])
    date_string = time.strftime("%Y-%m-%d-%H:%M:%S.pdf")
    file = open(date_string, "wb")
    file.write(pdf_bytes)
    file.close()
    return date_string


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
