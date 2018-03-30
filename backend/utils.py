#!/usr/bin/env python3

import time
import json
import operator
import os
import numpy as np
import img2pdf
import cv2
import pickle
import math
from PIL import ImageFont, ImageDraw, Image

import utilities.pre_process as pp

# from spellcheck import parse_name as pn
from utilities.ner import render_ner
from utilities.digicon_classes import coordinate, boundingBox, image_location
from vision_api import google_vision, azure_vision
from spellcheck import lexigram, spellcheck_azure, spellcheck_custom
import corenlp.CoreNLP2 as cnlp

def preprocess(input_image):
    """
    pre-processes the image and converts to gray-scale
    :param input_image: path to the image to be processed
    """
    # pp.whiteboard(input_image)
    pp.notescan_main(input_image)

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
    fresh_image = os.path.join(input_image.temp_path, "fresh_" + input_image.image_name)
    pdf_bytes = img2pdf.convert([fresh_image])
    fresh_pdf_image = os.path.join(input_image.temp_path, "freshpdf_" + input_image.image_id + ".pdf")
    file = open(fresh_pdf_image, "wb")
    file.write(pdf_bytes)
    file.close()
    return pdf_image, fresh_image

def drugdose_detect(bb_object, finding, all_boxes):
    for bbox in all_boxes:
        if bbox.box_type == 'L':
            for bb_child in bbox.bb_children:
                if bb_object == bb_child:
                    full_text = bbox.bound_text
                    drug, dosage = full_text.split(finding['token'], 1)
                    bb_object.dosage = {
                        'drug': ''.join(e for e in finding['label'] if (e.isalnum() or e == ' ')),
                        'dosage': ''.join(e for e in dosage if (e.isalnum() or e == ' '))
                    }

def get_dosage(all_boxes):
    dosage_json = {}
    for bbox in all_boxes:
        if bbox.box_type == 'W' and bbox.lexi_type == 'DRUGS':
            try:
                dosage_json[bbox.dosage['drug']] = bbox.dosage['dosage']
            except KeyError:
                pass
    return dosage_json

def get_lexigram(all_boxes):
    """
    Extracts all possible metadata from all the bounding boxes
    :param bounding_box: a bounding box with bound_text
    :return: bounding_box: a bounding box with spell-fixed bound_text
    """
    # The possible types detected by lexigraph are:
    # findings, problems, drugs, devices, anatomy
    # lexigram_json = {}
    bounding_box = all_boxes[0]
    print(bounding_box.bound_text)
    individual_json = lexigram.extract_metadata_json(bounding_box.bound_text)
    # for key in individual_json:
    #     if key not in lexigram_json:
    #         lexigram_json[key] = set()
    #     lexigram_json[key] = lexigram_json[key].union(individual_json[key])
    for finding_type in individual_json:
        individual_json[finding_type] = [finding for finding in individual_json[finding_type] if len(finding['token']) >= 2]
    print(individual_json)
    for w_box in bounding_box.bb_children:
        for finding_type in individual_json:
            for finding in individual_json[finding_type]:
                if finding['token'] == w_box.bound_text:
                    w_box.lexi_type = finding_type
                    w_box.lexi_label = finding['label']
                    if (finding_type == 'DRUGS' and len(finding['token']) >= 3):
                        drugdose_detect(w_box, finding, all_boxes)
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
    # print(len(bounding_box_list))
    # for bbox in bounding_box_list:
    #     if bbox.box_type == 'W':
    #         print(bbox.bound_text)

    bounding_box_list = spellcheck_azure.merge_bounding_boxes(bounding_box_list)
    print(bounding_box_list[0].bound_text)
    # exit(0)

    # print(len(bounding_box_list))
    # for bbox in bounding_box_list:
    #     if bbox.box_type == 'W':
    #         print(bbox.bound_text)
    # exit(0)
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
        kernel = np.ones((8,8), np.uint8)
        # crop = cv2.erode(crop, kernel, iterations=5)
        crop = cv2.dilate(crop, kernel, iterations=2)
        # crop = cv2.inpaint(crop, crop, 3, cv2.INPAINT_TELEA)
        input_image[y1:y2, x1:x2] = crop


