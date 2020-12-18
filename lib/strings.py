__project_name__ = 'SynCover'


class Console:
    program_start = 'Program {project_name} started.'.format(project_name=__project_name__)
    reloading_config = 'Reloading config.'
    start_converting = 'Converting of <{file}> started..'
    wait_files = 'Waiting for incoming files..'


class Report:
    mail_subject = '{project_name}: Error report'.format(project_name=__project_name__)
