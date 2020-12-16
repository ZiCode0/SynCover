import argparse
import os
import re
from datetime import datetime as dt
from lib import config


def sorted_list(path, folder):
    result = os.listdir(os.path.join(path, folder))
    result.sort()
    return result


def get_list_of_files_in_folder(path):
    list_of_folders = os.listdir(path)
    list_of_folders.sort()

    res_list = []
    for path_index in range(len(list_of_folders)):
        tmp = list_of_folders[path_index]
        if os.path.isdir(os.path.join(path, tmp)):
            res_list.append(list_of_folders[path_index])
    list_of_folders = res_list
    del res_list

    result = {a: sorted_list(path, a) for a in list_of_folders}
    return result


def head_maker(date, time):
    date = re.sub(r'^.*?_', '_', date)[1:]
    head_date = date + ' ' + time
    head_date = dt.strptime(head_date, '%Y-%m-%d %H:%M:%S.%f')
    head = '{:%Y%m%d%H%M%S0000}'.format(head_date, )
    # print(head)
    return head


def file_constructor(path, key, head, station, channel, head_key, collector):
    file_wr = open(os.path.join(path, key + '_{channel}.asc'.format(channel=channel)), 'a')
    file_wr.write('\n{head} {station} {head_key} {size}\n'.format(head=head,
                                                                  station=station,
                                                                  channel=channel,
                                                                  head_key=head_key,
                                                                  size=len(collector)))
    file_wr.writelines(collector)
    file_wr.close()


def station_skr(item, path):
    for key, values in iter(item.items()):

        head_time = str(open(os.path.join(path, key, values[0]), 'r').readline()).split(' ')
        head = head_maker(key, head_time[0])

        channels = {'SKRI D0 20': [],
                    'SKRG_EF4_2 D0 20': [],
                    'SKRG_EF0001_2 D0 20': [],
                    'SKRP D0 100': []}

        for val in values:
            with open(os.path.join(path, key, val), 'r') as file:
                data_from_file = file.readlines()

                for line in data_from_file:
                    line = line.split(' ')
                    if line[1] == '1':
                        channels['SKRI D0 20'].append(
                            config.get_station_line(line=line, station='skr', channel='SKRI')
                        )
                    elif line[1] == '2':
                        channels['SKRG_EF4_2 D0 20'].append(
                            config.get_station_line(line=line, station='skr', channel='SKRG_EF4_2')
                        )
                    elif line[1] == '3':
                        channels['SKRG_EF0001_2 D0 20'].append(
                            config.get_station_line(line=line, station='skr', channel='SKRG_EF0001_2')
                        )

                    else:
                        # inf['SKRI D0 20'].append(str(float(line[1].strip())) + '\n')
                        channels['SKRP D0 100'].append(
                            config.get_station_line(line=line, station='skr', channel='SKRP'))

                del data_from_file

        for head_key, s_values in iter(channels.items()):
            channel = list(head_key.split(' '))[0]
            file_constructor(path=path, key=key, head=head, station='SKRG', channel=channel, head_key=head_key,
                             collector=s_values)

        del channels


def station_kly(item, path):
    for key, values in iter(item.items()):

        head_time = str(open(os.path.join(path, key, values[0]), 'r').readline()).split(' ')
        head = head_maker(key, head_time[0])

        channels = {'KLY_EF4-3 D0 20': []}

        for val in values:
            with open(os.path.join(path, key, val), 'r') as file:
                data_from_file = file.readlines()

                for line in data_from_file:
                    line.split(' ')
                    channels['KLY_EF4-3 D0 20'].append(
                        config.get_station_line(line=line, station='kly', channel='KLY_EF4-3'))

                del data_from_file

        for head_key, s_values in iter(channels.items()):
            channel = list(head_key.split(' '))[0]
            file_constructor(path=path, key=key, head=head, station='KLYG', channel=channel, head_key=head_key,
                             collector=s_values)

        del channels


