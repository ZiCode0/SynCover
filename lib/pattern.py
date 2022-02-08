import re

filename_format_example = 'KLY_2000-12-30.zip'


def check_filename_format(name: str):
    """
    Check standard filename format
    :param name: target string
    :return:
    """
    # like: KLY_2020-12-12.zip
    pattern_filename_format = '[a-zA-Z]+_[0-9]{4}-[0-9]{2}-[0-9]{2}.[a-zA-Z]+'
    return bool(re.match(pattern_filename_format, name))
