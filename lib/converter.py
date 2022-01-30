import argparse
import datetime
import os
import re
import sys
from datetime import datetime, timedelta

import obspy

from lib import export
from lib import strings
from lib import sample_count


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


def asc_file_constructor(path, key, head, station, channel, head_key, collector, result_ext):
    file_wr = open(os.path.join(path,
                                key + '_{channel}'.format(channel=channel) + result_ext), 'a')
    file_wr.write('\n{head} {station} {head_key} {size}\n'.format(head=head,
                                                                  station=station,
                                                                  channel=channel,
                                                                  head_key=head_key,
                                                                  size=len(collector)))
    file_wr.writelines(collector)
    file_wr.close()


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


def trim_extra_values_for_last_trace_hour(mseed, logger=None):
    """
    Trim extra values in last hour because of "back-in-time" lags and non-normal delta of sample in raw records
    :param logger: print log information about trimmed length
    :param mseed: target mseed file with trace records
    :return: trimmed stream
    """
    for trace in mseed:
        # check if less than 1 hour data and starts from zero 00:00:00.0 datetime
        hours_more_or_equal_1 = ((trace.stats.endtime - trace.stats.starttime) / (60 * 60)) > 1
        zero_start = str(trace.stats.starttime.time) == '00:00:00'
        # parse trace if length is more than
        if zero_start and hours_more_or_equal_1:
            end_time = trace.stats.endtime
            # make endtime to format "YEAR-MONTH-DAY_00:00:00.0 - delta"
            trim_utc_datetime = obspy.UTCDateTime(end_time.year, end_time.month, end_time.day,
                                                  end_time.hour, 0, 0, 0) - timedelta(seconds=trace.stats.delta)
            # get time delta size to trim
            time_delta = end_time - trim_utc_datetime
            samples_number = str(int(time_delta * 50))
            # trim with new endtime marker
            trace.trim(starttime=trace.stats.starttime,
                       endtime=trim_utc_datetime)
            if logger:
                logger.warning(strings.Console.warning_dropped_samples.format(channel=trace.id,
                                                                              samples_time=str(time_delta),
                                                                              samples_number=samples_number
                                                                              ))
        # print()  # enable for #debug
    return mseed


