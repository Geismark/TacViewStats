import os
from src.managers.logHandler import logger
from src.utils.timeUtils import get_date_time
from src.utils.outputUtils import (
    files_csv_header,
    objects_csv_header,
    output_csv_header,
    output_exclude_object_types,
)
import csv
import re
from src.utils.configUtils import config


def process_outcome(files_data: dict):
    logger.info(f"\n\n{' Data Output '.center(128, '~')}\n")
    outcome_dirs = get_outcome_dirs()
    write_outcome(files_data, outcome_dirs)
    return


def get_outcome_dirs() -> tuple[str, str, str]:
    output_dir_config = config.OUTPUTS.output_dir
    references_dir_config = config.OUTPUTS.references_dir

    file_dir = os.path.dirname(os.path.realpath(__file__))
    cwd_dir_list = file_dir.split("\\")[:-2]
    date, time = get_date_time()

    # USER OUTPUT
    if output_dir_config:
        output_dir = output_dir_config
    else:
        output_dir = "/".join(cwd_dir_list + ["outputs"])
    if not os.path.isdir(output_dir):
        raise ValueError(f"Output directory is not a directory: {output_dir=}")
    output_file = f"{output_dir}/TVS_output_{date}_{time}.csv"
    with open(output_file, "x", newline="") as f:
        csv_writer = csv.writer(f)
        csv_writer.writerow(output_csv_header)

    # REFERENCE OUTPUTS
    if references_dir_config:
        files_data_dir = "/".join(
            references_dir_config + [f"{date}_{time}_files_data.csv"]
        )
        objects_data_dir = "/".join(
            references_dir_config + [f"{date}_{time}_objects_data.csv"]
        )
    else:
        files_data_dir = "/".join(
            cwd_dir_list + ["outputs", f"{date}_{time}_files_data.csv"]
        )
        objects_data_dir = "/".join(
            cwd_dir_list + ["outputs", f"{date}_{time}_objects_data.csv"]
        )
    with open(files_data_dir, "x", newline="") as f:
        csv_writer = csv.writer(f)
        csv_writer.writerow(files_csv_header)
    with open(objects_data_dir, "x", newline="") as f:
        csv_writer = csv.writer(f)
        csv_writer.writerow(objects_csv_header)

    output_directories = (output_file, files_data_dir, objects_data_dir)

    logger.info(f"Output directories: {output_directories}")

    return output_directories


def get_data_file_names():
    date, time = get_date_time()
    return f"files_data_{date}_{time}.csv", f"objects_data_{date}_{time}.csv"


def write_outcome(files_data: dict, outcome_dirs: tuple[str, str, str]):
    output_dir, files_dir, objects_dir = outcome_dirs

    logger.debug(f"{output_dir=}\n{files_dir=}\n{objects_dir=}")
    file_names_dict = {
        index: list(file.file_name.split("/"))[-1] for index, file in files_data.items()
    }
    logger.info(f"{len(files_data)=}\n{file_names_dict=}")

    file_counter = 0
    object_counter = 0

    for file_data in files_data.values():
        logger.info(
            f"\n\n\tFile Name: {file_data.file_name}\n\tFile Size:   {file_data.file_size:,} KB\n\tFile Length: {file_data.file_length:,}\n"
        )
        logger.info(file_data.info(all=True))

        file_csv_data_row = [
            file_counter,
            file_data.file_name,
            file_data.author,
            file_data.mission_title,
            file_data.file_type,
            file_data.file_version,
            file_data.file_length,
            file_data.file_size,
            file_data.recorder,
            file_data.source,
            file_data.mission_date,
            file_data.record_date,
            file_data.latitude_reference,
            file_data.longitude_reference,
            len(file_data.all_objects),
            file_data.first_time_stamp,
            file_data.time_stamp,  # is not 'reset' on file end, so acts as 'final' time stamp
        ]
        with open(files_dir, "a", encoding="utf-8-sig", newline="") as file_f:
            file_csv_writer = csv.writer(file_f)
            file_csv_writer.writerow(file_csv_data_row)

        with open(objects_dir, "a", encoding="utf-8-sig", newline="") as obj_f, open(
            output_dir, "a", encoding="utf-8-sig", newline=""
        ) as outcome_f:
            for obj in (
                list(file_data.objects.values())
                + list(file_data.dying_objects.values())
                + list(file_data.dead_objects.values())
            ):
                # if len(obj.launches) > 0:
                #     logger.info((f"{obj.id} - {obj.type} - {obj.name} - {obj.pilot}"))
                #     for launch in obj.launches.values():
                #         if len(launch.kills.values()) == 0:
                #             logger.info(
                #                 f"\t{launch.name}\t{launch.type}\t{len(launch.kills.values())} {launch.spawn_time_stamp=}"
                #             )
                #         elif len(launch.kills.values()) == 1:
                #             logger.info(
                #                 f"\t{launch.name}\t{launch.type}\t{len(launch.kills.values())} - {list(launch.kills.values())[0].name}\t{list(launch.kills.values())[0].pilot}\t{list(launch.kills.values())[0].type} {launch.spawn_time_stamp=}"
                #             )
                #         else:
                #             logger.critical(f"Multiple kills: {launch.kills.values()=}")
                object_csv_data_row = [
                    file_counter,
                    obj.uid,
                    obj.id,
                    obj.pilot,
                    obj.name,
                    obj.coalition,
                    obj.type,
                    obj.country,
                    len(obj.launches),
                    len(obj.kills),
                    obj.killer.uid if obj.killer else None,
                    obj.killer_weapon.uid if obj.killer else None,
                    obj.spawn_time_stamp,
                    obj.death_time_stamp
                    if obj.death_time_stamp
                    else obj.file_obj.time_stamp,
                    obj.origin,
                    obj.launcher.uid if obj.launcher else None,
                    object_counter,
                ]
                obj_csv_writer = csv.writer(obj_f)
                obj_csv_writer.writerow(object_csv_data_row)

                if set(output_exclude_object_types).isdisjoint(obj.type):
                    output_csv_data_row = [
                        file_counter,
                        obj.uid,
                        obj.pilot,
                        obj.name,
                        obj.coalition,
                        obj.type,
                        len(obj.launches),
                        len(obj.kills),
                        obj.killer.name if obj.killer else None,
                        obj.killer_weapon.name if obj.killer else None,
                        obj.spawn_time_stamp,
                        obj.death_time_stamp
                        if obj.death_time_stamp
                        else obj.file_obj.time_stamp,
                        file_data.mission_title,
                        re.split(r"[\\ | /]", file_data.file_name)[-1],
                    ]
                    output_csv_writer = csv.writer(outcome_f)
                    output_csv_writer.writerow(output_csv_data_row)
        file_counter += 1


if __name__ == "__main__":
    write_outcome({})
    logger.info(
        "/".join(
            os.path.dirname(os.path.realpath(__file__)).split("\\")[:-2] + ["outputs"]
        )
    )
