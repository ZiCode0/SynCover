import os
import shutil

from pathlib import Path

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


def create_channel_folder(channel_name):
    """
    Create channel folder in data source if not exist
    :param channel_name: target channel folder name
    :return:
    """
    target_path = os.path.join(config.data_folder, channel_name)
    # check channel folder name in data folder
    if not os.path.exists(target_path):
        os.makedirs(target_path)


def move_channel_files(target_folder):
    """
    Move files to channel folders. Detect target channel folder with file ending
    :return:
    """
    # target_folder_dest, target_path_name = os.path.split(target_folder)
    dir_list = os.listdir(target_folder)
    for path in dir_list:
        # check if target is file
        if os.path.isfile(os.path.join(target_folder, path)):
            # parse channel list
            for channel_codename in config.channels_list:
                # check ending
                if path.endswith(channel_codename + config.result_ext):
                    # create channel folder
                    create_channel_folder(channel_codename)
                    # move to channel folder
                    shutil.move(os.path.join(target_folder, path),
                                os.path.join(target_folder, channel_codename, path))


def get_last_log_files(log_count=1, select_zips=True):
    """Returns last log file in zip
    :param select_zips: switch flag
    :type log_count: amount of log files to grab
    """
    root_path = Path('.')
    result_logs = []
    if select_zips:
        # dir_list = [i for i in [*os.listdir(root_path)]]
        dir_list = list(reversed(
            sorted(filter(os.path.isfile,
                          os.listdir(root_path)
                          ),
                   key=os.path.getmtime)))
        i = 0
        for path_index in range(len(dir_list)):
            if i == log_count:
                return result_logs
            if dir_list[path_index].endswith('log.zip'):
                result_logs.append(dir_list[path_index])
                i += 1
    else:
        result_logs = open(root_path / 'SynCover.log')
        return result_logs
