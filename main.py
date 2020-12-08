import os
import time
import importlib

import lib.archive as ar
# import lib.config as config
import lib.files as files
import lib.station as station
import lib.txt2asc as txt2asc


if __name__ == '__main__':
    config = importlib.import_module('lib.config')
    while True:
        data_files = files.list_data_folder_files()
        if len(data_files) != 0:
            importlib.reload(config)
            print(config.scan_data_folder_in_seconds)
            for file in data_files:
                target_folder = ar.unzip(os.path.join(config.data_folder, file))
                files.move_from_sub_folder(target_folder)
                txt2asc.run_converter(station.define_station_by_pathname(target_folder), target_folder)
                files.used_files_cleaner(target_folder)
            # timer to sleep
            time.sleep(config.scan_data_folder_in_seconds)
