__project_name__ = 'SynCover'


class Console:
    program_start = 'Program {project_name} started.'.format(project_name=__project_name__)
    reloading_config = 'Reloading config.'
    start_converting = 'Converting of <{file}> started..'
    wait_files = 'Waiting for incoming files..'
    warning_error_filename_format = 'File name format for <{file}> is incorrect. Correct example: {filename_example}.'
    warning_error_read_data = 'Error reading: "{value}", line: {line_number} line.\n{ex}.'
    result_stream = 'Result object: {stream_text}'
    warning_back_time_lag = 'Channel <{channel}>: "back-in-time" {sec_lag} sec. lag detected in file: {channel_folder_name}/{file_part}, line: {line_index}.'
    error_back_time_lag = 'Problems with values delta after "back-in-time" lag, exit..'
    warning_dropped_samples = 'Channel <{channel}>: {samples_time} sec ({samples_number} samples) dropped from the end of trace.'
    warning_gap_found = 'Channel <{channel}>: "{gap_value}" sec. gap found, file: {folder}/{file}, time: {gap_time}, line: {line_number}'


class Report:
    mail_subject = '{project_name}: Error report'.format(project_name=__project_name__)