def rect_dim(point, img):
    """
    bounds the points to image size
    :param point: list containing x and y value for a single coordinate
    :param img: image on which the point is to be bound
    :return point: bounded point if it is out of image, otherwise original
    """
    y_max, x_max, channel_count = img.shape

    # checking x coordinate
    if point[0] < 1:
        point[0] = 1
    elif point[0] > x_max:
        point[0] = x_max - 1

    # checking y coordinate
    if point[1] < 1:
        point[1] = 1
    elif point[1] > y_max:
        point[1] = y_max - 1

    return point



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
            vertices = np.array([rect_dim([box.tl.x, box.tl.y], in_img), rect_dim([box.tr.x, box.tr.y], in_img),
                                 rect_dim([box.br.x, box.br.y], in_img), rect_dim([box.bl.x, box.bl.y], in_img)], np.int32)
            cv2.polylines(in_img, [vertices], True, red, thickness=1, lineType=cv2.LINE_AA)
    # uncomment below lines while debugging
    # cv2.imshow("debug", in_img)
    # cv2.waitKey(0)
    return in_img

def get_lexi_color(lexi_type):
    # The possible types detected by lexigraph are:
    # findings, problems, drugs, devices, anatomy
    font_color = (255, 0, 0)
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

def draw_rotated_text(image, fresh_image, angle, xy, text, fill, *args, **kwargs):
    """ Draw text at an angle into an image, takes the same arguments
        as Image.text() except for:

    :param image: Image to write text into
    :param angle: Angle to write text at
    """
    # get the size of our image
    width, height = image.size
    max_dim = max(width, height)

    # build a transparency mask large enough to hold the text
    mask_size = (max_dim * 2, max_dim * 2)
    mask = Image.new('L', mask_size, 0)

    # add text to mask
    draw = ImageDraw.Draw(mask)
    draw.text((max_dim, max_dim), text, 255, *args, **kwargs)

    if angle % 90 == 0:
        # rotate by multiple of 90 deg is easier
        rotated_mask = mask.rotate(angle)
    else:
        # rotate an an enlarged mask to minimize jaggies
        # bigger_mask = mask.resize((max_dim*8, max_dim*8),
        #                           resample=Image.BICUBIC)
        # rotated_mask = bigger_mask.rotate(angle).resize(
        #     mask_size, resample=Image.LANCZOS)
        bigger_mask = mask.resize((max_dim*8, max_dim*8))
        rotated_mask = bigger_mask.rotate(angle).resize(
            mask_size)

    # crop the mask to match image
    mask_xy = (max_dim - xy[0], max_dim - xy[1])
    b_box = mask_xy + (mask_xy[0] + width, mask_xy[1] + height)
    mask = rotated_mask.crop(b_box)

    # paste the appropriate color, with the text transparency mask
    color_image = Image.new('RGBA', image.size, fill)
    image.paste(color_image, mask)
    fresh_image.paste(color_image, mask)

def get_font(bbox, font_path):
    fontsize = 1
    bbox_fraction = 0.9
    bbox_width = math.hypot(bbox.tl.x - bbox.tr.x, bbox.tl.y - bbox.tr.y)
    bbox_height = math.hypot(bbox.tl.x - bbox.bl.x, bbox.tl.y - bbox.bl.y)

    font = ImageFont.truetype(font_path, fontsize)
    while (font.getsize(bbox.bound_text)[0] < bbox_fraction*bbox_width
        and font.getsize(bbox.bound_text)[1] < bbox_fraction*bbox_height):
        if fontsize == 50:
            break
        fontsize += 1
        font = ImageFont.truetype(font_path, fontsize)
    fontsize -= 1
    fontsize = max(fontsize, 15)
    font = ImageFont.truetype(font_path, fontsize)
    return font

