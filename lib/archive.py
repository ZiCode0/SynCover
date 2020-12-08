import os
import zipfile

import lib.config as conf


def unzip(file_path):
    """
    Unzip selected folder
    :type file_path: input path to target file with extension
    """
    target_unpack_folder = os.path.splitext(file_path)[0]  # get
    repeat_count = 0
    zip_ref = None
    while not zip_ref:
        try:
            zip_ref = zipfile.ZipFile(file_path, 'r')
        except zipfile.BadZipFile:
            if repeat_count == conf.repeat_reading_zip_file_in_seconds - 1:
                Exception(zipfile.BadZipFile)
            repeat_count += 1

    zip_ref.extractall(target_unpack_folder)
    zip_ref.close()
    return target_unpack_folder
