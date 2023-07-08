from src.utils.mathUtils import str_is_float
from src.managers.logHandler import logger
from src.data.coordReferences import death_coords
from src.data.typeReferences import skip_dying_types


class DCSObject:
    def __init__(self, file_obj, id: str, state: str = "Alive"):
        if not isinstance(id, str):
            raise TypeError(f"DCSObject init id is not string: {id=} {type(id)=}")
        if not isinstance(state, str):
            raise TypeError(
                f"DCSObject init state is not string: {state=} {type(state)=}"
            )
        if state not in ["Alive", "Dying", "Dead"]:
            raise ValueError(
                f"DCSObject init state is not Alive, Dying, or Dead: {state=}"
            )
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
        self.state = state  # None, Alive, Dying (checking for any kill/ers), Dead
        self.launches = {}  # {id:obj} of all munitions launched by this object
        self.kills = {}  # {weapon:victim}
        self.killer = None  # which 'launcher' this object was killed by (/collision)
        self.killer_weapon = None  # the munition this object was killed by
        # self.landed = None  # boolean
        # self.obj_events = []
        # self.carrier = None  # boolean
        # self.player = None  # boolean
        # self.cold_start = None # is there a way to determine this (e.g.: at init -> planes in the air already)
        # self.prior_spawn = None
        # self.difficulty = (
        #     None  # FUTUREDO will need to get information on a server basis
        # )
        self.spawn_time_stamp = (
            file_obj.time_stamp  # FUTUREDO not ideal for testing as requires FileData
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

    def get_death_pos(self):
        return self.death_position

    def get_real_death_pos(self):
        lat_ref, long_ref = self.file_obj.get_coord_reference()
        d_lat, d_long, d_alt = self.get_death_pos()
        return [d_lat + float(lat_ref), d_long + float(long_ref), d_alt]

    def add_launch(self, munition_obj):
        if not isinstance(munition_obj, DCSObject):
            raise TypeError(f"Munition is not DCSObject:\n\t{munition_obj=}")
        if munition_obj.id in self.launches:
            raise ValueError(
                f"Munition is already added to launches: {munition_obj.id=}\n\t{self.id=} {self.launches.keys()=}"
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
        self.launches[munition_obj.id] = munition_obj

    def add_kill(self, victim):
        """Adds self and self.launcher to relevant victim attributes.\n
        Checks both victim and self are dying.\n
        Updates both victim and self to dead."""
        if not isinstance(victim, DCSObject):
            raise TypeError(f"Victim is not DCSObject:\n\t{victim=}")
        if victim not in self.file_obj.dying_objects.values():
            raise AttributeError(
                f"Victim is not in dying objects:\n\t\t{self.id=} {self.type=} {self.name=} {self.state=}\n\t\t{victim.id=} {victim.type=} {victim.name=} {victim.state=}\n\t{self.file_obj.objects.keys()}\n\t{self.file_obj.dying_objects.keys()=}\n\t{self.file_obj.dead_objects.keys()=}"
            )
        elif self not in self.file_obj.dying_objects.values():
            raise AttributeError(
                f"Munition is not in dying objects:\n\t\t{self.id=} {self.type=} {self.name=} {self.state=}\n\t\t{victim.id=} {victim.type=} {victim.name=} {victim.state=}\n\t{self.file_obj.objects.keys()}\n\t{self.file_obj.dying_objects.keys()=}\n\t{self.file_obj.dead_objects.keys()=}"
            )
        if victim.killer != None or victim.killer_weapon != None:
            raise AttributeError(
                f"Victim already has killer/weapon: {self.id=} {victim.id=} {victim.killer=} {victim.killer_weapon=}"
            )
        if self.launcher != None:
            if self not in self.launcher.launches.values():
                raise AttributeError(
                    f"Munition is not in munition launcher: {self.id=} {self.launcher.id=} {self.launcher.launches.keys()=}"
                )
            self.launcher.kills[self] = victim
            victim.killer = self.launcher
        victim.killer_weapon = self
        self.kills[self] = victim
        self.update_to_dead()
        victim.update_to_dead()

    def update_to_dying(self):
        # validate state and found in correct object dictionary
        if self.state != "Alive":
            raise ValueError(f"New dying object is not alive: {self.id=} {self.state=}")
        if self.id not in self.file_obj.objects:
            raise ValueError(
                f"New dying object is not in objects: {self.id=} {self.state=}"
            )
        # check for appropriate death position value
        if self.death_position != None:
            raise ValueError(
                f"New dying object already has death position: {self.id=} {self.death_position=} {self.death_time_stamp=}"
            )

        # set death position
        self.set_death_coords()

        self.file_obj.objects.pop(self.id)
        self.file_obj.dying_objects[self.id] = self
        self.state = "Dying"
        self.death_time_stamp = self.file_obj.time_stamp

    def update_to_dead(self):
        # FUTUREDO may want to always go through dying first?
        # validate state and found in correct object dictionary
        if self.state not in ["Alive", "Dying"]:
            raise ValueError(
                f"New dead object is not alive/dying: {self.id=} {self.state=}"
            )
        elif not (
            (self.state == "Alive" and self.id in self.file_obj.objects)
            or (self.state == "Dying" and self.id in self.file_obj.dying_objects)
        ):
            raise ValueError(
                f"New dead object is not in appropriate object dictionary: {self.id=}"
                + f"\n\tIn objects: {True if self.id in self.file_obj.objects else False}"
                + f"\n\tIn dying_objects: {True if self.id in self.file_obj.dying_objects else False}"
            )
        elif self.id in self.file_obj.dead_objects:
            raise ValueError(
                f"New dead object is already in dead_objects: {self.id=} {self.state=} {self.type=}\n\t{self.file_obj.dead_objects.keys()=}"
            )
        # check death position value and time stamp value is /not/ set
        if self.state == "Dying" and (
            self.death_position == None or self.death_time_stamp == None
        ):
            raise ValueError(
                f"Old dying/new dead object has no death position: {self.id=} {self.death_time_stamp=}"
            )
        elif self.state == "Alive" and (
            self.death_position != None or self.death_time_stamp != None
        ):
            raise ValueError(
                f"Old alive/new dead object already has death position: {self.id=} {self.death_time_stamp=} {self.death_position=}"
            )

        # set death position if required:
        if self.death_position == None:
            self.set_death_coords()
        # update to correct object dictionary
        if self.state == "Alive":
            self.file_obj.objects.pop(self.id)
        if self.state == "Dying":
            self.file_obj.dying_objects.pop(self.id)
        self.file_obj.dead_objects[self.id] = self
        # update to correct state
        self.state = "Dead"

    def set_death_coords(self):
        if self.death_position != None:
            raise ValueError(
                f"Death coords already set: {self.id=} {self.death_position=} {self.death_time_stamp=}"
            )
        self.death_position = self.get_pos()
        self.update_transform(death_coords[0], death_coords[1], death_coords[2])

    def set_death_time_stamp(self):
        if self.death_time_stamp != None:
            raise ValueError(
                f"Death time stamp already set: {self.id=} {self.death_position=} {self.death_time_stamp=}"
            )
        self.death_time_stamp = self.file_obj.time_stamp

    def check_state(self, *states_to_check):
        """Checks if object state is one of the provided states"""
        valid_states = ["Alive", "Dying", "Dead"]
        if len(states_to_check) == 0:
            states_to_check = valid_states
        else:
            for state in states_to_check:
                if state not in valid_states:
                    raise ValueError(
                        f"State to check is not Alive/Dying/Dead: {state=} {states_to_check=}"
                    )
        if self.state in states_to_check:
            if self.check_is_state(self.state):
                return True
        return False

    def check_is_state(self, state: str):
        """Use object.check_state(*states_to_check) instead of this"""
        if state not in ["Alive", "Dying", "Dead"]:
            raise ValueError(f"State to check is not Alive/Dying/Dead: {state=}")
        if state == "Alive":
            if (
                (self.state != "Alive")
                or (self.id not in self.file_obj.objects)
                or (self.id in self.file_obj.dying_objects)
                or (self.id in self.file_obj.dead_objects)
            ):
                raise TypeError(
                    f"State is not Alive: {self.id=} {self.state=} {self.type=} {self.name=}\n\t{self.file_obj.objects.keys()=}\n\t{self.file_obj.dying_objects.keys()=}\n\t{self.file_obj.dead_objects.keys()=}"
                )
        elif state == "Dying":
            if (
                (self.state != "Dying")
                or (self.id in self.file_obj.objects)
                or (self.id not in self.file_obj.dying_objects)
                or (self.id in self.file_obj.dead_objects)
            ):
                raise TypeError(
                    f"State is not Dying: {self.id=} {self.state=} {self.type=} {self.name=}\n\t{self.file_obj.objects.keys()=}\n\t{self.file_obj.dying_objects.keys()=}\n\t{self.file_obj.dead_objects.keys()=}"
                )
        elif state == "Dead":
            if (
                (self.state != "Dead")
                or (self.id in self.file_obj.objects)
                or (self.id in self.file_obj.dying_objects)
                or (self.id not in self.file_obj.dead_objects)
            ):
                raise TypeError(
                    f"State is not Dead: {self.id=} {self.state=} {self.type=} {self.name=}\n\t{self.file_obj.objects.keys()=}\n\t{self.file_obj.dying_objects.keys()=}\n\t{self.file_obj.dead_objects.keys()=}"
                )
        return True

    def check_skip_dying_type(self):
        for skip_type in skip_dying_types:
            if skip_type in self.type:
                if self.state == "Alive":
                    self.update_to_dead()
                    # FUTUREDO later may wish to change this to allow detecting missiles being trashed by decoys
                return True
        return False
