from typing import Sequence

import numpy

from pyfunk.pyfunk import find, replace, count, mapl, split, first, take, join, concat, not_empty
from pyimage.data import ParsedImage, ImageTextObject, get_top, get_bottom, get_left, get_right


def is_valuable(text_object: ImageTextObject):
    return text_object.text and text_object.text != '' and text_object.text != ' '


def to_float(number, multiplier):
    return float(numpy.float128(number) * multiplier)


def as_number(s: str, zero_substitutes: Sequence[str] = None):
    if zero_substitutes and s in zero_substitutes:
        return 0
    if "," in s:
        return to_float(replace(s, ",", ""), 1)
    if s.endswith('K'):
        return to_float(replace(s, 'K', ''), 1000)
    if s.endswith('M'):
        return to_float(replace(s, 'M', ''), 1000000)
    if s.endswith('B'):
        return to_float(replace(s, 'B', ''), 1000000000)
    return float(s)


def as_integer(s: str, zero_substitutes: Sequence[str] = None):
    return int(as_number(s, zero_substitutes=zero_substitutes))


def is_number(s: str, zero_substitutes: Sequence[str] = None):
    try:
        as_number(s, zero_substitutes=zero_substitutes)
        return True
    except ValueError:
        return False


def is_integer(s: str, zero_substitutes: Sequence[str] = None):
    try:
        is_integer(s, zero_substitutes=zero_substitutes)
        return True
    except ValueError:
        return False


class FilteredObjects:
    def __init__(self, text_objects: list[ImageTextObject]):
        self.text_objects = text_objects

    def __iter__(self):
        return self.text_objects

    def sort(self, key_fn):
        self.text_objects = sorted(self.text_objects, key=key_fn)

    def reverse(self):
        self.text_objects.reverse()

    def filter(self, fn):
        self.text_objects = find(fn, self.text_objects)

    def take(self, n):
        self.text_objects = take(n, self.text_objects)


def get_text(text_object: ImageTextObject):
    return text_object.text


class ImageSearch:
    def __init__(self, parsed_image: ParsedImage):
        self.parsed_image = parsed_image

    def find(self, fn):
        return find(lambda to: fn(to.text), self.parsed_image.text_objects)

    def find_numbers(self, zero_substitutes=None):
        return self.find(lambda text: is_number(text, zero_substitutes=zero_substitutes))

    def find_phrase(self, phrase):
        split_text = split(phrase, " ")
        initial = split_text[0]
        rest = join(split_text[1:])
        rest_count = count(split_text[1:])

        for text_object in self.parsed_image.text_objects:
            if text_object.text == initial:
                if rest_count == 0:
                    return TextObjectGroup([text_object])

                following_objects = ImageFilter(self.parsed_image)\
                    .y_center_within(text_object.get_top(), text_object.get_bottom())\
                    .to_right(text_object.get_right())\
                    .valuable()\
                    .sort_right()\
                    .take(rest_count)\
                    .collect()

                following_text = join(mapl(get_text, following_objects))

                if following_text == rest:
                    return TextObjectGroup(concat([text_object], following_objects))


class TextObjectGroup:
    def __init__(self, text_objects: list[ImageTextObject]):
        self.text_objects = text_objects

    def get_top(self):
        if not_empty(self.text_objects):
            return min(mapl(get_top, self.text_objects))

    def get_bottom(self):
        if not_empty(self.text_objects):
            return max(mapl(get_bottom, self.text_objects))

    def get_left(self):
        if not_empty(self.text_objects):
            return min(mapl(get_left, self.text_objects))

    def get_right(self):
        if not_empty(self.text_objects):
            return max(mapl(get_right, self.text_objects))


class ImageFilter:
    def __init__(self, parsed_image):
        self.parsed_image = parsed_image
        self.filtered = FilteredObjects(self.parsed_image.text_objects)

    def valuable(self):
        self.filtered.filter(lambda text_object: text_object.text != '' and text_object.text != ' ')
        return self

    def sort_right(self):
        self.filtered.sort(get_left)
        return self

    def sort_left(self):
        self.filtered.sort(get_right)
        self.filtered.reverse()
        return self

    def sort_up(self):
        self.filtered.sort(get_bottom)
        self.filtered.reverse()
        return self

    def sort_down(self):
        self.filtered.sort(get_top)
        return self

    def above(self, y):
        self.filtered.filter(lambda text_object: get_bottom(text_object) <= y)
        return self

    def below(self, y):
        self.filtered.filter(lambda text_object: get_top(text_object) >= y)
        return self

    def to_right(self, x):
        self.filtered.filter(lambda text_object: get_left(text_object) >= x)
        return self

    def to_left(self, x):
        self.filtered.filter(lambda text_object: get_right(text_object) <= x)
        return self

    def y_center_within(self, y1, y2):
        self.filtered.filter(lambda text_object: y1 <= text_object.get_y_center() <= y2)
        return self

    def x_center_within(self, x1, x2):
        self.filtered.filter(lambda text_object: x1 <= text_object.get_x_center() <= x2)
        return self

    def numbers(self, zero_substitutes=None):
        self.filtered.filter(lambda text_object: is_number(text_object.text, zero_substitutes=zero_substitutes))
        return self

    def integers(self, zero_substitutes=None):
        self.filtered.filter(lambda text_object: is_integer(text_object.text, zero_substitutes=zero_substitutes))
        return self

    def take(self, n):
        self.filtered.take(n)
        return self

    def collect(self):
        return self.filtered.text_objects

    def collect_one(self):
        return first(self.filtered.text_objects)