def station_any(file_items: dict, path: str, target_station: str,
                stations_dict: dict, sampling_rate: float,
                max_normal_gap=0.0, logger=None, split_channels=False, trim_last_hour_values=False):
    """
    Make mseed file using obspy
    :param trim_last_hour_values: trim last hour extra values because of non-normal samples delta
    :param split_channels: each result channel to mseed. Default: False
    :param file_items: dictionary with list of channel target files to parse
    :param path: target folder path
    :param target_station: station
    :param stations_dict: dictionary with station params
    :param sampling_rate: sampling rate of data
    :param max_normal_gap: normal gap between records to ignore split. Default: 0.0 - to skip
    :param logger: loguru logger object **optional. Default: None - to skip
    :return:
    """
    # normal delta according sampling rate
    samples_delta = 1 / sampling_rate
    # calc number of decimals in float
    delta_after_point_numbers = len(str(samples_delta).split('.')[1])
    # make channels buffer
    channels = {i: []
                for i in stations_dict[target_station]}
    channel_number_aliases = [i for i in channels]

    start_file_date = None
    # datetime buffers
    datetime_last = {}
    datetime_now = {}
    # flag for first init
    first_parse = {i: True for i in channels}  # [True] * len(channels)
    # full channel name buffer
    channel_folder_name = ''
    datetime_line_now = {}
    datetime_line_last = {}

    calc_gaps = {i: [] for i in channels}

    # parse all files for each channel
    for channel_folder_name, parts in iter(file_items.items()):
        # start file date with zero time
        if not start_file_date:
            start_file_date = make_start_datetime(date_string=channel_folder_name)

        # for every file
        for file_part in parts:
            print(file_part)  # enable for #debug
            with open(os.path.join(path, channel_folder_name, file_part), 'r') as file:
                # get all raw data lines
                data_from_file = file.readlines()
                # parse all lines
                for line_index in range(len(data_from_file)):
                    # split line
                    line = data_from_file[line_index].split(' ')
                    channel_index = int(line[1]) - 1
                    # get name by station
                    # check if channel with target index exist
                    try:
                        channel_full_name = channel_number_aliases[channel_index]
                    except IndexError:
                        continue
                    # get now datetime by current sample string line
                    datetime_line_now[channel_full_name] = make_datetime(date=start_file_date, time_str=line[0])
                    # add first hour:min:sec:ms to start time
                    if first_parse[channel_full_name]:
                        # init first channel record part object
                        channels[channel_full_name] = [
                            {'data': [],
                             'start_time': start_file_date,
                             # make_datetime(date=start_file_date, time_str='00:00:00.0'),
                             'end_time': None}]
                        # mark for passed first run
                        first_parse[channel_full_name] = False
                        # init line last datetime
                        datetime_line_last[channel_full_name] = datetime_line_now[channel_full_name]
                    # calc current delta
                    # round by calculated numbers after point
                    current_delta = round((datetime_line_now[channel_full_name] - datetime_line_last[channel_full_name])
                                          .total_seconds(),
                                          delta_after_point_numbers)
                    # check if datetime jumped back and
                    if current_delta < 0:
                        # lag in seconds
                        sec_lag = round(current_delta / sampling_rate, 6)
                        # print warning
                        logger.warning(strings.Console.warning_back_time_lag.format(channel=channel_full_name,
                                                                                    sec_lag=sec_lag,
                                                                                    channel_folder_name=channel_folder_name,
                                                                                    file_part=file_part,
                                                                                    line_index=line_index))

                        # number of samples for each channel to check
                        sample_count_check = 5
                        # buffer of datetime objects for channels
                        _dt_to_check = {i: [] for i in channels}
                        # parse to add buffer channel values
                        for i in range(sample_count_check * len(channels)):
                            try:
                                # get temp string
                                _dt_str, _ch_index, _ = data_from_file[line_index + i].split(' ')
                                # make datetime
                                _dt = make_datetime(start_file_date, _dt_str)
                                # add to buffer according to channel
                                _dt_to_check[channel_number_aliases[int(_ch_index) - 1]].append(_dt)
                            except:
                                # skip on errors
                                pass
                        del _dt_str, _ch_index, _dt, _, i
                        if not check_datetime(datetime_str_list=_dt_to_check,
                                              max_normal_gap=max_normal_gap):
                            # if problems with gaps in some samples delta
                            if logger:
                                # print warning
                                logger.error(strings.Console.error_back_time_lag)
                                # try to exit
                                quit(0)
                                sys.exit()
                        del _dt_to_check

                    try:
                        # channel number as int
                        target_number = int(line[2])
                        # get exact value by expression
                        # disable for #debug
                        # e_value = evaluate_channel_value(value=target_number,
                        #                                  station=target_station,
                        #                                  channel=channel_full_name,
                        #                                  stations_dict=stations_dict)
                        e_value = target_number  # toggle for #debug

                        # #debug to check gap size
                        # if current_delta <= samples_delta:
                        #     seconds_delta = (datetime_line_now[channel_full_name] - datetime_line_last[channel_full_name]).total_seconds()
                        #     delta_gap = samples_delta - seconds_delta
                        #     # print(f'{channel_full_name:20s} {line_index:10.0f} {seconds_delta:.7f} {delta_gap:2.7f}')
                        #     calc_gaps[channel_full_name].append(delta_gap)

                        # check to find gaps
                        if (current_delta <= samples_delta) or (current_delta < max_normal_gap):
                            # if delta is normal
                            # add to temp station buffer
                            channels[channel_full_name][-1]['data'].append(e_value)
                        # split trace because of gap found
                        else:
                            _record_time_gap_before = sample_count.calc_dt(records_list=channels[channel_full_name],
                                                                           start_file_datetime=start_file_date,
                                                                           samples_delta=samples_delta)
                            _record_time_gap_after = _record_time_gap_before + timedelta(seconds=current_delta + samples_delta)

                            # _trace_buffer_size = len(channels[channel_full_name][-1]['data'])

                            # _gap_in_samples = current_delta * sampling_rate
                            # _delta_from_start_in_dt_end = start_file_date + timedelta(
                            #     seconds=samples_delta * _total_trace_size)
                            # _delta_from_start_in_dt_start = start_file_date + timedelta(
                            #     seconds=samples_delta * (_total_trace_size + _gap_in_samples))  # + samples_delta)
                            #

                            # log warning output about gap
                            if logger:
                                logger.warning(strings.Console.warning_gap_found.format(channel=channel_full_name,
                                                                                        folder=channel_folder_name,
                                                                                        file=file_part,
                                                                                        gap_value=current_delta,
                                                                                        gap_time=line[0],
                                                                                        line_number=line_index))
                            # print()  # enable for #debug
                            # if delta is not normal => gap => devide Trace
                            # set last datetime as endtime
                            channels[channel_full_name][-1][
                                'end_time'] = _record_time_gap_before  # datetime_last[channel_full_name]
                            # create new trace buffer
                            channels[channel_full_name].append(
                                {'data': [e_value, ], 'start_time': _record_time_gap_after, 'end_time': None})
                            # free memory
                            del _record_time_gap_after, _record_time_gap_before
                            # del _total_trace_size, _gap_in_samples, _delta_from_start_in_dt_end, _delta_from_start_in_dt_start
                    # ignore bad values
                    except Exception as ex:
                        if logger:
                            logger.warning(
                                strings.Console.warning_error_read_data.format(value=data_from_file[line_index].split('\n')[0],
                                                                               line_number=line_index,
                                                                               ex=ex
                                                                               ))
                    # set last datetime
                    # datetime_last[channel_full_name] = datetime_now[channel_full_name]
                    # set last channel datetime object
                    # channels[channel_full_name][-1]['end_time'] = datetime_last[channel_full_name]

                    # set last line datetime
                    datetime_line_last[channel_full_name] = datetime_line_now[channel_full_name]

                # remove file buffer
                del data_from_file

    # channels = trim_to_normal_max_day_size(channels_data_dict=channels, sampling_rate=sampling_rate)
    mseed = export.make_stream_mseed(channels_data_dict=channels, sampling_rate=sampling_rate)
    del channels
    if trim_last_hour_values:
        mseed = trim_extra_values_for_last_trace_hour(mseed, logger=logger)

    # del channels, datetime_last, datetime_now # disable for #debug

    # print result traces
    if logger:
        logger.success(strings.Console.result_stream.format(stream_text=mseed))

    # check split channels required
    if split_channels:
        # write each channel in separate mseed
        for trace in mseed:
            out_path = os.path.join(path, f'{channel_folder_name}_{trace.stats.channel}.mseed')
            trace.write(filename=out_path)
    else:
        # write each channel data in one mseed file
        out_path = os.path.join(path, f'{channel_folder_name}.mseed')
        mseed.write(filename=out_path)
    del mseed
    # print()  # enable for #debug


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


def txt_folder_2_mseed(target_folder, target_station, stations_dict, sampling_rate,
                       max_normal_gap=0.03, logger=None, split_channels=False, trim_last_hour_values=False):
    """
    Convert txt files of target folder to asc format
    :param trim_last_hour_values:
    :param split_channels:
    :param logger:
    :param max_normal_gap:
    :param sampling_rate:
    :param target_station: select target station
    :param stations_dict: dictionary of input channels information
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
        key: target folder
        values: files of target folder
    :param path: data folder path to store result
    """

    station_any(file_items=target_dict, path=target_folder, target_station=target_station,
                stations_dict=stations_dict, sampling_rate=sampling_rate, max_normal_gap=max_normal_gap,
                logger=logger, split_channels=split_channels, trim_last_hour_values=trim_last_hour_values)


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
                       stations_dict=args.config.stations,
                       sampling_rate=args.config.param['sampling_rate'],
                       max_normal_gap=args.config.param['max_normal_gap'],
                       logger=None,
                       split_channels=bool(args.config.param['split_channels']))
