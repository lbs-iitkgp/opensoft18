import sys
import cv2
import json
import copy
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

    def __init__(self, tl, tr, bl, br, bound_text):
        
        """
        :param tl: coordinates of top left
        :param tr: coordinates of top right
        :param bl: coordinates of bottom left
        :param br: coordinates of bottom right
        """
        
        self.tl = tl
        self.tr = tr
        self.br = br
        self.bl = bl
        self.bound_text = bound_text

    def __repr__(self): #object definition
        return "<boundingBox bound_text:%s tl:(%s,%s) tr:(%s,%s) bl:(%s,%s) br:(%s,%s)>" %(self.bound_text,self.tl.x,self.tl.y,
            self.tr.x,self.tr.y,self.bl.x,self.bl.y,self.br.x,self.br.y)

    def __str__(self): #print statement
        return "bound_text:%s \n tl:(%s,%s) \n tr:(%s,%s) \n bl:(%s,%s) \n br:(%s,%s)" %(self.bound_text,self.tl.x,self.tl.y,
            self.tr.x,self.tr.y,self.bl.x,self.bl.y,self.br.x,self.br.y)

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
    """
    extract data from json created by Azure
    :param azure_json: path to the json file
    :return llist: list of boundings boxes of words
    """

    data = json.load(open(azure_json))
    sentence = data["recognitionResult"]["lines"]
    l = len(sentence)

    #initialize
    c = coordinate(0,0)
    bb = boundingBox(c,c,c,c,"")
    llist = []
    for i in range(l):
        line = data["recognitionResult"]["lines"][i]["words"]
        llen = len(line)
        for j in range(llen):
            word_box = line[j]["boundingBox"]
            word = line[j]["text"]
            bb.bl = coordinate(word_box[0],word_box[1])
            bb.br = coordinate(word_box[2],word_box[3])
            bb.tr = coordinate(word_box[4],word_box[5])
            bb.tl = coordinate(word_box[6],word_box[7])
            bb.bound_text = word
            llist.append(copy.deepcopy(bb))
    return llist

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
