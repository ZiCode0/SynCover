import os
import shutil

from lib import config


def list_data_folder_files(target_ext='.zip'):
    """
    List all files with source extension from data folder
    :type target_ext: extension of target files
    :return: list of files in target data folder
    """
    res = []
    for file in os.listdir(config.data_folder):
        if file.endswith(target_ext):
            res.append(file)
    return res


def return_sub_dir_path(target_folder):
    """
    Return path to last folder with target files
    :param target_folder: target folder
    :return: path to folder with target files
    """
    sub_dir = [x[0] for x in os.walk(target_folder)][-1]
    return sub_dir


def rm_last_sub_folder(target_folder, repeat=4):
    for i in range(repeat):
        shutil.rmtree(return_sub_dir_path(target_folder))


def move_from_sub_folder(target_folder):
    """
    Move files to directory above.
    :type target_folder: target folder to move files in it
    """
    sub_dir = return_sub_dir_path(target_folder)
    files = os.listdir(sub_dir)

    for file in files:
        try:
            shutil.move(os.path.join(sub_dir, file), target_folder)
        except shutil.Error:
            pass

    rm_last_sub_folder(target_folder)


def used_files_cleaner(target_folder):
    """
    Clean used files such as target zip and temp folder.
    """
    target_folder_dest, target_path_name = os.path.split(target_folder)
    dir_list = os.listdir(target_folder_dest)
    for file in dir_list:
        if target_path_name in file:
            if not file.endswith(config.result_ext):
                try:
                    # remove temp dir
                    shutil.rmtree(os.path.join(target_folder_dest, file))
                except NotADirectoryError:
                    # remove source file
                    os.remove(os.path.join(target_folder_dest, file))
                except Exception as ex:
                    # catch unknown error
                    print(ex)
