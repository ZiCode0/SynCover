from json import dumps, load


class JsonConfig:
    def __init__(self, file_path: str):
        """
        Json input arguments parser
        :param file_path: input file path to input file
        """
        self.param = {}
        self.param = {**self.param, **load(open(file_path, "r"))['config']}

        self.stations = self.param['station_list']
        self.channels_list = [y for x in
                              [[*self.stations[i].keys()] for i in [*self.stations.keys()]]
                              for y in x]
        # print()

    def print_config(self):
        """
        Print input arguments
        """
        out_dump = dumps(self.param,
                         indent=4,
                         sort_keys=True)
        out_dump = out_dump.replace(',', '')
        out_dump = out_dump.replace('{', '').replace('}', '')
        out_dump = out_dump.replace('[', '').replace(']', '')
        print(f'Config loaded:\n{out_dump}')


if __name__ == '__main__':
    conf = JsonConfig('./../config.json')
    conf.print_config()
