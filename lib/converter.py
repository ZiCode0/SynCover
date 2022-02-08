import argparse
import datetime
import os
import re

import numpy as np
import obspy

from datetime import datetime, timedelta
from io import StringIO, BytesIO

from lib import strings


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


def get_station_line(line, station, channel, stations_dict):
    """
    Dynamic value changer for station record output
    :param stations_dict: dictionary with input config stations
    :param line: string input number
    :param station: station name
    :param channel: station channel
    :return: formatted string
    """
    x = float(line[2].strip())

    return '{station_line}\n'.format(station_line=str(
        eval(stations_dict[station][channel])(x)
    ))


def evaluate_channel_value(value, station, channel, stations_dict):
    # x = float(line[2].strip())
    return eval(stations_dict[station][channel])(value)


def make_start_datetime(date_string: str):
    """
    Form start datetime
    :param date_string: target datetime string
    :return: datetime.datetime object
    """
    date = re.sub(r'^.*?_', '_', date_string)[1:]
    dt_date = datetime.strptime(date, '%Y-%m-%d')
    return dt_date


def make_datetime(date: datetime, time_str: str):
    """
    Combine base date `datetime` object with time as `string`
    :param date:
    :param time_str:
    :return:
    """
    t = datetime.strptime(time_str, '%H:%M:%S.%f')
    delta = timedelta(hours=t.hour, minutes=t.minute,
                      seconds=t.second, microseconds=t.microsecond)
    return date + delta


def check_datetime(datetime_str_list, max_normal_gap):
    for channel_name in datetime_str_list:
        current_channel = datetime_str_list[channel_name]
        # calc each delta
        for item_index in range(len(current_channel) - 1):
            # calc delta
            delta = (current_channel[item_index + 1] - current_channel[item_index]).total_seconds()
            if delta >= max_normal_gap:
                # if non-normal gap
                return False
    return True


# def trim_extra_values_for_last_trace_hour(mseed, logger=None):
#     """
#     Trim extra values in last hour because of "back-in-time" lags and non-normal delta of sample in raw records
#     :param logger: print log information about trimmed length
#     :param mseed: target mseed file with trace records
#     :return: trimmed stream
#     """
#     for trace in mseed:
#         # check if less than 1 hour data and starts from zero 00:00:00.0 datetime
#         hours_more_or_equal_1 = ((trace.stats.endtime - trace.stats.starttime) / (60 * 60)) > 1
#         zero_start = str(trace.stats.starttime.time) == '00:00:00'
#         # parse trace if length is more than
#         if zero_start and hours_more_or_equal_1:
#             end_time = trace.stats.endtime
#             # make endtime to format "YEAR-MONTH-DAY_00:00:00.0 - delta"
#             trim_utc_datetime = obspy.UTCDateTime(end_time.year, end_time.month, end_time.day,
#                                                   end_time.hour, 0, 0, 0) - timedelta(seconds=trace.stats.delta)
#             # get time delta size to trim
#             time_delta = end_time - trim_utc_datetime
#             samples_number = str(int(time_delta * 50))
#             # trim with new endtime marker
#             trace.trim(starttime=trace.stats.starttime,
#                        endtime=trim_utc_datetime)
#             if logger:
#                 logger.warning(strings.Console.warning_dropped_samples.format(channel=trace.id,
#                                                                               samples_time=str(time_delta),
#                                                                               samples_number=samples_number
#                                                                               ))
#         # print()  # enable for #debug
#     return mseed


def trim_extra_values_for_last_trace_hour(trace: obspy.Trace, extra_values_sec_max=60, logger=None):
    """
        Trim extra values in last hour because of non-normal delta of sample in raw records
        Trim on extra values:  < 1min
        Get warning and skip:  > 1min
        :param trace: target trace record
        :param extra_values_sec_max: max limit seconds to trim. else => warning and skip
        :param logger: print log information about trimmed length
        :return: trimmed stream
    """
    # check if less than 1 hour data and starts from zero 00:00:00.0 datetime
    _hours_more_or_equal_1 = ((trace.stats.endtime - trace.stats.starttime) / (60 * 60)) > 1
    if _hours_more_or_equal_1:
        # vars to calc extra last hour tail
        _end_time = trace.stats.endtime
        _end_time_last_hour_start = obspy.UTCDateTime(_end_time.year, _end_time.month, _end_time.day, _end_time.hour,
                                                      0, 0, 0)
        # make endtime to format "YEAR-MONTH-DAY_00:00:00.0 - delta"
        last_hour_time = _end_time - _end_time_last_hour_start
        # make warning because of long extra values in last trace hour
        if last_hour_time > extra_values_sec_max:
            if logger:
                logger.warning(strings.Console().warning_extra_last_seconds_found.format(extra_sec=last_hour_time,
                                                                                         normal_sec=extra_values_sec_max))
            else:
                print(strings.Console().warning_extra_last_seconds_found.format(extra_sec=last_hour_time,
                                                                                normal_sec=extra_values_sec_max))
        # if normal extra values tail => trim trace
        else:
            # trim trace data
            trace.trim(trace.stats.starttime, _end_time_last_hour_start)

    return trace


