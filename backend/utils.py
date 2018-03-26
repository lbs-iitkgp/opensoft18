#!/usr/bin/env python3

import time
import json
import operator
import os
import numpy as np
import img2pdf
import cv2
import pickle

import pre_process as pp
from spellcheck import parse_name as pn
from utilities.digicon_classes import coordinate, boundingBox, image_location
from vision_api import google_vision, azure_vision
from spellcheck import lexigram, spellcheck_azure, spellcheck_custom

def preprocess(input_image):
    """
    pre-processes the image and converts to gray-scale
    :param input_image: path to the image to be processed
    :return: out_image: processed image in cv2 format
    """
    pp.notescan_main(input_image)

def get_names(in_str):
    """
    calls extract from parse_name module
    :param in_str: input string
    :return: list containing names present in the input string
    """
    return pn.extract(in_str)

def img_to_pdf(image):  # name of the image as input
    pdf_bytes = img2pdf.convert([image])
    date_string = time.strftime("%Y-%m-%d-%H:%M:%S.pdf")
    file = open(date_string, "wb")
    file.write(pdf_bytes)
    file.close()
    return date_string

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
    # text = spellcheck_azure.make_correction(text)
    if lexigram.extract_metadata_json(text):
        bounding_box.bound_text = text
        return bounding_box

    text = spellcheck_custom.spellcor(text)
    bounding_box.bound_text = text
    return bounding_box

def crop_image(input_image, x1, x2, y1, y2):
    crop_out = input_image[y1:y2, x1:x2]
    return crop_out

def remove_text(input_image, bb_object):
    if bb_object.box_type == 'W':
        img = input_image
        x1 = bb_object.tl.x
        x2 = bb_object.br.x
        y1 = bb_object.tl.y
        y2 = bb_object.br.y
        crop = crop_image(img, x1, x2, y1, y2)
        kernel = np.ones((5,5), np.uint8)
        # crop = cv2.erode(crop, kernel, iterations=5)
        crop = cv2.dilate(crop, kernel, iterations=60)
        # crop = cv2.inpaint(crop, crop, 3, cv2.INPAINT_TELEA)
        input_image[y1:y2, x1:x2] = crop

def draw_box(in_img, l_boxes, l_type='W'):
    """
    draw red bounding boxes for line ('W') box_types
    :param in_img: input image in opencv format
    :param l_boxes: list of bounding boxes to be drawn
    :return: in_img: image (in opencv format) after drawing boxes in red
    """
    red = (0, 0, 255)  # opencv follows bgr pattern
    for box in l_boxes:
        if box.box_type == l_type:
            vertices = np.array([[box.tl.x, box.tl.y], [box.tr.x, box.tr.y], [box.br.x, box.br.y],
                                 [box.bl.x, box.bl.y]], np.int32)
            cv2.polylines(in_img, [vertices], True, red, thickness=1, lineType=cv2.LINE_AA)
    # uncomment below lines while debugging
    # cv2.imshow("debug", in_img)
    # cv2.waitKey(0)
    return in_img

def put_text(in_img, bbox):
    """
    put extracted text (in black) over the place of original text
    :param in_img: cleaned image in opencv format
    :param bbox: bounding box
    :return: out_img: a separate image with text placed at right places
    """
    out_img = in_img
    font = cv2.FONT_HERSHEY_DUPLEX
    font_color = (0, 0, 0)
    # multiplying factor used to calculate font_scale in relation to height
    factor = .03

    height = bbox.bl.y - bbox.tl.y
    width = bbox.tr.x - bbox.tl.x

    font_scale = factor * height
    text_size = cv2.getTextSize(bbox.bound_text, font, font_scale, thickness=1)
    # to put text in middle of the bounding box
    text_x_center = int(bbox.bl.x + ((width / 2) - (text_size[0][0] / 2)))
    text_y_center = int(bbox.bl.y - ((height / 2) - (text_size[0][1] / 2)))

    cv2.putText(
        out_img, bbox.bound_text, (text_x_center, text_y_center),
        font, font_scale, font_color, thickness=1, lineType=cv2.LINE_AA
    )

    # while debugging and calibrating, uncomment below lines
    # cv2.imshow("test", out_img)
    # cv2.waitKey(0)
    return out_img

def add_to_pipeline(images_path, temp_path, image_name):
    print(image_name)
    input_image = image_location(images_path, temp_path, image_name)
    # Pre-processing
    # preprocessed_image = preprocess(input_image)
    preprocessed_image = input_image

    # Get OCR data
    ocr_data = google_vision.get_google_ocr(preprocessed_image)
    # ocr_data = azure_vision.get_azure_ocr(preprocessed_image)
    with open(os.path.join(input_image.images_path, input_image.image_id + '.pkl'), 'wb') as pkl_output:
        pickle.dump(ocr_data, pkl_output, pickle.HIGHEST_PROTOCOL)

    # Draw bounding boxes around words
    bbl_image_object = cv2.imread(
        os.path.join(preprocessed_image.images_path, preprocessed_image.image_name))
    draw_box(bbl_image_object, ocr_data)
    # cv2.imshow('bbl_image_object', bbl_image_object)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    bbl_image = os.path.join(input_image.temp_path, "bbl_" + input_image.image_name)
    cv2.imwrite(bbl_image, bbl_image_object)
    return bbl_image

def continue_pipeline(images_path, temp_path, image_name):
    input_image = image_location(images_path, temp_path, image_name)
    with open(os.path.join(input_image.images_path, input_image.image_id + '.pkl'), 'rb') as pkl_input:
        ocr_data = pickle.load(pkl_input)
    complete_sentence = ''
    for bbox in ocr_data:
        complete_sentence = complete_sentence + bbox.bound_text + ' '
    print(complete_sentence)

    # Fix all spellings
    # for bbox in ocr_data:
    #     fix_spelling(bbox)

    replaced_image_object = cv2.imread(
        os.path.join(input_image.images_path, input_image.image_name))
    # Remove original text from image
    for bbox in ocr_data:
        remove_text(replaced_image_object, bbox)
    # Put font text back on image
    for bbox in ocr_data:
        if bbox.box_type == 'W':
            put_text(replaced_image_object, bbox)
    # cv2.imshow('replaced_image_object', replaced_image_object)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    replaced_image = os.path.join(input_image.temp_path, "replaced_" + input_image.image_name)
    cv2.imwrite(replaced_image, replaced_image_object)
    return replaced_image

if __name__ == '__main__':
    print("hello!")
