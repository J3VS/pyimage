from abc import ABC
from typing import Optional

from pyfunk.pyfunk import not_empty, count, concat, mapl
from pyimage.data import ParsedImage
from pyimage.search import ImageSearch, ImageFilter, as_integer, as_number


def find_value_to_right(parsed_image: ParsedImage, label: str):
    image_search = ImageSearch(parsed_image)
    group = image_search.find_phrase(label)

    if group and not_empty(group.text_objects):
        value_for_label = ImageFilter(parsed_image) \
            .y_center_within(group.get_top(), group.get_bottom()) \
            .to_right(group.get_right()) \
            .valuable() \
            .sort_right() \
            .take(1) \
            .collect_one()

        if value_for_label:
            try:
                return as_integer(value_for_label.text)
            except ValueError:
                return None
    return None


def find_number_above(parsed_image: ParsedImage, label: str):
    image_search = ImageSearch(parsed_image)
    group = image_search.find_phrase(label)

    if group and not_empty(group.text_objects):
        value_for_label = ImageFilter(parsed_image)\
            .above(group.get_top())\
            .sort_up()\
            .take(1)\
            .x_center_within(group.get_left(), group.get_right())\
            .collect_one()

        if value_for_label:
            try:
                return as_integer(value_for_label.text)
            except ValueError:
                return None
    return None


def get_number_row(parsed_image: ParsedImage, size: int, zero_substitutes: Optional[list[str]] = None):
    image_search = ImageSearch(parsed_image)
    text_objects = image_search.find_numbers(zero_substitutes=zero_substitutes)

    if not_empty(text_objects):
        for text_object in text_objects:
            neighboring_numbers = ImageFilter(parsed_image)\
                .y_center_within(text_object.get_top(), text_object.get_bottom()) \
                .to_right(text_object.get_right()) \
                .sort_right() \
                .valuable() \
                .numbers(zero_substitutes=zero_substitutes) \
                .collect()

            if neighboring_numbers and count(neighboring_numbers) == size - 1:
                return mapl(lambda to: as_integer(to.text, zero_substitutes=zero_substitutes),
                            concat([text_object], neighboring_numbers))


class AbstractScreenShotSearch(ABC):
    def __init__(self, image_path, preprocesses=None):
        if preprocesses is None:
            preprocesses = [None]

        self.parsed_images = [ParsedImage(image_path, preprocess=preprocess) for preprocess in preprocesses]

    def find_value_to_right(self, label: str):
        for parsed_image in self.parsed_images:
            value = find_value_to_right(parsed_image, label)
            if value is not None:
                return value

    def find_number_above(self, label: str):
        for parsed_image in self.parsed_images:
            value = find_number_above(parsed_image, label)
            if value is not None:
                return value

    def get_number_row(self, size: int, zero_substitutes: Optional[list[str]] = None):
        for parsed_image in self.parsed_images:
            value = get_number_row(parsed_image, size, zero_substitutes=zero_substitutes)
            if value is not None:
                return value

    @staticmethod
    def suffix_to_multiplies(suffix):
        if suffix.lower().startswith("k"):
            return 1000
        elif suffix.lower().startswith("m"):
            return 1000000
        elif suffix.lower().startswith("b"):
            return 1000000000
        return 1

    def get_number_below_with_suffix(self, label: str):
        for parsed_image in self.parsed_images:
            image_search = ImageSearch(parsed_image)
            group = image_search.find_phrase(label)

            if group:
                value_for_label = ImageFilter(parsed_image)\
                    .valuable()\
                    .below(group.get_bottom())\
                    .x_center_within(group.get_left(), group.get_right())\
                    .sort_down()\
                    .take(1)\
                    .numbers()\
                    .collect_one()

                if value_for_label:
                    value = as_number(value_for_label.text)

                    suffix_for_value = ImageFilter(parsed_image) \
                        .valuable() \
                        .y_center_within(value_for_label.get_top(), value_for_label.get_bottom())\
                        .to_right(value_for_label.get_right())\
                        .sort_right()\
                        .take(1)\
                        .collect_one()

                    if suffix_for_value and suffix_for_value.text:
                        value *= self.suffix_to_multiplies(suffix_for_value.text)

                    return int(value)
