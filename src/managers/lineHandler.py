from src.managers.logHandler import logger
from src.utils.fileUtils import (
    FileData,
    attr_split,
)
from src.data.acmiAttrDicts import (
    acmi_old_obj_to_attr,
    acmi_new_obj_to_attr,
    acmi_obj_to_attr_all,
    acmi_global_to_attr,
)
from src.managers.dataProcessor import process_file_tick
from src.utils.coordUtils import get_closest_obj

# https://www.tacview.net/documentation/acmi/en/
# T = Longitude | Latitude | Altitude
# T = Longitude | Latitude | Altitude | U | V
# T = Longitude | Latitude | Altitude | Roll | Pitch | Yaw
# T = Longitude | Latitude | Altitude | Roll | Pitch | Yaw | U | V | Heading


def global_line(line: list, file_data: FileData):
    """Takes a global line and updates the FileData object."""
    for attr_pointer, attr_var_name in acmi_global_to_attr.items():
        if line.startswith(attr_pointer):
            setattr(file_data, attr_var_name, line[len(attr_pointer) :])


def object_line(line: list, file_data: FileData):
    """Parses an object update line and updates the relevant attributes in the FileData object."""
    attrs = attr_split(line)
    id = str(attrs[0])
    new = False
    obj_by_id = file_data.get_obj_by_id(id, "Alive")
    if obj_by_id:
        obj_data = obj_by_id
        if (
            obj_data.check_skip_dying_type()
        ):  # TODO update this to something more relevant
            return
        new = False
        acmi_obj_attr_list = acmi_old_obj_to_attr
    else:
        new = True
        obj_data = file_data.new_obj(id, init_state="Alive")
        acmi_obj_attr_list = acmi_new_obj_to_attr
    acmi_obj_attr_list = acmi_obj_to_attr_all  # FUTUREDO could use shorter dictionary to reduce time/memory? Unsure if it would have any effect
    for attr_line in attrs:
        if attr_line.startswith("Type="):
            obj_data.set_types(attr_line[len("Type=") :])
            continue
        for acmi_pointer, obj_attr_name in acmi_obj_attr_list.items():
            if attr_line.startswith(
                acmi_pointer
            ):  # TODO how to make this more efficient?
                if acmi_pointer == "T=":
                    if obj_data.check_state("Dead"):
                        logger.critical(
                            f"Updating object attributes with check_state(Dead):\n\t{obj_data.__dict__}"
                        )
                    transform_line = attr_line[2:]
                    transformers = transform_line.split("|")
                    obj_data.update_transform(
                        transformers[1], transformers[0], transformers[2]
                    )
                elif obj_attr_name == None:
                    continue  # dict.value==None -> skip this attr
                else:
                    setattr(obj_data, obj_attr_name, attr_line[len(acmi_pointer) :])
    if new:
        if obj_data.file_obj != file_data:
            raise ValueError(
                f"New object FileDate != file_data passed to object_line {obj_data.file_obj=} {file_data=}"
            )
        if "Missile" in obj_data.type:
            max_avg_dist = 0.01
            max_alt = 100
            launcher_obj, avg_unit_dist = get_closest_obj(
                obj_data, list(file_data.objects.values())
            )  # FUTUREDO update get_launcher logic

            if launcher_obj == None:
                logger.warning(
                    f"Missile launch, no other unit: {obj_data.id=} {obj_data.name} {obj_data.spawn_time_stamp=} {obj_data.death_time_stamp=}"
                )
            elif max_avg_dist < avg_unit_dist:
                logger.debug(
                    f"Missile launch, no unit within range - {max_avg_dist=} {avg_unit_dist=}\n\tMissile: {obj_data.id} {obj_data.type} {obj_data.name} {obj_data.pilot}\n\tLauncher: {launcher_obj.id} {launcher_obj.type} {launcher_obj.name} {launcher_obj.pilot}"
                )
            else:
                launcher_obj.add_launch(obj_data)
                logger.trace(
                    f"Missile launch success - {max_avg_dist=} {avg_unit_dist=}\n\tMissile: {obj_data.id} {obj_data.type} {obj_data.name} {obj_data.pilot}\n\tLauncher: {launcher_obj.id} {launcher_obj.type} {launcher_obj.name} {launcher_obj.pilot}"
                )
        logger.detail(f"NEW OBJECT: {obj_data.info()}")


def time_stamp_line(line: list, file_data: FileData, last_file_tick_processed: int):
    """Takes a time stamp line and updates the FileData object.\n\nCalls process_file_tick if set amount of time in recording has passed."""
    seconds_per_process = 1
    new_time = float(line[1:])
    file_data.set_time(new_time)
    if (file_data.time_stamp == 0) or (
        file_data.time_stamp > last_file_tick_processed + seconds_per_process
    ):
        process_file_tick(file_data)
        last_file_tick_processed += seconds_per_process
    return last_file_tick_processed


def obj_removed_line(line: list, file_data: FileData):
    """Parses an object removal line and updates the FileData and DCSObject objects."""
    # TODO add killed-by logic/checking (will be delayed - check dying unit against recently dead units)
    obj_id = line[1:]
    obj = file_data.get_obj_by_id(obj_id)
    if obj:
        if obj.check_skip_dying_type():
            obj.update_to_dead()
        elif obj.check_state("Alive"):
            obj.update_to_dying()
        else:
            raise ValueError(
                f"Attempting to remove object that is not alive and not skip dying:\n\t{obj.id=} {obj.type=} {obj.name=} {obj.death_time_stamp=}\n\t{line=}"
            )
        logger.detail(f"REMOVE LINE OBJECT: {obj.info(times=True)}")

    else:
        raise ValueError(
            f"Attempting to remove object id that is not within file_data: {line=}\n{file_data.objects.items()=}"
        )
