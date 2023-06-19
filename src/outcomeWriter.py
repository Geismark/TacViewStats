try:
    from src.utils.fileUtils import FileData, DCSObject, DCSEvent
except ImportError:
    from utils.fileUtils import FileData, DCSObject, DCSEvent

import os


def write_outcome(files_data: dict):
    print(f"\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n")
    file_dir = os.path.dirname(os.path.realpath(__file__))
    output_dir = f"{file_dir[:-4]}\\outputs"
    print(f"{output_dir=}\n{file_dir=}")
    assert os.path.isdir(output_dir)
    print(f"{files_data}")
    for file_data in files_data.values():
        print(f"\n{file_data.file_name}\n")
        for obj in file_data.objects.values():
            if len(obj.launches) > 0:
                print((f"{obj.id} - {obj.type} - {obj.name} - {obj.pilot}"))
                for launch in obj.launches:
                    print(f"\t{launch.name}")

    return


if __name__ == "__main__":
    print(write_outcome({}))
