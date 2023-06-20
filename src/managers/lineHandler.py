import logging
from src.utils.fileUtils import (
    FileData,
    attr_split,
    get_nearest_obj,
    is_unit,
    get_launcher,
)
from src.data.acmiAttrDicts import (
    acmi_old_obj_to_attr,
    acmi_new_obj_to_attr,
    acmi_obj_to_attr_all,
    acmi_global_to_attr,
)

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
    if id in file_data.objects:
        new = False
        obj_data = file_data.objects[id]
        acmi_obj_attr_list = acmi_old_obj_to_attr
    else:
        new = True
        obj_data = file_data.new_obj(id)
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
        # logging.debug(f"NEW OBJECT:\n\t\tName: {obj_data.name}   Type: {obj_data.type}   ID: {obj_data.id}")
        if "Missile" in obj_data.type:
            max_avg_lat_long = 0.1
            max_alt = 100
            launcher_obj, distance_coords, avg_unit_dist = get_launcher(
                file_data, obj_data
            )

            # logging.debug(f"\n#####################################\n{obj_data.id} {obj_data.name} {obj_data.type}\n\t{obj_data.get_pos()}\n-------------------------------------\n")
            # for obj in file_data.objects.values():
            # 	if is_unit(obj):
            # 		logging.debug(f"{obj.id} {obj.name} {obj.type} {obj.pilot}\n\t{obj.get_pos()}")
            # logging.debug("\n-------------------------------------\n")
            if launcher_obj == None:
                logging.error(
                    f"Missile launch, no other unit: {obj_data.id=} {obj_data.name} {obj_data.spawn_time_stamp=} {obj_data.death_time_stamp=}"
                )
            elif max_avg_lat_long < avg_unit_dist:
                logging.warning(
                    f"Missile launch, no unit within range - {max_avg_lat_long=} {distance_coords=} {avg_unit_dist=}\n\tMissile: {obj_data.id} {obj_data.type} {obj_data.name} {obj_data.pilot}\n\tLauncher: {launcher_obj.id} {launcher_obj.type} {launcher_obj.name} {launcher_obj.pilot}"
                )
            else:
                obj_data.launcher = launcher_obj
                launcher_obj.add_launch(obj_data)
                logging.debug(
                    f"MISSILE LAUNCH - {max_avg_lat_long=} {distance_coords=} {avg_unit_dist=}\n\tMissile: {obj_data.id} {obj_data.type} {obj_data.name} {obj_data.pilot}\n\tLauncher: {launcher_obj.id} {launcher_obj.type} {launcher_obj.name} {launcher_obj.pilot}"
                )
            # logging.debug(f"{file_data.get_coord_reference()}\n#####################################\n")


def time_line(line: list, file_data: FileData):
    new_time = float(line[1:])
    file_data.set_time(new_time)


def obj_removed_line(line: list, file_data: FileData):
    # TODO add killed-by logic/checking (will be delayed - check dying unit against recently dead units)
    obj_id = line[1:]
    if str(obj_id) in file_data.objects:
        file_data.objects[obj_id].die()
    else:
        logging.error(f"{file_data.objects.items()=}")
        raise ValueError(f"Removed object is not within file_data: {obj_id}")
