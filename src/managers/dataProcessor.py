from src.classes.DCSEvent import DCSEvent
from src.classes.FileData import FileData
from src.classes.DCSObject import DCSObject
from src.utils.coordUtils import get_closest_obj
from src.managers.logHandler import logger
from src.data.typeReferences import skip_dying_types, killer_types
from src.utils.processingUtils import check_is_type


# TODO MASSIVE TIME SINK
def process_file_tick(file: FileData):
    if not isinstance(file, FileData):
        raise TypeError(f"FileData is not FileData: {type(file)=}")
    dying_ref_list = [
        obj for obj in file.dying_objects.values() if not obj.check_skip_dying_type()
    ]
    for ref_obj in dying_ref_list:
        if (file.time_stamp - ref_obj.death_time_stamp) > 10:
            ref_obj.update_to_dead()
            logger.debug(
                f"Dying process delay expired: id:{ref_obj.id=} type:{ref_obj.type=}"
            )
            continue

        if ref_obj.name not in [
            "AIM_120C",
            "AIM-9",
        ]:  # TODO update to obj.type using list
            continue

        if ref_obj.check_skip_dying_type() or ref_obj.check_state("Dead"):
            continue

        if len(dying_ref_list) > 1:
            closest_list = [o for o in dying_ref_list if o.check_state("Dying")]
            closest_obj, dist = get_closest_obj(ref_obj, closest_list)
        else:
            logger.trace(f"ref_list len <= 1: {dying_ref_list=}")
            return

        if closest_obj == None:
            logger.trace(f"closest_obj is None - {file.dying_objects.keys()=}")
            return
        # logger.debug(
        #     f"Closest object: ref:{ref_obj.id} other:{closest_obj.id} dist:{dist} time:{file.time_stamp}"
        # )
        if not closest_obj.check_state("Dying"):
            raise ValueError(
                f"Closest object is not dying:\n\t{closest_obj.id=} {closest_obj.type=}\n\t{ref_obj.id=} {ref_obj.type=}"
            )
        # TODO: currently only checks for kills, NOT HITS
        # TODO: get closest objects within range/radius
        # TODO: get working coordinates to distance function
        if dist < 0.1:
            if check_is_type(ref_obj, killer_types) and not check_is_type(
                closest_obj, killer_types
            ):
                logger.critical(
                    f"Closest object:\n\t\t{file.time_stamp=} {dist=}\n\t\t{ref_obj.id=} {ref_obj.type=} {ref_obj.name=} {f'{ref_obj.launcher.name} {ref_obj.launcher.pilot}' if ref_obj.launcher != None else ''}\n\t\t{closest_obj.id=} {closest_obj.type=} {closest_obj.name=} {f'{closest_obj.launcher.name} {closest_obj.launcher.pilot}' if closest_obj.launcher != None else ''}\n\t\t{ref_obj.pilot=} {closest_obj.pilot=}"
                )
                ref_obj.add_kill(closest_obj)
    # TODO add more checks here, NEEDS testing

    # logger.debug(f"{file.dying_objects.keys()=}")
    # logger.debug(f"{file.objects.keys()=}")
    # logger.debug(f"{file.dying_objects.keys()=}")
    # # logger.debug(f"{file.dead_objects.keys()=}")
    # logger.debug(f"{file.time_stamp=}")
