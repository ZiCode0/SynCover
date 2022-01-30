import os


def define_station_by_pathname(target_pathname, stations):
    """
    Return station name according to name of file.
    :param: target_pathname: target file name
    :return: string of station name / None
    """
    target_pathname = os.path.basename(target_pathname).lower()
    for station_name in stations:
        station_name = station_name.lower()
        if station_name in target_pathname:
            return station_name
    return None
