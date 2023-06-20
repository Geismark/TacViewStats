import os
import logging

# from src.utils.fileUtils import FileData, DCSObject, DCSEvent


def write_outcome(files_data: dict):
    logging.info(f"\n\n{' Data Output '.center(128, '~')}\n")
    file_dir = os.path.dirname(os.path.realpath(__file__))
    cwd_dir_list = file_dir.split("\\")[:-2]
    assert cwd_dir_list[-1] == "TacViewStats"
    # TODO thought: might be a good idea to allow users to rename the folder.....
    output_dir = "/".join(cwd_dir_list + ["outputs"])
    logging.debug(f"{output_dir=}\n{file_dir=}\n{cwd_dir_list=}")
    assert os.path.isdir(output_dir)
    print(f"{files_data}")
    for file_data in files_data.values():
        print(f"\n{file_data.file_name}\n")
        for obj in file_data.objects.values():
            if len(obj.launches) > 0:
                print((f"{obj.id} - {obj.type} - {obj.name} - {obj.pilot}"))
                for launch in obj.launches:
                    print(f"\t{launch.name}")
    print("\n")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format=f"%(asctime)s %(levelname)s - %(message)s",
        datefmt="%H:%M:%S",
    )
    print(write_outcome({}))
    print(
        "/".join(
            os.path.dirname(os.path.realpath(__file__)).split("\\")[:-2] + ["outputs"]
        )
    )