def make_tspair_buffer_header(channel_name: str,
                              sampling_rate: float,
                              datetime_start_obj: datetime,
                              data_type='INTEGER',
                              data_quality='D'):
    # Header example: TIMESERIES D0_KBG_20_PG1_D, 5 samples, 50 sps, 2021-05-21T00:00:05.0, TSPAIR, INTEGER, Counts
    # channel name format example: NETWORK_STATION_PLACE_CHANNEL_QUALITY(DEFAULT=D)
    #
    # Data quality flags:
    # > D — The state of quality control of the data is indeterminate.
    #   R — Raw Waveform Data with no Quality Control
    #   Q — Quality Controlled Data, some processes have been applied to the data.
    #   M — Data center modified, time-series values have not been changed.
    # >> dev mention: .split('.')[0]
    # OBSPY UTCDATETIME FORMAT: '%Y%m%d%H%M%S'
    datetime_start_str = datetime_start_obj.strftime(
        '%Y%m%d%H%M%S.%f')  # '%Y-%M-%dT%H:%M:%S.%f'  # strings.datetime_format
    return f'\n\nTIMESERIES {channel_name}_{data_quality}, 0 samples, {sampling_rate} sps, {datetime_start_str}, TSPAIR, {data_type}, Counts\n'


def create_tspair_io_buffer_object(**headers_args):
    sio = StringIO()
    # sio += (make_tspair_buffer_header(**headers_args))  # for str
    sio.writelines(make_tspair_buffer_header(**headers_args))
    # sio.getvalue()  # enable for #debug
    return sio


