"""Module DocString"""  # TODO add module docstrings

from src.classes.DCSObject import DCSObject


class FileData:
    def __init__(self):
        self.is_zip = None  # is the file a .zip?
        self.file_name = None  # what is the name of the file itself
        self.file_type = None  # ACMI file type recorded by TacView
        self.file_version = None  # ACMI version recorded by TacView
        self.recorder = (
            None  # what application and version was used to record the data?
        )
        self.source = None  # what application and version was the data collected from?
        self.mission_title = None  # title of the mission file loaded on the DCS server
        self.author = None  # client's in-game name
        self.server = None
        self.comments = (
            []
        )  # appears this is used for the briefing, yet to see 0,Briefing
        self.briefing = None  # may be used when changing slots?? *UNSURE*
        self.debriefing = None  # expect None?
        self.mission_date = None
        self.mission_start_time = None  # TODO separate/parse mission date and time
        self.record_date = None
        self.record_start_time = None  # TODO separate/parse record date and time
        self.longitude_reference = (
            None  # the base longitude that all recorded data is added to
        )
        self.latitude_reference = (
            None  # the base latitude that all recorded data is added to
        )
        self.objects = {}  # all objects currently alive within the file
        self.dying_objects = {}  # all objects currently currently in death processing
        self.dead_objects = {}  # all objects that have died
        self.first_time_stamp = None
        self.time_stamp = (
            0  # the most recent timestamp processed whilst reading the file
        )
        self.final_time_stamp = None
        # self.server_events = []
        self.category = None  # unsure what this is, needs testing/researching

    def __str__(self):
        return self.file_name

    def set_time(self, time: float):
        if not isinstance(time, float) and not isinstance(time, int):
            raise TypeError(f"Time is not a float(/int): {time=}")
        if time < self.time_stamp:
            raise ValueError(
                f"Provided time is earlier than set time:\n\t{time=}\n\t{self.time_stamp=}\n\t{self.first_time_stamp=}"
            )
        self.time_stamp = float(time)
        if self.first_time_stamp == None:
            # can't test False, as first time stamp may be 0.0 (although highly unlikely)
            self.first_time_stamp = self.time_stamp

    def new_obj(self, id: str, init_state="Alive"):
        if not isinstance(id, str):
            raise TypeError("id is not a string")
        if id in self.objects:
            raise ValueError("Object already exists")
        new_object = DCSObject(self, id, state=init_state)
        self.objects[id] = new_object
        return new_object

    def get_coord_reference(self):
        if self.latitude_reference == None or self.longitude_reference == None:
            if self.latitude_reference == self.longitude_reference == None:
                raise ValueError(
                    f"Lat/Long references not set\n\tLat: {self.latitude_reference}\n\tLong: {self.longitude_reference}"
                )
            else:
                raise TypeError(
                    f"Lat/Long partially set - {self.file_name=}\n\tLat: {self.latitude_reference}\n\tLong: {self.longitude_reference}"
                )
        return [self.latitude_reference, self.longitude_reference]

    def remove_obj(self, obj):
        obj.die()

    def get_obj_by_id(self, id):
        if id in self.objects:
            return self.objects[id]
        elif id in self.dying_objects:
            return self.dying_objects[id]
        elif id in self.dead_objects:
            return self.dead_objects[id]
        else:
            return False
