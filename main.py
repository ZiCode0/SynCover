__program_name__ = 'SynCover'

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


@logger.catch
def main():
    awaiting_flag = True
    logger_lib.init_logger(__program_name__)
    config = importlib.import_module('lib.config')
    logger.info('Program {program_name} started.'.format(program_name=__program_name__))
    while True:
        data_files = files.list_data_folder_files()
        # if files are found
        if len(data_files) != 0:
            awaiting_flag = True
            logger.info('Reloading config.')
            importlib.reload(config)
            for file in data_files:
                logger.info('Converting of <{file}> started..'.format(file=file))
                target_folder = ar.unzip(os.path.join(config.data_folder, file))
                files.move_from_sub_folder(target_folder)
                txt2asc.run_converter(station.define_station_by_pathname(target_folder), target_folder)
                files.used_files_cleaner(target_folder)
                files.move_channel_files(config.data_folder)
            # timer to sleep
            time.sleep(config.scan_data_folder_in_seconds)
        else:
            if awaiting_flag:
                logger.info('Waiting for incoming files..')
                awaiting_flag = False
            # timer to sleep
            time.sleep(config.scan_data_folder_in_seconds)


if __name__ == '__main__':
    main()
