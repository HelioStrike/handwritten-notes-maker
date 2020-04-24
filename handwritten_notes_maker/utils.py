from PIL import Image, ImageFont, ImageDraw
import numpy as np
import cv2

def imageFromText(text, font, horizontal_padding=0, vertical_padding=0):
    im = Image.new("RGB", (800, 600))
    draw = ImageDraw.Draw(im)
    draw.text((0, 0), text, font=font)
    bbox = im.getbbox()
    bbox = (max(0, bbox[0]-horizontal_padding), max(0, bbox[1]-vertical_padding), bbox[2]+2*horizontal_padding, bbox[3]+2*vertical_padding)
    im = im.crop(bbox)
    return im, bbox

def rotate_image(image, angle):
    image_center = tuple(np.array(image.shape[1::-1]) / 2)
    rot_mat = cv2.getRotationMatrix2D(image_center, angle, 1.0)
    result = cv2.warpAffine(image, rot_mat, image.shape[1::-1], flags=cv2.INTER_LINEAR)
    return result

def scale_image(image, scale_x, scale_y):
    resized = cv2.resize(image, (int(image.shape[1]*scale_y), int(image.shape[0]*scale_x)))
    result = np.zeros(image.shape)
    result[int(image.shape[0]*(1-scale_x)/2):int(image.shape[0]*(1-scale_x)/2)+resized.shape[0], \
        int(image.shape[1]*(1-scale_y)/2):int(image.shape[1]*(1-scale_y)/2)+resized.shape[1]] = resized
    return result