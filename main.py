import logging
import os
import time

from loguru import logger

import lib.archive as ar
import lib.files as files
import lib.logger as logger_lib
import lib.station as station
from lib import converter
from lib import strings, pattern
from lib.config import JsonConfig


@logger.catch
def main():
    awaiting_flag = True
    logger_lib.init_logger(strings.__project_name__)
    config = JsonConfig(file_path='config.json')  # importlib.import_module('lib.config')
    logger.info(strings.Console.program_start)
    while True:
        data_files = files.list_data_folder_files(data_folder=config.param['data_folder'])
        # if files are found
        if len(data_files) != 0:
            awaiting_flag = True
            logger.info(strings.Console.reloading_config)
            # importlib.reload(config)
            config = JsonConfig(file_path='config.json')
            for file in data_files:
                logger.info(strings.Console.start_converting.format(file=file))
                # skip if filename format is incorrect
                if not pattern.check_filename_format(name=file):
                    logger.warning(
                        strings.Console.warning_error_filename_format.format(file=file,
                                                                             filename_example=
                                                                             pattern.filename_format_example))
                    # skip file
                    continue
                target_folder = ar.unzip(file_path=os.path.join(config.param['data_folder'], file),
                                         repeat_in_seconds=config.param['repeat_reading_zip_file_in_seconds'])
                files.move_from_sub_folder(target_folder)
                converter.txt_folder_2_mseed(target_folder=target_folder,
                                             target_station=station.define_station_by_pathname(
                                                 target_pathname=target_folder,
                                                 stations=config.stations),
                                             stations_dict=config.stations,
                                             sampling_rate=config.param['sampling_rate'],
                                             max_normal_gap=config.param['max_normal_gap'],
                                             logger=logger,
                                             split_channels=bool(config.param['split_channels']),
                                             trim_last_hour_values=bool(config.param['trim_last_hour_extra_values'])
                                             )
                files.used_files_cleaner(target_folder,
                                         result_ext=config.param['result_ext'])
                files.move_channel_files(target_folder=config.param['data_folder'],
                                         channels_list=config.channels_list,
                                         result_ext=config.param['result_ext'])
                files.get_last_log_files()
            # timer to sleep
            time.sleep(config.param['scan_data_folder_in_seconds'])
        else:
            if awaiting_flag:
                logger.info(strings.Console.wait_files)
                awaiting_flag = False
            # timer to sleep
            time.sleep(config.param['scan_data_folder_in_seconds'])


if __name__ == '__main__':
    main()
