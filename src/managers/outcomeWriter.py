import os
from src.managers.logHandler import logger


def write_outcome(files_data: dict):
    logger.info(f"\n\n{' Data Output '.center(128, '~')}\n")
    file_dir = os.path.dirname(os.path.realpath(__file__))
    cwd_dir_list = file_dir.split("\\")[:-2]
    assert cwd_dir_list[-1] == "TacViewStats"
    # TODO thought: might be a good idea to allow users to rename the folder.....
    output_dir = "/".join(cwd_dir_list + ["outputs"])
    logger.debug(f"{output_dir=}\n{file_dir=}\n{cwd_dir_list=}")
    assert os.path.isdir(output_dir)
    file_names_dict = {
        index: list(file.file_name.split("/"))[-1] for index, file in files_data.items()
    }
    logger.info(f"{files_data=}\n\t{file_names_dict=}")
    for file_data in files_data.values():
        logger.info(
            f"\n\nFile Name: {file_data.file_name}\n\tFile Size:   {file_data.file_size:,} KB\n\tFile Length: {file_data.file_length:,}\n"
        )
        for obj in (
            list(file_data.objects.values())
            + list(file_data.dying_objects.values())
            + list(file_data.dead_objects.values())
        ):
            if len(obj.launches) > 0:
                logger.info((f"{obj.id} - {obj.type} - {obj.name} - {obj.pilot}"))
                for launch in obj.launches.values():
                    if len(launch.kills.values()) == 0:
                        logger.info(
                            f"\t{launch.name}\t{launch.type}\t{len(launch.kills.values())} {launch.spawn_time_stamp=}"
                        )
                    elif len(launch.kills.values()) == 1:
                        logger.info(
                            f"\t{launch.name}\t{launch.type}\t{len(launch.kills.values())} - {list(launch.kills.values())[0].name}\t{list(launch.kills.values())[0].pilot}\t{list(launch.kills.values())[0].type} {launch.spawn_time_stamp=}"
                        )
                    else:
                        logger.critical(f"Multiple kills: {launch.kills.values()=}")
    # logger.info("\n")


# seconds to minute seconds


if __name__ == "__main__":
    write_outcome({})
    logger.info(
        "/".join(
            os.path.dirname(os.path.realpath(__file__)).split("\\")[:-2] + ["outputs"]
        )
    )
