from src.managers.logHandler import logger
from src.utils.fileUtils import (
    FileData,
    attr_split,
    get_launcher,
)
from src.data.acmiAttrDicts import (
    acmi_old_obj_to_attr,
    acmi_new_obj_to_attr,
    acmi_obj_to_attr_all,
    acmi_global_to_attr,
)
from src.managers.dataProcessor import process_file_tick

# https://www.tacview.net/documentation/acmi/en/
# T = Longitude | Latitude | Altitude
# T = Longitude | Latitude | Altitude | U | V
# T = Longitude | Latitude | Altitude | Roll | Pitch | Yaw
# T = Longitude | Latitude | Altitude | Roll | Pitch | Yaw | U | V | Heading


def global_line(line: list, file_data: FileData):
    for attr_pointer, attr_var_name in acmi_global_to_attr.items():
        if line.startswith(attr_pointer):
            setattr(file_data, attr_var_name, line[len(attr_pointer) :])


def object_line(line: list, file_data: FileData):
    attrs = attr_split(line)
    id = str(attrs[0])
    new = False
    obj_by_id = file_data.get_obj_by_id(id)
    if obj_by_id:
        obj_data = obj_by_id
        if obj_data.check_skip_dying_type():
            return
        new = False
        acmi_obj_attr_list = acmi_old_obj_to_attr
    else:
        new = True
        obj_data = file_data.new_obj(id)
        obj_data.state = "Alive"
        acmi_obj_attr_list = acmi_new_obj_to_attr
    acmi_obj_attr_list = acmi_obj_to_attr_all  # FUTUREDO could use shorter dictionary to reduce time/memory? Unsure if it would have any effect
    for attr_line in attrs:
        for acmi_pointer, obj_attr_name in acmi_obj_attr_list.items():
            if attr_line.startswith(
                acmi_pointer
            ):  # TODO how to make this more efficient?
                if acmi_pointer == "T=":
                    transform_line = attr_line[2:]
                    transformers = transform_line.split("|")
                    obj_data.update_transform(
                        transformers[1], transformers[0], transformers[2]
                    )
                elif obj_attr_name == None:
                    break  # dict.value==None -> skip this attr
                else:
                    setattr(obj_data, obj_attr_name, attr_line[len(acmi_pointer) :])
    if new:
        # logger.debug(f"NEW OBJECT:\n\t\tName: {obj_data.name}   Type: {obj_data.type}   ID: {obj_data.id}")
        if "Missile" in obj_data.type:
            max_avg_lat_long = 0.1
            max_alt = 100
            launcher_obj, distance_coords, avg_unit_dist = get_launcher(
                obj_data
            )  # FUTUREDO update get_launcher logic

            if launcher_obj == None:
                logger.error(
                    f"Missile launch, no other unit: {obj_data.id=} {obj_data.name} {obj_data.spawn_time_stamp=} {obj_data.death_time_stamp=}"
                )
            elif max_avg_lat_long < avg_unit_dist:
                logger.debug(
                    f"Missile launch, no unit within range - {max_avg_lat_long=} {distance_coords=} {avg_unit_dist=}\n\tMissile: {obj_data.id} {obj_data.type} {obj_data.name} {obj_data.pilot}\n\tLauncher: {launcher_obj.id} {launcher_obj.type} {launcher_obj.name} {launcher_obj.pilot}"
                )
            else:
                launcher_obj.add_launch(obj_data)
                logger.trace(
                    f"Missile launch success - {max_avg_lat_long=} {distance_coords=} {avg_unit_dist=}\n\tMissile: {obj_data.id} {obj_data.type} {obj_data.name} {obj_data.pilot}\n\tLauncher: {launcher_obj.id} {launcher_obj.type} {launcher_obj.name} {launcher_obj.pilot}"
                )
                logger.critical(
                    f"New launch: {obj_data.id=} {obj_data.name=} {obj_data.launcher} {obj_data.type}\n\t{launcher_obj.id=} {launcher_obj.name=} {launcher_obj.launches=} {launcher_obj.type}"
                )


def time_stamp_line(line: list, file_data: FileData, last_file_tick_processed: int):
    new_time = float(line[1:])
    file_data.set_time(new_time)
    if (file_data.time_stamp == 0) or (
        file_data.time_stamp > last_file_tick_processed + 1
    ):
        process_file_tick(file_data)
        last_file_tick_processed += 1
    return last_file_tick_processed


def obj_removed_line(line: list, file_data: FileData):
    # TODO add killed-by logic/checking (will be delayed - check dying unit against recently dead units)
    obj_id = line[1:]
    obj = file_data.get_obj_by_id(obj_id)
    if obj:
        if obj.check_skip_dying_type():
            return
        elif obj.check_state("Alive"):
            obj.update_to_dying()
        else:
            raise ValueError(
                f"Attempting to remove object that is not alive and not skip dying:\n\t{obj.id=} {obj.type=} {obj.name=} {obj.death_time_stamp=}\n\t{line=}"
            )
        logger.trace(
            f"REMOVE OBJECT: {obj.id=} {obj.type=} {obj.name=} {obj.death_time_stamp=} {obj.file_obj.time_stamp=}\n\t{line}"
        )

    else:
        logger.error(f"{file_data.objects.items()=}\n\t{obj_id=} {line=}")
        raise ValueError(f"Removed object is not within file_data: {obj_id=}")
