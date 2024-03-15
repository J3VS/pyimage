import cv2
import pytesseract
import os
from PIL import Image
from pyimage.utils import uuid

MIN_WIDTH = 600


class PreProcess:
    GRAY = "gray"
    ADAPTIVE_THRESH = 'adaptive_thresh'
    THRESH = "thresh"
    BLUR = "blur"


def resize(img):
    width, height = img.shape[1], img.shape[0]
    new_width = max([width, MIN_WIDTH])
    factor = new_width/width
    new_height = int(height * factor)
    dim = (new_width, new_height)
    return cv2.resize(img, dim)


def get_grayscale(image, preprocess=None):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    resized = resize(gray)
    if preprocess is None or preprocess == PreProcess.GRAY:
        return resized
    elif preprocess == PreProcess.ADAPTIVE_THRESH:
        return cv2.adaptiveThreshold(resized, 250, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 11)
    elif preprocess == PreProcess.THRESH:
        return cv2.threshold(resized, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    elif preprocess == PreProcess.BLUR:
        return cv2.medianBlur(resized, 3)


def as_temp_with_grayscale(preprocess=None):
    def wrapper(f):
        def wrapped(image_path):
            filename = None
            try:
                image = cv2.imread(image_path)
                gray = get_grayscale(image, preprocess=preprocess)
                filename = "{}.png".format(uuid())
                cv2.imwrite(filename, gray)
                return f(filename)
            finally:
                if filename:
                    os.remove(filename)
        return wrapped
    return wrapper


@as_temp_with_grayscale()
def read_image_string(image_path):
    return pytesseract.image_to_string(Image.open(image_path))


@as_temp_with_grayscale()
def read_image_data(image_path):
    return pytesseract.image_to_data(Image.open(image_path))


@as_temp_with_grayscale(preprocess=PreProcess.ADAPTIVE_THRESH)
def read_image_data_adaptive_thresh(image_path):
    return pytesseract.image_to_data(Image.open(image_path))
