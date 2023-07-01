class Config:
    def __init__(self, config_file="config.ini"):
        import configparser

        self.config = configparser.RawConfigParser()
        self.config.read(config_file)

        class Section:
            def add(self, key, value):
                setattr(self, key, value)

        for section in self.config.sections():
            temp_section = Section()
            for key in self.config[section]:
                # convert to bool if possible
                if self.config[section][key].capitalize() in ["True", "False"]:
                    temp_section.add(
                        key, self.config[section][key].capitalize() == "True"
                    )

                # convert to int if possible
                elif self.config[section][key].isdigit():
                    temp_section.add(key, int(self.config[section][key]))

                else:
                    temp_section.add(key, self.config[section][key])

            setattr(self, section, temp_section)


config = Config("config.ini")
