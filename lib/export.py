import datetime

import numpy as np
import obspy


def make_stream_mseed(channels_data_dict: dict,
                      sampling_rate: float):
    # result buffer
    stream = obspy.Stream()
    # parse all channels
    for key in channels_data_dict:
        # set temp current channel var
        current_channel = channels_data_dict[key]
        # if channel is not empty
        if len(current_channel) > 0:
            # convert channel parts to traces
            for part_index in range(len(current_channel)):
                # get part object
                part_object = current_channel[part_index]
                # make trace based on part object data
                current_channel[part_index] = make_trace(data=part_object['data'],
                                                         ch_name_full=key,
                                                         sampling_rate=sampling_rate,
                                                         starttime=part_object['start_time'],
                                                         # endtime=part_object['end_time']
                                                         )
        # if any parts
        if len(current_channel) > 1:
            channel_trace = None
            # merge trace parts
            for part_index in range(len(current_channel)):
                # free trace part object buffer
                # del part_object
                # init first trace
                channel_trace = current_channel[0]
                # parse all trace parts
                for idx in range(1, len(current_channel)):
                    # concatenate trace using __add__ function. gaps to fill with zeros.
                    channel_trace = channel_trace.__add__(current_channel[idx], fill_value=0)
            # add to result
            stream.append(channel_trace)
        else:
            # add 1 part to result buffer
            stream.append(current_channel[0])

    # print()  # enable for #debug
    return stream


def make_trace(data: list,
               ch_name_full,
               sampling_rate,
               starttime: datetime.datetime,
               endtime=None):
    """
    Form ObsPy Trace object using data list, full channel name and time
    :param sampling_rate: data sampling rate
    :param ch_name_full: target channel name. Example: "KLY_PG D0 20"
    :param data: target data list
    :param starttime: start datetime of trace
    :param endtime: end datetime of trace. :type: datetime.datetime or None
    :return:
    """
    # ch_name_full = channel_number_aliases[ch_name_index]
    ch_station_with_channel, ch_network, ch_location = ch_name_full.split(' ')
    ch_station, ch_channel = ch_station_with_channel.split('_')
    try:
        endtime = obspy.UTCDateTime(endtime)
    except:
        endtime = None

    array = np.array(
        data,
        # channels[ch_name_full],
        dtype='float32')
    trace = obspy.Trace(data=array,
                        header={'network': f'{ch_network}',
                                'station': f'{ch_station}',
                                'location': f'{ch_location}',
                                'channel': f'{ch_channel}',
                                'starttime': obspy.UTCDateTime(starttime),
                                'endtime': endtime,
                                'sampling_rate': sampling_rate,
                                'npts': len(array),
                                '_format': 'MSEED',
                                }
                        )
    # print(trace)  # enable for #debug
    return trace
