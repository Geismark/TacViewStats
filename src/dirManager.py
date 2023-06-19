import logging
import os
import glob
import tkinter as tk
from tkinter import filedialog


def directory_dialog(dialog_single_file):
    # https://stackoverflow.com/questions/9319317/quick-and-easy-file-dialog-in-python
    root = tk.Tk()
    root.withdraw()  # required - hides the root window
    if dialog_single_file:
        dir_path = filedialog.askopenfilename()
    else:
        dir_path = filedialog.askdirectory()
    return dir_path


def get_directory(dir_path=None, dialog_single_file=False):
    if not dir_path:
        dir_path = directory_dialog(dialog_single_file)
    if os.path.isdir(dir_path):
        return str(dir_path)
    elif os.path.isfile(dir_path):
        return str(dir_path)
    else:
        raise FileNotFoundError(f"Directory not found\n\t{dir_path=}")


def get_files(folder_dir: str):
    if os.path.isfile(folder_dir):
        files_any = [folder_dir]
    else:
        files_any = glob.glob(f"{folder_dir}/*.*")  # lists all files in dir
    f_mod, f_txt, f_zip, f_acmi = 0, 0, 0, 0
    for file in files_any:  # TODO could also split string ('.') and count - faster?
        f_zip += file.count(".zip")
        f_acmi += file.count(".acmi")
        f_txt += file.count(".txt")
        f_mod += file.count(".mod")
    logging.debug(
        f"get_files types:\n\tAll={len(files_any)}\n\t{f_zip=}\n\t{f_acmi=}\n\t{f_txt=}\n\t{f_mod=}"
    )
    return files_any


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format=f"%(asctime)s %(levelname)s - %(message)s",
        datefmt="%H:%M:%S",
    )
    dir = get_directory(dialog_single_file=True)
    print(get_files(dir))
