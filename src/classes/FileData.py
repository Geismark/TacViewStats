from src.classes.DCSObject import DCSObject


class FileData:
    def __init__(self):
        self.is_zip = None
        self.file_name = None
        self.file_type = None
        self.file_version = None
        self.recorder = None
        self.source = None
        self.mission_title = None
        self.author = None  # client's in-game name
        self.server = None
        self.comments = (
            []
        )  # appears this is used for the briefing, yet to see 0,Briefing
        self.briefing = None  # may be used when changing slots?? *UNSURE*
        self.debriefing = None  # expect None
        self.mission_date = None  # TODO
        self.mission_start_time = None  # TODO
        self.record_date = None  # TODO
        self.record_start_time = None  # TODO
        self.longitude_reference = None
        self.latitude_reference = None
        self.objects = {}
        self.first_time_stamp = None
        self.time_stamp = 0
        self.server_events = []
        self.category = None  # unsure what this is, needs testing

    def __str__(self):
        return self.file_name

    def set_time(self, time: float):
        self.time_stamp = float(time)
        if (
            self.first_time_stamp == None
        ):  # can't test False, as first time stamp may be 0.0 (although highly unlikely)
            self.first_time_stamp = self.time_stamp

    def new_obj(self, id: str):
        new_object = DCSObject(self, id)
        self.objects[id] = new_object
        return new_object

    def get_coord_reference(self):
        return [self.latitude_reference, self.longitude_reference]

    def remove_obj(self, obj):
        obj.die()
