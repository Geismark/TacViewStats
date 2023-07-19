from src.managers.logHandler import logger
from src.utils.mathUtils import str_is_float
from src.data.coordReferences import death_coords
from src.data.typeReferences import (
    skip_dying_types,
    skip_data_processing_types,
    all_known_types,
    valid_DCSObject_states,
)


class DCSObject:
    def __init__(self, file_obj, id: str, uid: int, state: str = "Alive"):
        if not isinstance(id, str):
            raise TypeError(f"DCSObject init id is not string: {id=} {type(id)=}")
        if not isinstance(state, str):
            raise TypeError(
                f"DCSObject init state is not string: {state=} {type(state)=}"
            )
        if state not in valid_DCSObject_states:
            raise ValueError(
                f"DCSObject init state is not Alive, Dying, or Dead: {state=}"
            )
        if not file_obj.check_is_FileData():
            # cannot directly import FileData as it would become a circular import
            raise TypeError(
                f"DCSObject init file_obj is not FileData: {type(file_obj)}\n\t{file_obj=}"
            )
        self.file_obj = (
            file_obj  # FileData object of the TacView file this object belongs to
        )
        self.id = str(id)  # the ID of this object (same as the one used in the TV file)
        if uid != file_obj.uid_counter:
            raise ValueError(
                f"DCSObject init uid is not equal to file_obj.uid_counter: {uid=} {file_obj.uid_counter=}"
            )
        self.uid = uid  # the unique ID of this object (from counter within file_obj)
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

    def update_transform(self, lat: str, long: str, alt: str):
        """Updates this object's coordinates and altitude (str floats) based on the latest coordinate update from the TacView file."""
        num_check = [lat, long, alt]
        check_list = [
            c for c in num_check if c != ""
        ]  # often only a single unit is updated
        for value in check_list:
            if not str_is_float(value):
                raise TypeError(f"transform is not numeric: {lat=} {long=} {alt=}")
        self.lat_old, self.long_old, self.alt_old = self.lat, self.long, self.alt
        # do this manually to prevent issues with get_pos with reused ids
        if lat != "":
            self.lat = float(lat)
        if long != "":
            self.long = float(long)
        if alt != "":
            self.alt = float(alt)

    def get_pos(self, _ignore_state=False):
        """Get relative position of this object as provided by the file (exclude lat/long reference)."""
        if not self.check_is_alive() and not _ignore_state:
            raise ValueError(
                f"Trying to get position of {self.state} object: {self.id=} {self.name=} {self.type=}"
            )
        return [self.lat, self.long, self.alt]

    def get_real_pos(self):
        """Get absolute position of this object as provided by the file (include lat/long reference)."""
        if not self.check_is_alive():
            raise ValueError(
                f"Trying to get real position of {self.state} object: {self.id=} {self.name=} {self.type=}"
            )
        lat_ref, long_ref = self.file_obj.get_coord_reference()
        return [self.lat + float(lat_ref), self.long + float(long_ref), self.alt]

    def get_prev_pos(self):
        """Return coordinates of this object at its previous coordinate update."""
        return [self.lat_old, self.long_old, self.alt_old]

    def get_death_pos(self):
        """Get relative position of this object at death as provided by the file (exclude lat/long reference)."""
        return self.death_position

    def get_real_death_pos(self):
        """Get absolute position of this object at death as provided by the file (include lat/long reference)."""
        lat_ref, long_ref = self.file_obj.get_coord_reference()
        d_lat, d_long, d_alt = self.get_death_pos()
        return [d_lat + float(lat_ref), d_long + float(long_ref), d_alt]

    def add_launch(self, munition_obj):
        """Adds munition to self.launches{id:obj}.\n
        Adds launcher to munition.launcher"""
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
        self.check_in_same_file(munition_obj)
        munition_obj.launcher = self
        self.launches[munition_obj.id] = munition_obj

    def add_kill(self, victim, dist=None):
        """Adds self and self.launcher to relevant victim attributes.\n
        Checks both victim and self are dying.\n
        Updates both victim and self to dead."""
        if not isinstance(victim, DCSObject):
            raise TypeError(f"Victim is not DCSObject:\n\t{victim=}")
        if not self.check_is_dying():
            raise AttributeError(
                f"Munition (self) is not in dying objects:\n\t\t{self.id=} {self.type=} {self.name=} {self.state=}\n\t\t{victim.id=} {victim.type=} {victim.name=} {victim.state=}\n\t{self.file_obj.objects.keys()}\n\t{self.file_obj.dying_objects.keys()=}\n\t{self.file_obj.dead_objects.keys()=}"
            )
        if not victim.check_is_dying():
            raise AttributeError(
                f"Victim is not in dying objects:\n\t\t{self.id=} {self.type=} {self.name=} {self.state=}\n\t\t{victim.id=} {victim.type=} {victim.name=} {victim.state=}\n\t{self.file_obj.objects.keys()}\n\t{self.file_obj.dying_objects.keys()=}\n\t{self.file_obj.dead_objects.keys()=}"
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
        logger.trace(
            f"Added kill: {dist=} {self.file_obj.file_name}\n\t{self.id=} {self.name=} {self.type=} {self.state=} {self.pilot=}\n\t{victim.id=} {victim.name=} {victim.type=} {victim.state=} {self.pilot=}\n\t{f'{self.launcher.id=} {self.launcher.name=} {self.launcher.type=} {self.launcher.pilot=}' if self.launcher else ''}"
        )

    def update_to_dying(self):
        """Update self to dying state (includes moving to appropriate dictionary)."""
        # validate state and found in correct object dictionary
        if not self.check_is_alive():
            raise ValueError(
                f"New dying object does not have correct state/not in correct object dictionary:\n\t{self.id=} {self.state=}"
            )
        # check for appropriate death position value
        if self.death_position != None:
            raise ValueError(
                f"New dying object already has death position: {self.id=} {self.death_position=} {self.death_time_stamp=}"
            )

        # set death position
        self.set_death_coords()

        self.file_obj.objects.pop(self.id)
        self.state = "Dying"
        self.file_obj.dying_objects[self.id] = self
        self.death_time_stamp = self.file_obj.time_stamp

    def update_to_dead(self):
        """Update self to dead state (includes moving to appropriate dictionary)."""
        # ensure id or obj not already found in dead_objects
        if self in self.file_obj.dead_objects.values():
            raise ValueError(
                f"New dead object is already in dead_objects: {self.id=} {self.state=} {self.type=}\n\t{self.file_obj.dead_objects.keys()=}"
            )
        # validate state and found in correct object dictionary
        if not (self.check_is_alive() or self.check_is_dying()):
            raise ValueError(
                f"New dead object is not in appropriate object dictionary: {self.id=} {self.state=}"
                + f"\n\tIn objects: {True if self.id in self.file_obj.objects else False}"
                + f"\n\tIn dying_objects: {True if self.id in self.file_obj.dying_objects else False}"
                + f"\n\tIn dead_objects: {True if self.id in self.file_obj.dead_objects else False}"
            )
        # check death position value and time stamp value is /not/ set
        if self.check_is_alive():
            if self.death_position != None or self.death_time_stamp != None:
                raise ValueError(
                    f"Old alive/new dead object already has death position: {self.id=} {self.death_time_stamp=} {self.death_position=}"
                )
            self.set_death_coords()
            self.file_obj.objects.pop(self.id)
        elif self.check_is_dying():
            if self.death_position == None or self.death_time_stamp == None:
                raise ValueError(
                    f"Old dying/new dead object has no death position: {self.id=} {self.death_time_stamp=}"
                )
            self.file_obj.dying_objects.pop(self.id)
        else:
            raise ValueError(f"Object is not alive or dying: {self.id=} {self.state=}")
        # update to correct object dictionary
        self.file_obj.dead_objects[self.id] = self
        # update to correct state
        self.state = "Dead"

    def set_death_coords(self):
        """Set death position and update 'current' position to death_coords"""
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

    def check_is_alive(self):
        if self.state == "Alive":
            if self.id not in self.file_obj.objects:
                raise ValueError(
                    f"Object is alive but not in objects dictionary: {self.info(all=True)}"
                )
            return True
        return False

    def check_is_dying(self):
        if self.state == "Dying":
            if self.id not in self.file_obj.dying_objects:
                raise ValueError(
                    f"Object is dying but not in dying_objects dictionary: {self.info(all=True)}"
                )
            return True
        return False

    def check_is_dead(self):
        if self.state == "Dead":
            if self.id not in self.file_obj.dead_objects:
                raise ValueError(
                    f"Object is dead but not in dead_objects dictionary: {self.info(all=True)}"
                )
            return True
        return False

    def check_skip_dying_type(self):
        """Returns True if an object type is within skip_dying_type list."""
        for skip_type in skip_dying_types:
            if skip_type in self.type:
                # if self.state == "Alive":
                #     self.update_to_dead()
                # FUTUREDO later may wish to change this to allow detecting missiles being trashed by decoys
                return True
        return False

    def check_skip_data_processing_type(self):
        """Returns True if an object type is within skip_data_processing_type list."""
        for skip_type in skip_data_processing_types:
            if skip_type in self.type:
                return True
        return False

    def check_in_same_file(self, other):
        """Raises TypeError if objects are from different files"""
        if not isinstance(self, DCSObject) or not isinstance(other, DCSObject):
            raise TypeError(
                f"Trying to check same_file on non-DCSObject: {type(self)=} {type(other)=}"
            )
        if self.file_obj != other.file_obj:
            raise ValueError(
                f"Objects from different files!\n\t{self.id=} - {self.file_obj.file_name}\n\t{other.id=} - {other.file_obj.file_name}"
            )

    def set_types(self, types: str):
        """Set object types. Pass in type string as found in .acmi"""
        type_list = types.split("+")
        for type in type_list:
            if type not in all_known_types:
                logger.critical(f"Unknown type: {type=}")
        self.type = type_list

    def info(
        self,
        basic=True,
        combat=False,
        position=False,
        times=False,
        side=False,
        all=False,
    ):
        """Returns string with object information."""
        if all:
            basic, combat, position, times, side = True, True, True, True, True
        b, c, p, t, s = "", "", "", "", ""
        if basic:
            b = f"ID: {self.id} "
            b += f"UID: {self.uid} "
            b += f"Type: {self.type} "
            b += f"Name: {self.name} "
            b += f"State: {self.state} "
            b += f"Pilot: {self.pilot} "
        if combat:
            c = f"Launches: {[launch.id for launch in self.launches.values()] if self.launches else None} "
            c += f"Launcher: {self.launcher.id if self.launcher else None} "
            c += f"Kills: {[[kill.id, kill.type, kill.name] for kill in self.kills.values()] if self.kills else None} "
            c += f"Killer: {[self.killer.id, self.killer.type, self.killer.name] if self.killer else None} "
            c += f"Killer Weapon: {self.killer_weapon.name if self.killer_weapon else None} "
        if position:
            p = f"Position: {self.get_pos(_ignore_state=True)} "
            p += f"Previous: {self.get_prev_pos()} "
            p += f"Origin: {self.origin} "
            p += f"Death: {self.get_death_pos()} "
            p += f"LatLong Ref: {self.file_obj.get_coord_reference()} "
        if times:
            t += f"Time Stamp: {self.file_obj.time_stamp} "
            t += f"Spawn: {self.spawn_time_stamp} "
            t += f"Death: {self.death_time_stamp} "
        if side:
            s = f"Coalition: {self.coalition} "
            s += f"Country: {self.country}"

        temp = [element for element in [b, c, p, t, s] if element]
        info = "\n".join(temp)
        return info
