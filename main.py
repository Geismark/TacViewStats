# MUST BE IMPORTED FIRST
from src.managers.logHandler import logger


from src.managers.fileManager import read_files
from src.utils.timeUtils import get_timer
from src.managers.dirManager import get_directory, get_files
from src.managers.outcomeWriter import process_outcome

try:
    from dev.dev_vars import test_file2 as input_dir  # trimmed test file
    from dev.dev_vars import test_temp as input_dir
    from dev.dev_vars import test_launcher_accuracy as input_dir
    from dev.dev_vars import test_kill_accuracy as input_dir
    from dev.dev_vars import test_brody as input_dir
    from dev.dev_vars import problem as input_dir  # problem file
    from dev.dev_vars import test_file1 as input_dir  # full test file
    from dev.dev_vars import test_dir as input_dir  # test dir


except ImportError:
    input_dir = None


if __name__ == "__main__":
    get_timer()

    # input_dir = None
    dialog_single_file = False

    files_dir = get_directory(dir_path=input_dir, dialog_single_file=dialog_single_file)
    files, _ = get_files(files_dir)
    files_dict = read_files(
        files, AuthorIsUser=True
    )  # AuthorIsUser not implemented yet
    process_outcome(files_dict, None)
    end_time = get_timer()
    logger.info(
        f"END\n\t{'Total Time: ':>24}{end_time:.6f}\n\t{'Average Time per File: ':>24}{end_time / len(files_dict):.6f}"
    )

# print(f"{' Start ':=^50}") # https://docs.python.org/3/library/string.html#format-examples
