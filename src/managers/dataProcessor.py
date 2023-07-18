from src.managers.logHandler import logger
from src.classes.FileData import FileData
from src.utils.coordUtils import get_closest_obj
from src.data.typeReferences import killer_types
from src.utils.processingUtils import check_is_type, check_lists_share_element
from src.data.valueReferences import max_kill_distance


# TODO MASSIVE TIME SINK
def process_file_tick(file: FileData):
    """Processes all data within the associated FileData.\n\n
    Should not be run every file update - intended to be run/updated every second of file-update-time at most.\n\n
    Ensure this is run at least twice within the dying-to-dead processing delay for any object to account for desync.
    """
    if not isinstance(file, FileData):
        raise TypeError(f"FileData is not FileData: {type(file)=}")
    dying_ref_list = [
        obj
        for obj in list(file.dying_objects.values())
        if not obj.check_skip_data_processing_type()
    ]
    for ref_obj in dying_ref_list:
        # if dying grace period is over, update to dead
        if (file.time_stamp - ref_obj.death_time_stamp) > 10:
            ref_obj.update_to_dead()
            logger.trace(f"Dying process delay expired: {ref_obj.info()}")
            continue
        # ensure ref_obj is dying (i.e.: hasn't died since dying_ref_list was created)
        if not ref_obj.check_state("Dying"):
            continue

        # if there is more than 1 object, find closest object and distance
        if len(dying_ref_list) > 1:
            closest_list = [o for o in dying_ref_list if o.check_state("Dying")]
            closest_obj, dist = get_closest_obj(ref_obj, closest_list)
        # if len == 1 only the current object remains, can skip rest of processing
        elif len(dying_ref_list) == 1:
            logger.detail(f"ref_list len == 1: {len(dying_ref_list)=}")
            return
        # if len == 0, something has gone wrong, as if no Dying objects remain, this point shouldn't be reached
        elif len(dying_ref_list) == 0:
            raise ValueError(
                f"ref_list len == 0: {[[o.id, o.uid, o.state] for o in dying_ref_list]=}"
            )
            return
        else:
            return

        if not check_lists_share_element(ref_obj.type, killer_types):
            continue

        if ref_obj.check_skip_data_processing_type() or ref_obj.check_state("Dead"):
            continue
            # both above and below unfortunately (potentially?) necessary, as objects in ref_list change during this loop

        if closest_obj == None:
            logger.trace(f"closest_obj is None - {file.dying_objects.keys()=}")
            return

        if not closest_obj.check_state("Dying"):
            raise ValueError(
                f"Closest object is not dying:\n\t{closest_obj.id=} {closest_obj.type=}\n\t{ref_obj.id=} {ref_obj.type=}"
            )
        # TODO: currently only checks for kills, NOT HITS
        # TODO: get closest objects within range/radius
        # TODO: get working coordinates to distance function
        if dist < max_kill_distance:
            if check_is_type(ref_obj, killer_types) and not check_is_type(
                closest_obj, killer_types
            ):
                ref_obj.add_kill(closest_obj, dist=dist)
    # TODO add more checks here, NEEDS testing
