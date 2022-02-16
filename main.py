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
    files.init_work_dir(data_folder=config.param['data_folder'])
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
                target_zip_file = os.path.join(config.param['data_folder'], file)
                target_folder = ar.unzip(file_path=target_zip_file,
                                         repeat_in_seconds=config.param['repeat_reading_zip_file_in_seconds'])
                files.move_from_sub_folder(target_folder)
                _target_station_name = station.define_station_by_pathname(target_pathname=target_folder,
                                                                          stations=config.stations)
                _sampling_rate = config.stations[_target_station_name]['sampling_rate']
                parse_response = converter.txt_folder_2_mseed(target_folder=target_folder,
                                                              target_station=_target_station_name,
                                                              stations_opts_map=config.stations,
                                                              sampling_rate=_sampling_rate,
                                                              max_normal_gap=config.param['max_normal_gap'],
                                                              export_ext=config.param['result_ext'],
                                                              logger=logger,
                                                              split_channels=bool(config.param['split_channels']),
                                                              trim_last_hour_values=bool(
                                                                  config.param['trim_last_hour_extra_values'])
                                                              )
                # if exception/error code status => move to exclude folder
                if parse_response == 500:
                    logger.warning(strings.Console().error_stop_parsing_folder.format(folder_name=target_folder))
                    files.move_source_to_exclude_folder(target_source_path=target_zip_file,
                                                        data_folder=config.param['data_folder'])

                # clean files
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