def put_text_alt(cv_object, bbox_list):
    """
    put extracted text (in black) over the place of original text
    :param in_img: cleaned image path
    :param bbox: bounding box
    :param img_object: replaced image object
    """
    cv_object = cv2.cvtColor(cv_object, cv2.COLOR_BGR2RGB)
    image_object = Image.fromarray(cv_object)
    fresh_image_object = Image.new('RGB', image_object.size, color=(255, 255, 255))

    for bbox in bbox_list:
        if bbox.box_type == 'W':
            if bbox.language == 'bn':
                font = get_font(bbox, os.path.join(
                    os.path.dirname(os.path.realpath(__file__)), "fonts", "Hind_Siliguri", "HindSiliguri-Regular.ttf"))
            else:
                font = get_font(bbox, os.path.join(
                    os.path.dirname(os.path.realpath(__file__)), "fonts", "Noto_Sans", "NotoSans-Regular.ttf"))
            print("WRITING!!!!")
            start_time = time.time()
            draw_rotated_text(
                image_object,
                fresh_image_object,
                math.degrees(math.atan2(bbox.bl.y - bbox.br.y, bbox.br.x - bbox.bl.x)),
                # (bbox.tl.x + (bbox.tl.x - font_width)/2, bbox.tl.y + (bbox.tl.y - font_height)/2),
                (bbox.tl.x, bbox.tl.y),
                bbox.bound_text,
                get_lexi_color(bbox.lexi_type),
                font=font
            )
            taken_time = time.time() - start_time
            minutes, seconds = taken_time // 60, taken_time % 60
            print(minutes, seconds)
            print("DONE!!!!")
    image_object = image_object.convert('RGB')
    cv_object = np.array(image_object)
    cv_object = cv_object[:, :, ::-1].copy()
    fresh_image_object = fresh_image_object.convert('RGB')
    fresh_cv_object = np.array(fresh_image_object)
    fresh_cv_object = fresh_cv_object[:, :, ::-1].copy()
    return cv_object, fresh_cv_object

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

def fix_orientation(image_path, bounding_boxes):
    avg_angle = 0
    image_object = cv2.imread(image_path)
    for bbox in bounding_boxes[:5]:
        angle = math.degrees(math.atan2(bbox.br.y - bbox.bl.y, bbox.br.x - bbox.bl.x))
        avg_angle += angle
    avg_angle /= 5
    if avg_angle > -45 and avg_angle <= 45:
        rotated_object = image_object
        cv2.imwrite(image_path, rotated_object)
    elif avg_angle > 45 and avg_angle <= 135:
        rotated_object = cv2.rotate(image_object, cv2.ROTATE_90_COUNTERCLOCKWISE)
        cv2.imwrite(image_path, rotated_object)
    elif avg_angle > -135 and avg_angle < 135:
        rotated_object = cv2.rotate(image_object, cv2.ROTATE_90_CLOCKWISE)
        cv2.imwrite(image_path, rotated_object)
    else:
        rotated_object = cv2.rotate(image_object, cv2.ROTATE_180)
        cv2.imwrite(image_path, rotated_object)

def call_CoreNLP(in_img, bounding_boxes) :
    # This calls core function to get name of hospital, address, doctors name ,specialisation
    height, _, _ = in_img.shape
    return cnlp.core(height, bounding_boxes) #Output as a list - refer Readme_nlp

def get_all_text(bounding_boxes):
    return bounding_boxes[0].bound_text

def add_to_pipeline(images_path, temp_path, image_name, sockethandler):
    print(image_name)
    input_image = image_location(images_path, temp_path, image_name)
    input_path = os.path.join(input_image.images_path, input_image.image_name)
    image_object = cv2.imread(input_path)
    # Pre-processing
    sockethandler.emit('statusChange','Applying Pre-Processing')
    try:
        preprocess(input_image)
    except:
        cv2.imwrite(input_path, image_object)
    preprocessed_image = input_image

    # Get OCR data
    sockethandler.emit('statusChange','Running OCR')
    ocr_data = google_vision.get_google_ocr(input_image)
    # ocr_data = azure_vision.get_azure_ocr(input_image)

    ocr_data = fix_spelling(ocr_data)

    with open(os.path.join(input_image.images_path, input_image.image_id + '.pkl'), 'wb') as pkl_output:
        pickle.dump(ocr_data, pkl_output, pickle.HIGHEST_PROTOCOL)

    # Draw bounding boxes around words
    sockethandler.emit('statusChange','Drawing bounding boxes')
    bbl_image_object = cv2.imread(
        os.path.join(preprocessed_image.images_path, preprocessed_image.image_name))
    draw_box(bbl_image_object, ocr_data)
    # cv2.imshow('bbl_image_object', bbl_image_object)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    bbl_image = os.path.join(input_image.temp_path, "bbl_" + input_image.image_name)
    cv2.imwrite(bbl_image, bbl_image_object)
    sockethandler.emit('statusChange','Fixing orientation')
    fix_orientation(bbl_image, ocr_data)
    return bbl_image, render_ner(get_all_text(ocr_data))

