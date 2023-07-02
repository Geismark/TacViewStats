from src.utils.mathUtils import str_is_float


class DCSObject:
    def __init__(self, file_obj, id: str):
        if not isinstance(id, str):
            raise TypeError(f"DCSObject init id is not string: {id=} {type(id)=}")
        self.file_obj = (
            file_obj  # FileData object of the TacView file this object belongs to
        )
        self.id = str(id)  # the ID of this object (same as the one used in the TV file)
        self.lat = (
            None  # the most recent latitude of this object (doesn't include reference)
        )
        self.long = (
            None  # the most recent latitude of this object (doesn't include reference)
        )
        self.alt = 0  # the most recent altitude in meters MSL // some naval units are never updated -> 0 is default
        self.lat_old = (
            None  # the latitude value at the previous coordinate update of this object
        )
        self.long_old = (
            None  # the longitude value at the previous coordinate update of this object
        )
        self.alt_old = (
            None  # the altitude value at the previous coordinate update of this object
        )
        self.type = (
            None  # the assigned type(s) of this object (e.g.: fixed-wing / projectile)
        )
        # self.U = None # native x (2D world - unsure if used in DCS TV)
        # self.V = None # native y (2D world - unsure if used in DCS TV)
        self.coalition = None  # coalition this object was assigned to
        self.name = None  # name of this object (i.e.: the name set in the mission editor for objects)
        self.pilot = None  # the name of the pilot (what about AI, WSO, and RIOs?)
        self.group = None  # the name of the group the object was assigned to in the mission editor
        # self.group_members = [] # the other members of the group this object was assigned
        self.color = (
            None  # colour used in TacView (using American spelling for consistency)
        )
        self.country = None
        self.state = None  # None, Alive, Killed, Dead, Dying (checking for any weapons)
        self.launches = []  # id of all munitions launched by this object
        self.kills = []  # [weapon, victim]
        self.killer = None  # which 'launcher' this object was killed by
        self.killer_weapon = None  # the munition this object was killed by
        self.landed = None  # boolean
        # self.obj_events = []
        # self.carrier = None  # boolean
        self.player = None  # boolean
        # self.difficulty = (
        #     None  # FUTUREDO will need to get information on a server basis
        # )
        self.spawn_time_stamp = (
            file_obj.time_stamp
        )  # uses acmi time stamp, not recording/mission time
        self.death_time_stamp = None  # uses acmi time stamp, not recording/mission time
        self.death_position = None
        self.origin = []  # lat, long, alt at spawn
        self.launcher = None  # only for munitions

    def update_transform(self, lat, long, alt):
        num_check = [lat, long, alt]
        check_list = [
            c for c in num_check if c != ""
        ]  # often only a single unit is updated
        for value in check_list:
            if not str_is_float(value):
                raise TypeError(f"transform is not numeric: {lat=} {long=} {alt=}")
        self.lat_old, self.long_old, self.alt_old = self.get_pos()
        if lat != "":
            self.lat = float(lat)
        if long != "":
            self.long = float(long)
        if alt != "":
            self.alt = float(alt)

    def get_pos(self):
        return [self.lat, self.long, self.alt]

    def get_real_pos(self):
        lat_ref, long_ref = self.file_obj.get_coord_reference()
        return [self.lat + float(lat_ref), self.long + float(long_ref), self.alt]

    def add_launch(self, munition_obj):
        if not isinstance(munition_obj, DCSObject):
            raise TypeError(f"Munition is not DCSObject:\n\t{munition_obj=}")
        if munition_obj in self.launches:
            raise ValueError(
                f"Munition is already added to launches: {munition_obj.id=}\n\t{self.id=} {self.launches=}"
            )
        if munition_obj.launcher != None:
            raise ValueError(
                f"Munition already has attributed launcher\n\t{munition_obj.id=} {self.id=}\n\t{munition_obj.launcher.id=}"
            )
        if munition_obj.file_obj != self.file_obj:
            raise ValueError(
                f"Objects from different files!\n\t{self.id=} - {self.file_obj.file_name}\n\t{munition_obj.id=} - {munition_obj.file_obj.file_name}"
            )
        munition_obj.launcher = self
        self.launches.append(munition_obj)

    def die(self):
        self.update_transform(100, 100, -1)
        self.state = "Dying"
        self.death_time_stamp = self.file_obj.time_stamp