def station_any(target_objects: dict,
                out_path: str, station_opts_map: dict,
                sampling_rate: float, max_normal_gap=0.0, export_ext='.mseed',
                logger=None, split_channels=False, trim_last_hour_values=False):
    """
    Make mseed file using obspy
    :param trim_last_hour_values: trim last hour extra values because of non-normal samples delta
    :param split_channels: each result channel to mseed. Default: False
    :param target_objects: dictionary with list of channel target files to parse
    :param out_path: output result folder
    :param station_opts_map: dictionary with station params
    :param sampling_rate: sampling rate of data
    :param max_normal_gap: normal gap between records to ignore split. Default: 0.0 - to skip
    :param logger: loguru logger object **optional. Default: None - to skip
    :return:
    """
    # normal delta according sampling rate
    samples_delta = 1 / sampling_rate
    # calc number of decimals in float
    delta_after_point_numbers = len(str(samples_delta).split('.')[1])
    # buffers for parsable datetime objects
    l_datetime_now = {}
    l_datetime_prev = {}

    for s_name, s_parts in iter(target_objects.items()):
        # make channels buffer
        s_channels = {i: None for i in station_opts_map[s_name]}
        # init station channel names
        s_channel_number_aliases = [i for i in s_channels]
        # flag for first init
        s_channel_first_parse = {i: True for i in s_channels}  # [True] * len(channels)
        # use folder name to get date
        _folder_name_for_start_date = return_target_folder_name_from_path(s_parts[0])
        # make start datetime object
        s_datetime_start = make_start_datetime(date_string=_folder_name_for_start_date)
        # make start datetime object as str ( for speed-up :D )
        s_datetime_start_data_str = s_datetime_start.strftime(strings.date_start_format)

        # for every file
        for part_path in s_parts:
            # print current part path
            # if logger:
            #     logger.info(f'Parsing part file: {part_path}..')  # enable for #debug to print current part
            # open part file
            with open(part_path, 'r') as _f:
                # get all raw data lines
                data_from_part = _f.readlines()
                # parse all lines
                for line_index in range(len(data_from_part)):
                    # split line on defined var parts
                    l_datetime_text, l_channel_index, l_value_text = data_from_part[line_index].split(' ')
                    # channel idx correction
                    l_channel_index = int(l_channel_index) - 1
                    # get name by station
                    # check if channel with target index exist
                    try:
                        l_channel_full_name = s_channel_number_aliases[l_channel_index]
                    except IndexError:
                        continue
                    # print(l_datetime_text, l_channel_full_name, l_value_text)  # enable for #debug
                    # get now datetime by current sample string line
                    l_datetime_now[l_channel_full_name] = make_datetime(date=s_datetime_start,
                                                                        time_str=l_datetime_text)

                    # add first hour:min:sec:ms to start time
                    if s_channel_first_parse[l_channel_full_name]:
                        # mark for passed first run
                        s_channel_first_parse[l_channel_full_name] = False
                        # init channel buffer
                        s_channels[l_channel_full_name] = create_tspair_io_buffer_object(
                            channel_name=l_channel_full_name,
                            sampling_rate=sampling_rate,
                            datetime_start_obj=
                            l_datetime_now[
                                l_channel_full_name]
                        )
                        # init line last datetime
                        l_datetime_prev[l_channel_full_name] = l_datetime_now[l_channel_full_name]
                    # calc current delta
                    # round by calculated numbers after point
                    current_delta = round((l_datetime_now[l_channel_full_name] - l_datetime_prev[l_channel_full_name])
                                          .total_seconds(),
                                          delta_after_point_numbers)
                    # check if datetime jumped back and
                    if current_delta < 0:
                        # lag in seconds
                        sec_lag = round(current_delta / sampling_rate, 6)
                        # print warning
                        logger.warning(strings.Console.warning_back_time_lag.format(channel=l_channel_full_name,
                                                                                    file_part=part_path,
                                                                                    sec_lag=sec_lag,
                                                                                    line_index=line_index))
                        # RETURN FAIL STATUS
                        return 500

                    try:
                        # check to find gaps
                        # # if delta is normal
                        if (current_delta <= samples_delta) or (current_delta < max_normal_gap):
                            # prepare datetime record str
                            # dt_cur = make_datetime(date=s_datetime_start, time_str=l_datetime_text)
                            # dt_cur_str = dt_cur.strftime(strings.datetime_format)
                            dt_cur_str = (s_datetime_start_data_str + l_datetime_text).replace(':',
                                                                                               '')  # .replace('.', '')
                            _str = f'{dt_cur_str} {l_value_text}'
                            # add to temp station buffer
                            # s_channels[l_channel_full_name] += _str  # for str
                            s_channels[l_channel_full_name].writelines(_str)  # for stringio

                            # print(s_channels[l_channel_full_name].getvalue())
                        # # split trace because of gap found
                        else:
                            # log warning output about gap
                            if logger:
                                logger.warning(strings.Console.warning_gap_found.format(channel=l_channel_full_name,
                                                                                        file_part=part_path,
                                                                                        gap_value=current_delta,
                                                                                        gap_time=l_datetime_text,
                                                                                        line_number=line_index))
                            # add next part header to buffer
                            _str = make_tspair_buffer_header(
                                channel_name=l_channel_full_name,
                                sampling_rate=sampling_rate,
                                datetime_start_obj=l_datetime_now[l_channel_full_name])
                            # s_channels[l_channel_full_name] += _str  # for str
                            s_channels[l_channel_full_name].writelines(_str)  # for StringIO
                            # print()  # enable for #debug

                    # ignore bad values
                    except Exception as ex:
                        if logger:
                            logger.warning(
                                strings.Console.warning_error_read_data.format(
                                    value=data_from_part[line_index].split('\n')[0],
                                    line_number=line_index,
                                    ex=ex
                                ))

                    # set last line datetime
                    l_datetime_prev[l_channel_full_name] = l_datetime_now[l_channel_full_name]

        # make export buffer
        export_targets = []
        # if split_channels disabled => using common single obspy.Stream() temp buffer
        if not split_channels:
            export_targets.append(obspy.Stream())

        # prepare and export stream channel objects
        for _key, value in s_channels.items():
            # if channel buffer exist
            if value:
                # get raw stream object
                _channel_stream = obspy.read(BytesIO(value.getvalue().encode()),
                                             format="TSPAIR",
                                             dtype=np.dtype(np.int16))
                # fill missed channel stream object params
                for _trace_part in _channel_stream:
                    _trace_part.stats.npts = _trace_part.data.size
                    _trace_part.meta.npts = _trace_part.data.size

                # trim last channel part if trim_last_hour_values selected
                if trim_last_hour_values:
                    _channel_stream[-1] = trim_extra_values_for_last_trace_hour(trace=_channel_stream[-1],
                                                                                logger=logger)

                # add separate channels stream
                if split_channels:
                    export_targets.append(_channel_stream)
                # add channel to common single stream
                else:
                    export_targets[0] += _channel_stream
        del s_channels

        # export targets
        for target in export_targets:
            # export/write result files
            _out_path_f_name = f'{_folder_name_for_start_date}_{target.traces[0].id}{export_ext}'
            _out_path_file = os.path.join(out_path, _out_path_f_name)
            # write to mseed format
            # # define file export format by extension postfix
            target.write(_out_path_file)  # , format="MSEED"
            # print result traces
            if logger:
                logger.success(strings.Console.success_channel_report.format(stream_object=target,
                                                                             file_path=_out_path_file))
            # print()  # enable for #debug

    # return OK status
    return 200