def station_kbg(item, path):
    for key, values in iter(item.items()):

        head_time = str(open(os.path.join(path, key, values[0]), 'r').readline()).split(' ')
        head = head_maker(key, head_time[0])

        channels = {'KBG_EF4 D0 20': []}

        for val in values:
            with open(os.path.join(path, key, val), 'r') as file:
                data_from_file = file.readlines()

                for line in data_from_file:
                    line = line.split(' ')
                    channels['KBG_EF4 D0 20'].append(str(
                        # TODO: change by config value
                        ((-1392.5 * (((0.00000035 * (float(line[2].strip()))) + 0.0001) * 5)) - 73.671) / 10) + '\n')

                del data_from_file

        for head_key, s_values in iter(channels.items()):
            channel = list(head_key.split(' '))[0]
            file_constructor(path=path, key=key, head=head, station='KRBG', channel=channel, head_key=head_key,
                             collector=s_values)

        del channels


def station_pet(item, path):
    for key, values in iter(item.items()):

        head_time = str(open(os.path.join(path, key, values[0]), 'r').readline()).split(' ')
        head = head_maker(key, head_time[0])

        channels = {'PET_EF4-4 D0 20': [],
                    'PET_EF1 D0 20': []}

        for val in values:
            with open(os.path.join(path, key, val), 'r') as file:
                data_from_file = file.readlines()

                for line in data_from_file:
                    line = line.split(' ')

                    if line[1] == '1':
                        channels['PET_EF4-4 D0 20'].append(
                            # TODO: change by config value
                            str((386.63 * (((0.000000345 * (float(line[2].strip()))) + 0.0001) * 3)) + 54.902) + '\n')
                    else:
                        channels['PET_EF1 D0 20'].append(str(
                            # TODO: change by config value
                            ((-6099.5 * (
                                ((0.000000345 * (float(line[2].strip()))) + 0.0001) * 1)) - 185.73) / 5) + '\n')

                del data_from_file

        for head_key, s_values in iter(channels.items()):
            channel = list(head_key.split(' '))[0]
            file_constructor(path=path, key=key, head=head, station='PETG', channel=channel, head_key=head_key,
                             collector=s_values)

        del channels


def create_convert_object(target_folder):
    """
    Create object to convertible format.
    :param target_folder: target folder to convert
    :return: object as dictionary
    """
    result_list = os.listdir(target_folder)
    result_list.sort()
    target_name = os.path.split(target_folder)[1]
    result_dict = {target_name: result_list}
    return result_dict


def run_converter(station_name, target_folder):
    """
    Convert txt files of folder to asc format
    :param station_name: select station name converter
    :param target_folder: target folder to convert
    """
    destination_folder, folder_name = os.path.split(target_folder)
    target_folder = destination_folder
    target_dict = create_convert_object(os.path.join(destination_folder, folder_name))
    """
    :param item: dictionary like an example:
    {'KLY_2020-09-01' = ['00.txt', '01.txt', '02.txt', '03.txt'],
     'KLY_2020-09-02' = ['00.txt', '01.txt', '02.txt', '03.txt']}
    where:
        key = target folder
        values: files of target folder
    :param path: data folder path to store result
    """
    if station_name == "KBG":
        station_kbg(item=target_dict, path=target_folder)
    elif station_name == "SKR":
        station_skr(item=target_dict, path=target_folder)
    elif station_name == "KLY":
        station_kly(item=target_dict, path=target_folder)
    elif station_name == "PET":
        station_pet(item=target_dict, path=target_folder)
    else:
        print("Error")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('name_of_station', type=str, help='display a square of a given number')
    args = parser.parse_args()

    data_path = os.path.split(os.getcwd())[0]

    arg_path = os.path.join(data_path, 'data')
    arg_item = get_list_of_files_in_folder(arg_path)

    if args.name_of_station == "KBG":
        station_kbg(item=arg_item, path=arg_path)
    elif args.name_of_station == "SKR":
        station_skr(item=arg_item, path=arg_path)
    elif args.name_of_station == "KLY":
        station_kly(item=arg_item, path=arg_path)
    elif args.name_of_station == "PET":
        station_pet(item=arg_item, path=arg_path)
    else:
        print("Error")
