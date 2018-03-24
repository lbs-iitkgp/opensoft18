#!/usr/bin/env python3

import time
import json
import copy
import operator

import numpy as np
import img2pdf
import cv2

import pre_process as pp
import parse_name as pn
import lexigram
import spellcheck_azure
import spellcheck_custom

from utilities.digicon_classes import coordinate, boundingBox, image_location

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
    bb = boundingBox(c, c, c, c, "", "W")
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
        llist.append(copy.deepcopy(bb))
        llen = len(line)
        for j in range(llen):
            word_box = line[j]["boundingBox"]
            word = line[j]["text"]
            bb.box_type = "W"
            bb.bl = coordinate(word_box[0], word_box[1])
            bb.br = coordinate(word_box[2], word_box[3])
            bb.tr = coordinate(word_box[4], word_box[5])
            bb.tl = coordinate(word_box[6], word_box[7])
            bb.bound_text = word
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
    """
    Extracts all possible metadata from all the bounding boxes
    :param bounding_box: a bounding box with bound_text
    :return: bounding_box: a bounding box with spell-fixed bound_text
    """

    lexigram_json = {}
    for bounding_box in bounding_boxes:
        individual_json = lexigram.extract_metadata_json(bounding_box.bound_text)
        for key in individual_json:
            if key not in lexigram_json:
                lexigram_json[key] = set()
            lexigram_json[key] = lexigram_json[key].union(individual_json[key])

    return lexigram_json

def fix_spelling(bounding_box):
    """
    Fixes spelling based on Azure spellchecker, metadata extraction and custom spellchecker
    :param bounding_box: a bounding box with bound_text
    :return: bounding_box: a bounding box with spell-fixed bound_text
    """

    text = bounding_box.bound_text
    text = spellcheck_azure.make_correction(text)
    if lexigram.extract_metadata_json(text):
        bounding_box.bound_text = text
        return bounding_box

    text = spellcheck_custom.spellcor(text)
    bounding_box.bound_text = text
    return bounding_box

def crop_image(input_image,x1,x2,y1,y2):
    crop_out = input_image[y1:y2, x1:x2]
    return crop_out

def remove_text(input_image, bb_object):

    if bb_object.box_type == 'L':
        return input_image

    elif bb_object.box_type == 'W':
        img = cv2.imread(input_image, 0)
        x1 = bb_object.tl.x
        x2 = bb_object.br.x
        y1 = bb_object.tl.y
        y2 = bb_object.br.y
        crop = crop_image('img',x1,x2,y1,y2)
        kernel = np.ones((5,5), np.uint8)
        img_erosion = cv2.erode(crop, kernel, iterations=5)
        img_dilation = cv2.dilate(img_erosion, kernel, iterations=60)
        out_image = img_dilation
        return out_image

def draw_box(in_img, l_boxes):
    """
    draw red bounding boxes for line ('L') box_types
    :param in_img: input image in opencv format
    :param l_boxes: list of bounding boxes to be drawn
    :return: in_img: image (in opencv format) after drawing boxes in red
    """
    red = (0, 0, 255)  # opencv follows bgr pattern
    for box in l_boxes:
        if box.box_type == 'L':
            vertices = np.array([[box.tl.x, box.tl.y], [box.tr.x, box.tr.y], [box.br.x, box.br.y],
                                 [box.bl.x, box.bl.y]], np.int32)
            cv2.polylines(in_img, [vertices], True, red, thickness=1, lineType=cv2.LINE_AA)

    # uncomment below lines while debugging
    # cv2.imshow("debug", in_img)
    # cv2.waitKey(0)

    return in_img


def put_text(in_img, l_boxes):
    """
    put extracted text (in black) over the place of original text
    :param in_img: cleaned image in opencv format
    :param l_boxes: list of bounding boxes
    :return: out_img: a separate image with text placed at right places
    """
    out_img = in_img
    font = cv2.FONT_HERSHEY_DUPLEX
    font_color = (0, 0, 0)
    # multiplying factor used to calculate font_scale in relation to height
    factor = .03

    for box in l_boxes:
        if box.box_type == 'W':

            height = box.bl.y - box.tl.y
            width = box.tr.x - box.tl.x

            font_scale = factor * height
            text_size = cv2.getTextSize(box.bound_text, font, font_scale, thickness=1)
            # to put text in middle of the bounding box
            text_x_center = int(box.bl.x + ((width / 2) - (text_size[0][0] / 2)))
            text_y_center = int(box.bl.y - ((height / 2) - (text_size[0][1] / 2)))

            cv2.putText(out_img, box.bound_text, (text_x_center, text_y_center), font, font_scale, font_color,
                        thickness=1, lineType=cv2.LINE_AA)

    # while debugging and calibrating, uncomment below lines
    # cv2.imshow("test", out_img)
    # cv2.waitKey(0)
    return out_img

def add_to_pipeline(images_path, temp_path, image_name):
    print(image_name)
    input_image = image_location(images_path, temp_path, image_name)
    # Pre-processing
    preprocessed_image = preprocess(input_image)

if __name__ == '__main__':
    print("hello!")