def create_convert_object(target_folder):
    """
    Create object to convertible format.
    :param: target_folder: target folder to convert
    :return: object as dictionary
    """
    result_list = os.listdir(target_folder)
    result_list.sort()
    target_name = os.path.split(target_folder)[1]
    result_dict = {target_name: result_list}
    return result_dict


def create_target_objects_dict(target_station: str, target_folder: str):
    """
    Create object to convertible format.
    :param: target_folder: target folder to convert
    :return: object as dictionary
    """
    result_list = os.listdir(target_folder)
    result_list.sort()
    target_folder_name_for_date = os.path.split(target_folder)[-1]
    result_dict = {target_station: [os.path.join(target_folder, i) for i in result_list]}
    return result_dict


def return_target_folder_name_from_path(path):
    # Get 'KBG_2021-05-21' from 'data/KBG_2021-05-21/00.txt'
    head = os.path.split(path)[-2]
    return os.path.split(head)[-1]


def txt_folder_2_mseed(target_folder, target_station, stations_opts_map, sampling_rate,
                       max_normal_gap=0.03, logger=None, split_channels=False, trim_last_hour_values=False):
    """
    Convert txt files of target folder to asc format
    :param trim_last_hour_values:
    :param split_channels:
    :param logger:
    :param max_normal_gap:
    :param sampling_rate:
    :param target_station: select target station
    :param stations_opts_map: dictionary of input channels information
    :param target_folder: target folder to convert
    """
    output_folder, _ = os.path.split(target_folder)
    target_objects = create_target_objects_dict(target_station=target_station,
                                                target_folder=target_folder)
    """
    :param item: dictionary like an example:
    {'kbg': ['data/KBG_2021-05-21/00.txt',
             'data/KBG_2021-05-21/01.txt',
             'data/KBG_2021-05-21/02.txt',
             'data/KBG_2021-05-21/03.txt']}
    where:
        key: target station
        values: target part paths
    """
    response = station_any(target_objects=target_objects,
                           out_path=output_folder, station_opts_map=stations_opts_map,
                           sampling_rate=sampling_rate, max_normal_gap=max_normal_gap,
                           logger=logger, split_channels=split_channels, trim_last_hour_values=trim_last_hour_values)
    return response


if __name__ == '__main__':
    from lib import config

    app_name = 'SynCover.console'
    app_version = 2.1
    author = 'ZiCode0'
    contacts = '[Telegram] @MrFantomz'
    # args = None

    # define program description
    text = '{app_name} converter txt_files=>mseed by {author} v.{app_version}\nContacts: {contacts}'.format(
        app_name=app_name,
        author=author,
        app_version=app_version,
        contacts=contacts)
    parser = argparse.ArgumentParser(description=text)
    parser.add_argument('station_name', type=str, help='target station name')
    parser.add_argument('config', type=str, help='path to "config.json" file')
    args = parser.parse_args()

    # init paths
    data_path = os.path.split(os.getcwd())[0]
    arg_path = os.path.join(data_path, 'data')
    arg_item = get_list_of_files_in_folder(arg_path)

    # init config.json
    args.config = config.JsonConfig(file_path=str(args.config))

    txt_folder_2_mseed(target_folder=arg_path,
                       target_station=args.station_name,
                       stations_opts_map=args.config.stations,
                       sampling_rate=args.config.param['sampling_rate'],
                       max_normal_gap=args.config.param['max_normal_gap'],
                       logger=None,
                       split_channels=bool(args.config.param['split_channels']))
