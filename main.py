import logging
from src.fileManager import read_files
from src.utils.performance import get_timer
from src.dirManager import get_directory, get_files
from src.outcomeWriter import write_outcome

try:
    from dev.dev_dirs import test_dir as input_dir
    from dev.dev_dirs import test_file1 as input_dir
except ImportError:
    input_dir = None

# TODO add *args and **kwargs
# TODO add logging to file

if __name__ == "__main__":
    get_timer()
    logging.basicConfig(
        level=logging.INFO,
        format=f"%(asctime)s %(levelname)s - %(message)s",
        datefmt="%H:%M:%S",
    )
    # files_dir = get_directory(dir_path=None, dialog_single_file=False)
    files_dir = get_directory(dir_path=input_dir, dialog_single_file=False)
    files = get_files(files_dir)
    files_dict = read_files(
        files, AuthorIsUser=True
    )  # AuthorIsUser not implemented yet
    write_outcome(files_dict)  # TODO
    logging.info(f"END - time: {get_timer()}")

# print(f"{' Start ':=^50}") # https://docs.python.org/3/library/string.html#format-examples
