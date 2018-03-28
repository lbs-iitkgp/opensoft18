import argparse
import numpy as np
import cv2


#run this file as: python3 rotate.py --image /image_directory/image_name

def rotate_a_rightup_image(image):
    # construct the argument parse and parse the arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--image", required=True, help="path to input image file")
    args = vars(ap.parse_args())

    # load the image from disk and convert the image to grayscale
    image = cv2.imread(args["image"],0)
    
    # flip the foreground and background to ensure foreground is now "white" and
    # the background is "black"
    gray = cv2.bitwise_not(image)
    # threshold the image, setting all foreground pixels to
    # 255 and all background pixels to 0
    thresh = cv2.threshold(gray, 0, 255,cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    coords = np.column_stack(np.where(thresh > 0))

    # find (x, y) coordinates of all pixel values that
    # are greater than zero, then use these coordinates to
    # compute a rotated bounding box that contains all
    # coordinates
    angle = cv2.minAreaRect(coords)[-1]
    print(angle)

    if angle == 0.0:
        cv2.imshow("Input", image)
        cv2.waitKey(0)
    else :
        angle = -(90 + angle) 
        #rotate the image to deskew it
        (h,w) = image.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)   
        print("[INFO] angle: {:.3f}".format(angle))
        cv2.imshow("Input", image)
        cv2.imshow("Rotated", rotated)
        cv2.waitKey(0)

def rotate_a_leftup_image(image):
    # construct the argument parse and parse the arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--image", required=True, help="path to input image file")
    args = vars(ap.parse_args())

    # load the image from disk and convert the image to grayscale
    image = cv2.imread(args["image"],0)
    
    # flip the foreground and background to ensure foreground is now "white" and
    # the background is "black"
    gray = cv2.bitwise_not(image)
    # threshold the image, setting all foreground pixels to
    # 255 and all background pixels to 0
    thresh = cv2.threshold(gray, 0, 255,cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    coords = np.column_stack(np.where(thresh > 0))

    # find (x, y) coordinates of all pixel values that
    # are greater than zero, then use these coordinates to
    # compute a rotated bounding box that contains all
    # coordinates
    angle = cv2.minAreaRect(coords)[-1]
    print(angle)

    if angle == 0.0:
        cv2.imshow("Input", image)
        cv2.waitKey(0)
    else :
        angle = -angle 
        #rotate the image to deskew it
        (h,w) = image.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)   
        print("[INFO] angle: {:.3f}".format(angle))
        cv2.imshow("Input", image)
        cv2.imshow("Rotated", rotated)
        cv2.waitKey(0)
