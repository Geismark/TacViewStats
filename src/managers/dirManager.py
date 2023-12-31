from src.managers.logHandler import logger
import os
import glob
import tkinter as tk
from tkinter import filedialog


def directory_dialog(dialog_single_file, init_dir=None, init_file=None):
    """Opens a dialog to select a directory or file."""
    # https://stackoverflow.com/questions/9319317/quick-and-easy-file-dialog-in-python
    # TODO: multiple files can be selected
    root = tk.Tk()
    root.withdraw()  # required - hides the root window
    if dialog_single_file:
        dir_path = filedialog.askopenfilename(
            initialdir=init_dir, initialfile=init_file
        )
    else:
        dir_path = filedialog.askdirectory(initialdir=init_dir)
    return dir_path


def get_directory(
    dir_path=None, dialog_single_file=False, init_dir=None, init_file=None
):
    """Returns path as a directory string. If none is given, opens a dialog."""
    if not dir_path:
        dir_path = directory_dialog(
            dialog_single_file, init_dir=init_dir, init_file=init_file
        )
    if os.path.isdir(dir_path):
        return str(dir_path)
    elif os.path.isfile(dir_path):
        return str(dir_path)
    else:
        raise FileNotFoundError(f"Directory not found\n\t{dir_path=}")


def get_files(folder_dir: str):
    """Returns list of any files found in folder directory,
    alongside list of extensions found:\n
    [.zip, .acmi, .txt, .mod]"""
    if os.path.isfile(folder_dir):
        files_any = [folder_dir]
    else:
        files_any = glob.glob(f"{folder_dir}/*.*")  # lists all files in dir
        files_any = [
            file
            for file in files_any
            if os.path.isfile(file) and file.endswith(".acmi")
        ]
    f_mod, f_txt, f_zip, f_acmi = 0, 0, 0, 0
    for index, file in enumerate(files_any):
        # TODO could also split string ('.') and count - faster?
        f_zip += file.count(".zip")
        f_acmi += file.count(".acmi")
        f_txt += file.count(".txt")
        f_mod += file.count(".mod")
        files_any[index] = file.replace("\\", "/")
    logger.debug(
        f"get_files types:\n\tAll={len(files_any)}\n\t{f_zip=}\n\t{f_acmi=}\n\t{f_txt=}\n\t{f_mod=}"
    )
    return files_any, [f_zip, f_acmi, f_txt, f_mod]


if __name__ == "__main__":
    dir = get_directory()
    logger.debug(get_files(dir))
