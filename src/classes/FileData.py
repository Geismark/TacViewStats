"""Module DocString"""  # TODO add module docstrings

from src.classes.DCSObject import DCSObject
from src.data.typeReferences import valid_DCSObject_states
from src.managers.logHandler import logger


class FileData:
    def __init__(self):
        self.is_zip = None  # is the file a .zip?
        self.file_name = None  # what is the name of the file itself
        self.file_type = None  # ACMI file type recorded by TacView
        self.file_version = None  # ACMI version recorded by TacView
        self.file_length = None  # Number of lines in the file
        self.file_size = None  # size of the file in KB
        self.recorder = (
            None  # what application and version was used to record the data?
        )
        self.source = None  # what application and version was the data collected from?
        self.mission_title = None  # title of the mission file loaded on the DCS server
        self.author = None  # client's in-game name
        self.server = (
            None  # Not Implemented: will predict which server the data came from
        )
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
        self.objects = {}  # id:obj all objects currently alive within the file
        self.dying_objects = (
            {}
        )  # id:obj all objects currently currently in death processing
        self.dead_objects = {}  # uid:obj all objects that have died
        self.all_objects = {}  # uid:obj all objects in file (all states)
        self.first_time_stamp = None
        self.time_stamp = (
            0  # the most recent timestamp processed whilst reading the file
        )
        self.final_time_stamp = None
        # self.server_events = []
        self.category = None  # unsure what this is, needs testing/researching
        self.uid_counter = 0

    def set_time(self, time: float):
        """Updates current time stamp to input.\n\nCannot input an earlier timestamp than what is currently set."""
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
        """Returns a new DCSObject with given id and state; sets obj.uid from internal FileData UID counter.\n\nObject also placed in correct dictionary"""
        if not isinstance(id, str):
            raise TypeError("id is not a string")
        if id in self.objects:
            raise ValueError("Object already exists in alive object dictionary")
        new_object = DCSObject(self, id, self.uid_counter, state=init_state)
        self.objects[id] = new_object
        self.uid_counter += 1
        self.all_objects[new_object.uid] = new_object.id
        return new_object

    def get_coord_reference(self):
        """Returns lat/long references. Raises ValueError/TypeError if not set."""
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

    def get_obj_by_id(self, id, *states):
        """Returns the most recently initialized object with given id.\n\n
        NOTE: not ideally suitable for use with dead objects."""
        if states == ():
            states = valid_DCSObject_states
        if "Alive" in states and id in self.objects:
            return self.objects[id]
        elif "Dying" in states and id in self.dying_objects:
            return self.dying_objects[id]
        elif "Dead" in states:
            dead_with_id = [obj for obj in self.dead_objects.values() if obj.id == id]
            if dead_with_id != []:
                return dead_with_id[-1]
        else:
            return None

    def get_obj_by_uid(self, uid):
        """Returns DCSObject with the given UID (regardless of state)"""
        if uid in self.all_objects:
            return self.all_objects[uid]
        else:
            raise ValueError(f"Object not found: {uid=}")

    def get_all_by_ids(self, ids: list[str], states_to_search: list = None):
        """Returns all objects with given id(s), ordered from most recent to oldest by init time stamp."""
        if states_to_search is None:
            states_to_search = valid_DCSObject_states
        elif isinstance(ids, str):
            ids = [ids]

        get_alive, get_dead, get_dying = False, False, False
        if "Alive" in states_to_search:
            get_alive = True
        if "Dying" in states_to_search:
            get_dying = True
        if "Dead" in states_to_search:
            get_dead = True
        all_objs = self.get_all_objs(alive=get_alive, dying=get_dying, dead=get_dead)

        unordered_obj_list = []
        for id in ids:
            unordered_obj_list += [obj for obj in all_objs if obj.id == id]

        ordered_obj_list = sorted(
            unordered_obj_list, key=lambda obj: obj.spawn_time_stamp
        )
        return ordered_obj_list

    def get_all_objs(self, alive=True, dying=True, dead=True):
        """Returns list of all objects in file"""
        all_obj_list = []
        if alive:
            all_obj_list += list(self.objects.values())
        if dying:
            all_obj_list += list(self.dying_objects.values())
        if dead:
            all_obj_list += list(self.dead_objects.values())
        return all_obj_list

    def check_is_FileData(self):
        """Returns True if file is a FileData object, False otherwise"""
        # useful as cannot import FileData in some files (e.g.: if they import DCSObject)
        if isinstance(self, FileData):
            return True
        else:
            return False

    def info(
        self,
        metadata=True,
        context=False,
        time=False,
        objects=False,
        coords=False,
        extras=False,
        all=False,
    ):
        """Returns a string containing all FileData attributes and their values"""
        if all:
            metadata, time, objects, coords, extras = True, True, True, True, True
        m, cx, t, o, cd, e = "", "", "", "", "", ""
        if metadata:
            m += f"Name: {self.file_name}\n\t"
            m += f"Type: {self.file_type}\n\t"
            m += f"Version: {self.file_version}\n\t"
            m += f"Length: {self.file_length}\n\t"
            m += f"Size: {self.file_size}\n\t"
            m += f"Recorder: {self.recorder}\n\t"
            m += f"Source: {self.source}\n\t"
        if context:
            cx += f"Mission Title: {self.mission_title}\n\t"
            cx += f"Author: {self.author}\n\t"
            cx += f"Server: {self.server}\n\t"
            cx += f"Comments: {self.comments}\n\t"
            cx += f"Briefing: {self.briefing}\n\t"
            cx += f"Debriefing: {self.debriefing}\n\t"
        if time:
            t += f"Mission Date: {self.mission_date}\n\t"
            t += f"Mission Start Time: {self.mission_start_time}\n\t"
            t += f"Record Date: {self.record_date}\n\t"
            t += f"Record Start Time: {self.record_start_time}\n\t"
            t += f"First Time Stamp: {self.first_time_stamp}\n\t"
            t += f"Time Stamp: {self.time_stamp}\n\t"
            t += f"Final Time Stamp: {self.final_time_stamp}\n\t"
        if coords:
            cd += f"Longitude Reference: {self.longitude_reference}\n\t"
            cd += f"Latitude Reference: {self.latitude_reference}\n\t"
        if objects:
            o += f"All Objects: {len(self.all_objects)}\n\t"
            o += f"Alive Objects ({len(self.objects.keys())}): {list(self.objects.keys())}\n\t"
            o += f"Dying Objects ({len(self.dying_objects.keys())}): {list(self.dying_objects.keys())}\n\t"
            o += f"Dead Objects ({len(self.dead_objects.keys())}): {[obj.id for obj in self.dead_objects.values()]}\n\t"
        if extras:
            e += f"Category: {self.category}\n\t"
            e += f"UID Counter: {self.uid_counter} "

        info = "\n\t" + "".join([m, cx, t, o, cd, e])
        return info
