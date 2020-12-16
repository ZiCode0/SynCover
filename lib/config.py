scan_data_folder_in_seconds = 10
repeat_reading_zip_file_in_seconds = 5
data_folder = 'data'


def get_station_line(line, station, channel):
    float_line = float(line[2].strip())
    station_line = {'skr': {'SKRI':         (float_line * 0.00000035 + 0.0001) / 0.07865,
                            'SKRG_EF4_2':   (-717.82 * ((float_line * 0.00000035 + 0.0001) * 5) + 18.458) * 0.135,
                            'SKRG_EF0001_2': (1329.6 * ((float_line * 0.00000035 + 0.0001) * 5) - 47.295) * 0.141,
                            'SKRP':         (float_line * 0.00000035 + 0.0001) * 3.7
                            },
                    'kly': {'KLY_EF4-3': ((2041 * (((0.000000345 * float_line) + 0.0001) * 11)) + 42.375) / 4
                            },
                    'kbg': {'KBG_EF4': ((-1392.5 * (((0.00000035 * float_line) + 0.0001) * 5)) - 73.671) / 10
                            },
                    }

    return '{station_line}\n'.format(station_line=str(station_line[station][channel]))
