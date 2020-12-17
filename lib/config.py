scan_data_folder_in_seconds = 10
repeat_reading_zip_file_in_seconds = 5
data_folder = 'data'
result_ext = '.asc'
station_line = {'skr': {'SKRI': lambda x: (x * 0.00000035 + 0.0001) / 0.07865,
                        'SKRG_EF4_2': lambda x: (-717.82 * ((x * 0.00000035 + 0.0001) * 5) + 18.458) * 0.135,
                        'SKRG_EF0001_2': lambda x: (1329.6 * ((x * 0.00000035 + 0.0001) * 5) - 47.295) * 0.141,
                        'SKRP': lambda x: (x * 0.00000035 + 0.0001) * 3.7
                        },
                'kly': {'KLY_EF4-3': lambda x: ((2041 * (((0.000000345 * x) + 0.0001) * 11)) + 42.375) / 4
                        },
                'kbg': {'KBG_EF4': lambda x: ((-1392.5 * (((0.00000035 * x) + 0.0001) * 5)) - 73.671) / 10
                        },
                'pet': {'PET_EF4-4': lambda x: (386.63 * (((0.000000345 * x) + 0.0001) * 3)) + 54.902,
                        'PET_EF1': lambda x: ((-6099.5 * (((0.000000345 * x) + 0.0001) * 1)) - 185.73) / 5
                        }
                }
channels_list = [y for x in
                 [[*station_line[i].keys()] for i in [*station_line.keys()]]
                 for y in x]


def get_station_line(line, station, channel):
    """
    Dynamic value changer for station record output
    :param line: string input number
    :param station: station name
    :param channel: station channel
    :return: formatted string
    """
    x = float(line[2].strip())

    return '{station_line}\n'.format(station_line=str(
        eval(
            str(
                station_line[station][channel](x)
            )
        )
    ))
