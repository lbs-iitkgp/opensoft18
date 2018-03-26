#!/usr/bin/env python3

import time
import json
import operator
import os
import numpy as np
import img2pdf
import cv2
import pickle

import utilities.pre_process as pp

from spellcheck import parse_name as pn
from utilities.digicon_classes import coordinate, boundingBox, image_location
from vision_api import google_vision, azure_vision
from spellcheck import lexigram, spellcheck_azure, spellcheck_custom

def preprocess(input_image):
    """
    pre-processes the image and converts to gray-scale
    :param input_image: path to the image to be processed
    """
    pp.whiteboard(input_image)
    # pp.notescan_main(input_image)

def get_names(in_str):
    """
    calls extract from parse_name module
    :param in_str: input string
    :return: list containing names present in the input string
    """
    return pn.extract(in_str)

def img_to_pdf(input_image):  # name of the image as input
    replaced_image = os.path.join(input_image.temp_path, "replaced_" + input_image.image_name)
    pdf_bytes = img2pdf.convert([replaced_image])
    pdf_image = os.path.join(input_image.temp_path, "pdf_" + input_image.image_id + ".pdf")
    file = open(pdf_image, "wb")
    file.write(pdf_bytes)
    file.close()
    return pdf_image

def get_lexigram(bounding_box):
    """
    Extracts all possible metadata from all the bounding boxes
    :param bounding_box: a bounding box with bound_text
    :return: bounding_box: a bounding box with spell-fixed bound_text
    """
    # The possible types detected by lexigraph are:
    # findings, problems, drugs, devices, anatomy
    lexigram_json = {}
    print(bounding_box.bound_text)
    individual_json = lexigram.extract_metadata_json(bounding_box.bound_text)
    # for key in individual_json:
    #     if key not in lexigram_json:
    #         lexigram_json[key] = set()
    #     lexigram_json[key] = lexigram_json[key].union(individual_json[key])
    print(individual_json)
    for w_box in bounding_box.bb_children:
        for finding_type in individual_json:
            for finding in individual_json[finding_type]:
                if finding['token'] == w_box.bound_text:
                    w_box.lexi_type = finding_type
                    w_box.lexi_label = finding['label']
    # for w_box in bounding_box.bb_children:
    #     print(w_box.bound_text)
    return individual_json

def fix_bound_text(bounding_box_list):
    """
    Fixes the `bound_text` attribute for sentence level boundingBox objects
    using the bb_children attribute.
    :param bounding_box_list: a list of bounding boxes with bound_text
    :return: bounding_box_list: a list of bounding boxes with spell-fixed bound_text
    """
    for bbox in bounding_box_list:
        if bbox.box_type == 'L' or bbox.box_type == 'A':
            bound_text = ''
            for child_box in bbox.bb_children:
                bound_text = bound_text + child_box.bound_text + ' '
            bbox.bound_text = bound_text
    return bounding_box_list

def fix_spelling(bounding_box_list):
    """
    Fixes spelling based on Azure spellchecker and custom spellchecker
    :param bounding_box_list: a list of bounding boxes with bound_text
    :return: bounding_box_list: a list of bounding boxes with spell-fixed bound_text
    """
    # text = spellcheck_azure.make_correction(text)

    for bbox in bounding_box_list:
        if bbox.box_type == 'W':
            text = spellcheck_custom.spellcor(bbox.bound_text)
            bbox.bound_text = text

    bounding_box_list = fix_bound_text(bounding_box_list)
    return bounding_box_list

def crop_image(input_image, x1, x2, y1, y2):
    crop_out = input_image[y1:y2, x1:x2]
    return crop_out

def remove_text(input_image, bb_object):
    if bb_object.box_type == 'W':
        img = input_image
        x1 = min(bb_object.tl.x, bb_object.tr.x, bb_object.bl.x, bb_object.br.x)
        x2 = max(bb_object.tl.x, bb_object.tr.x, bb_object.bl.x, bb_object.br.x)
        y1 = min(bb_object.tl.y, bb_object.tr.y, bb_object.bl.y, bb_object.br.y)
        y2 = max(bb_object.tl.y, bb_object.tr.y, bb_object.bl.y, bb_object.br.y)
        # print(x1,x2,y1,y2)
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

def get_lexi_color(lexi_type):
    # The possible types detected by lexigraph are:
    # findings, problems, drugs, devices, anatomy
    font_color = (0, 0, 0)
    if lexi_type == 'FINDINGS':
        font_color = (0, 153, 0)
    elif lexi_type == 'PROBLEMS':
        font_color = (102, 0, 51)
    elif lexi_type == 'DRUGS':
        font_color = (204, 102, 0)
    elif lexi_type == 'DEVICES':
        font_color = (255, 204, 0)
    elif lexi_type == 'ANATOMY':
        font_color = (102, 0, 0)
    return font_color

def put_text(in_img, bbox):
    """
    put extracted text (in black) over the place of original text
    :param in_img: cleaned image in opencv format
    :param bbox: bounding box
    :return: out_img: a separate image with text placed at right places
    """
    out_img = in_img
    font = cv2.FONT_HERSHEY_DUPLEX
    font_color = get_lexi_color(bbox.lexi_type)
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


def call_CoreNLP(in_img,bounding_boxes) :
    # This calls core function to get name of hospital, address, doctors name ,specialisation
    height, width, _ = in_img.shape
    return cnlp.core(height,width,bounding_boxes) #Output as a list - refer Readme_nlp

def add_to_pipeline(images_path, temp_path, image_name):
    print(image_name)
    input_image = image_location(images_path, temp_path, image_name)
    # Pre-processing
    # preprocess(input_image)
    preprocessed_image = input_image
    
    # Get OCR data
    ocr_data = google_vision.get_google_ocr(input_image)
    # ocr_data = azure_vision.get_azure_ocr(input_image)
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

    # Fix all spellings
    fix_spelling(ocr_data)
    ocr_data = fix_bound_text(ocr_data)

    # Get lexigram data
    get_lexigram(ocr_data[0])

    # Create image object to return
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

    with open(os.path.join(input_image.images_path, input_image.image_id + '.pkl'), 'wb') as pkl_output:
        pickle.dump(ocr_data, pkl_output, pickle.HIGHEST_PROTOCOL)

    replaced_image = os.path.join(input_image.temp_path, "replaced_" + input_image.image_name)
    cv2.imwrite(replaced_image, replaced_image_object)
    return replaced_image

def finish_pipeline(images_path, temp_path, image_name):
    input_image = image_location(images_path, temp_path, image_name)
    with open(os.path.join(input_image.images_path, input_image.image_id + '.pkl'), 'rb') as pkl_input:
        ocr_data = pickle.load(pkl_input)
    final_json = {}
    
    # Create PDF
    pdf_path = img_to_pdf(input_image)

    return final_json

def do_download(images_path, temp_path, image_name, download_type):
    input_image = image_location(images_path, temp_path, image_name)
    if download_type == 0:
        return os.path.join(input_image.temp_path, "replaced_" + input_image.image_name)
    elif download_type == 1:
        return os.path.join(input_image.temp_path, "pdf_" + input_image.image_id + ".pdf")

if __name__ == '__main__':
    print("hello!")
