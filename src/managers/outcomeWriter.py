import os
from src.managers.logHandler import logger
from src.utils.timeUtils import get_date_time
from src.utils.outputUtils import files_csv_header, objects_csv_header
import pandas as pd
import csv


def process_outcome(files_data: dict, output_dir: str = None):
    logger.info(f"\n\n{' Data Output '.center(128, '~')}\n")
    outcome_dirs = get_outcome_dirs(output_dir)
    write_outcome(files_data, outcome_dirs)
    return


def get_outcome_dirs(output_dir_input: str) -> tuple[str, str, str]:
    file_dir = os.path.dirname(os.path.realpath(__file__))
    cwd_dir_list = file_dir.split("\\")[:-2]

    if output_dir_input:
        output_dir = output_dir_input
    else:
        output_dir = "/".join(cwd_dir_list + ["outputs"])
    if not os.path.isdir(output_dir):
        raise ValueError(f"Output directory is not a directory: {output_dir=}")

    date, time = get_date_time()
    files_data_dir = "/".join(
        cwd_dir_list + ["outputs", f"{date}_{time}_files_data.csv"]
    )
    objects_data_dir = "/".join(
        cwd_dir_list + ["outputs", f"{date}_{time}_objects_data.csv"]
    )

    with open(files_data_dir, "w", newline="") as f:
        csv_writer = csv.writer(f)
        csv_writer.writerow(files_csv_header)
    with open(objects_data_dir, "w", newline="") as f:
        csv_writer = csv.writer(f)
        csv_writer.writerow(objects_csv_header)

    print(f"{len(files_csv_header)=} {len(objects_csv_header)=}")

    return output_dir, files_data_dir, objects_data_dir


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
            file_data.time_stamp,  # is not 'reset' on end, so acts as 'final' time stamp
        ]
        with open(files_dir, "a", encoding="utf-8-sig", newline="") as f:
            csv_writer = csv.writer(f)
            csv_writer.writerow(file_csv_data_row)

        with open(objects_dir, "a", encoding="utf-8-sig", newline="") as f:
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
                csv_writer = csv.writer(f)
                csv_writer.writerow(object_csv_data_row)
        file_counter += 1


if __name__ == "__main__":
    write_outcome({})
    logger.info(
        "/".join(
            os.path.dirname(os.path.realpath(__file__)).split("\\")[:-2] + ["outputs"]
        )
    )