def continue_pipeline(images_path, temp_path, image_name, sockethandler):
    input_image = image_location(images_path, temp_path, image_name)
    with open(os.path.join(input_image.images_path, input_image.image_id + '.pkl'), 'rb') as pkl_input:
        ocr_data = pickle.load(pkl_input)

    # Fix all spellings
    # ocr_data = fix_spelling(ocr_data)
    # ocr_data = fix_bound_text(ocr_data)

    # Get lexigram data
    sockethandler.emit('statusChange','Extracting medical metadata')
    lexigram_json = get_lexigram(ocr_data)

    # Get dosages
    sockethandler.emit('statusChange','Getting dosage data')
    dosage_json = get_dosage(ocr_data)

    # Create image object to return
    replaced_image_object = cv2.imread(
        os.path.join(input_image.images_path, input_image.image_name))

    # Remove original text from image
    sockethandler.emit('statusChange','Replacing detected text')
    for bbox in ocr_data:
        try:
            remove_text(replaced_image_object, bbox)
        except:
            pass
    ### Put font text back on image (using OpenCV)
    # for bbox in ocr_data:
    #     if bbox.box_type == 'W':
    #         put_text(replaced_image_object, bbox)
    ### Put font text back on image (using PIL)
    print("WRITING!!!!")
    # start_time = time.time()
    replaced_image_object, fresh_image_object = put_text_alt(replaced_image_object, ocr_data)
    # taken_time = time.time() - start_time
    # minutes, seconds = taken_time // 60, taken_time % 60
    # print(minutes, seconds)
    print("OKKKK")

    # cv2.imshow('replaced_image_object', replaced_image_object)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    with open(os.path.join(input_image.images_path, input_image.image_id + '.pkl'), 'wb') as pkl_output:
        pickle.dump(ocr_data, pkl_output, pickle.HIGHEST_PROTOCOL)

    # print("STARTING ================")
    # start_time = time.time()
    replaced_image = os.path.join(input_image.temp_path, "replaced_" + input_image.image_name)
    cv2.imwrite(replaced_image, replaced_image_object)
    fresh_image = os.path.join(input_image.temp_path, "fresh_" + input_image.image_name)
    cv2.imwrite(fresh_image, fresh_image_object)
    fix_orientation(replaced_image, ocr_data)
    fix_orientation(fresh_image, ocr_data)
    # print(time.time() - start_time)
    return replaced_image, fresh_image, lexigram_json, dosage_json

def finish_pipeline(images_path, temp_path, image_name, sockethandler):
    input_image = image_location(images_path, temp_path, image_name)
    final_json = {}

    # # Call CoreNLP
    # image_path = os.path.join(input_image.images_path, input_image.image_name)
    # image_object = cv2.imread(image_path)
    # corenlp_result = call_CoreNLP(image_object, ocr_data)
    # print(corenlp_result)

    # Create PDF
    sockethandler.emit('statusChange','Creating pdfs')
    pdf_path, fresh_pdf_path = img_to_pdf(input_image)

    return final_json

def do_nlp(images_path, temp_path, image_name, sockethandler):
    input_image = image_location(images_path, temp_path, image_name)
    with open(os.path.join(input_image.images_path, input_image.image_id + '.pkl'), 'rb') as pkl_input:
        ocr_data = pickle.load(pkl_input)

    corenlp_result = []

    # Call CoreNLP
    sockethandler.emit('statusChange','Running CoreNLP models')
    image_path = os.path.join(input_image.images_path, input_image.image_name)
    image_object = cv2.imread(image_path)
    corenlp_result = call_CoreNLP(image_object, ocr_data)
    sockethandler.emit('statusChange','Complete')

    return corenlp_result

def do_download(images_path, temp_path, image_name, download_type):
    input_image = image_location(images_path, temp_path, image_name)
    if download_type == 0:
        return os.path.join(input_image.temp_path, "replaced_" + input_image.image_name)
    elif download_type == 1:
        return os.path.join(input_image.temp_path, "pdf_" + input_image.image_id + ".pdf")
    elif download_type == 2:
        return os.path.join(input_image.temp_path, "fresh_" + input_image.image_name)
    elif download_type == 3:
        return os.path.join(input_image.temp_path, "freshpdf_" + input_image.image_id + ".pdf")

if __name__ == '__main__':
    print("hello!")
