__project_name__ = 'SynCover'
datetime_format = '%Y%M%d%H%M%S%f'
date_start_format = '%Y%m%d'


class Console:
    program_start = 'Program {project_name} started.'.format(project_name=__project_name__)
    reloading_config = 'Reloading config.'
    start_converting = 'Converting of <{file}> started..'
    wait_files = 'Waiting for incoming files..'

    success_channel_report = 'Result channel file <{file_path}> saved: {stream_object}'

    warning_error_filename_format = 'File name format for <{file}> is incorrect. Correct example: {filename_example}.'
    warning_error_read_data = 'Error reading: "{value}", line: {line_number} line.\n{ex}.'
    warning_back_time_lag = 'Channel <{channel}>: "back-in-time" {sec_lag} sec. lag detected in file: {file_part}, line: {line_index}.'
    warning_dropped_samples = 'Channel <{channel}>: {samples_time} sec ({samples_number} samples) dropped from the end of trace.'
    warning_gap_found = 'Channel <{channel}>: "{gap_value}" sec. gap found, file: <{file_part}>, time: {gap_time}, line: {line_number}'
    warning_extra_last_seconds_found = 'Last hour extra values({extra_sec}sec) more than normal {normal_sec}sec, skip trimming.'

    error_stop_parsing_folder = 'Stop parsing <{folder_name}> folder..'
    error_back_time_lag = 'Problems with values delta after "back-in-time" lag, exit..'


class Report:
    mail_subject = '{project_name}: Error report'.format(project_name=__project_name__)
