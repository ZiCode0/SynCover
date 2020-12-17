import importlib
import os
import time

from loguru import logger

import lib.archive as ar
# import lib.config as config
import lib.files as files
import lib.logger as logger_lib
import lib.station as station
import lib.txt2asc as txt2asc
from lib import strings


@logger.catch
def main():
    awaiting_flag = True
    logger_lib.init_logger(strings.__program_name__)
    config = importlib.import_module('lib.config')
    logger.info(strings.Console.program_start)
    while True:
        data_files = files.list_data_folder_files()
        # if files are found
        if len(data_files) != 0:
            awaiting_flag = True
            logger.info(strings.Console.reloading_config)
            importlib.reload(config)
            for file in data_files:
                logger.info(strings.Console.start_converting.format(file=file))
                target_folder = ar.unzip(os.path.join(config.data_folder, file))
                files.move_from_sub_folder(target_folder)
                txt2asc.run_converter(station.define_station_by_pathname(target_folder), target_folder)
                files.used_files_cleaner(target_folder)
                files.move_channel_files(config.data_folder)
            # timer to sleep
            time.sleep(config.scan_data_folder_in_seconds)
        else:
            if awaiting_flag:
                logger.info(strings.Console.wait_files)
                awaiting_flag = False
            # timer to sleep
            time.sleep(config.scan_data_folder_in_seconds)


if __name__ == '__main__':
    main()
