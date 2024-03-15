from dataclasses import dataclass


from pyfunk.pyfunk import split
from pyimage.read import read_image_data, PreProcess, read_image_data_adaptive_thresh


@dataclass
class ImageTextObject:
    id: str
    level: int
    page_num: int
    block_num: int
    par_num: int
    line_num: int
    word_num: int
    left: int
    top: int
    width: int
    height: int
    conf: float
    text: str

    def get_top(self):
        return self.top

    def get_bottom(self):
        return self.top + self.height

    def get_left(self):
        return self.left

    def get_right(self):
        return self.left + self.width

    def get_x_center(self):
        return self.left + (self.width / 2)

    def get_y_center(self):
        return self.top + (self.height / 2)


def read_text_objects(image_path, preprocess=None):
    if preprocess == PreProcess.ADAPTIVE_THRESH:
        data = read_image_data_adaptive_thresh(image_path)
    else:
        data = read_image_data(image_path)
    lines = split(data, "\n")
    text_objects = []
    for line in lines[1:]:
        if line:
            words = split(line, "\t")
            text_objects.append(ImageTextObject(
                str(uuid()),
                int(words[0]),
                int(words[1]),
                int(words[2]),
                int(words[3]),
                int(words[4]),
                int(words[5]),
                int(words[6]),
                int(words[7]),
                int(words[8]),
                int(words[9]),
                float(words[10]),
                words[11]
            ))
    return sorted(text_objects, key=lambda text_object: (text_object.top, text_object.left))


class ParsedImage:
    def __init__(self, image_path, preprocess=None):
        self.text_objects = read_text_objects(image_path, preprocess=preprocess)


def get_text(text_object: ImageTextObject):
    return text_object.text


def get_top(text_object: ImageTextObject):
    return text_object.get_top()


def get_bottom(text_object: ImageTextObject):
    return text_object.get_bottom()


def get_left(text_object: ImageTextObject):
    return text_object.get_left()


def get_right(text_object: ImageTextObject):
    return text_object.get_right()
