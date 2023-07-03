import configparser


class Section:
    pass


class Config:
    def __init__(self):
        config = configparser.RawConfigParser()
        config.read("config.ini")
        for section in config:
            current_section = Section()
            setattr(self, section, current_section)
            for key, value in config[section].items():
                if value.capitalize() in ["True"]:
                    setattr(current_section, key, True)
                elif value.capitalize() in ["False"]:
                    setattr(current_section, key, False)
                elif value.isdigit():
                    setattr(current_section, key, int(value))
                else:
                    setattr(current_section, key, value)
        # TODO need to choose file to write to - needs to be the same for all processes
        # have each log start with id/counter for files -> keeps track of both processor and file


config = Config()

# FUTUREDO going to introduce multiprocessing later -> need to ensure object is initialised only once
