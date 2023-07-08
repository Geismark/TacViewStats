from src.managers.logHandler import logger
import zipfile
import os
from src.utils.fileUtils import FileData, DCSObject, coords_to_distance
from src.managers.lineHandler import (
    global_line,
    object_line,
    time_line,
    obj_removed_line,
)
from src.utils.timeUtils import get_timer


# FUTUREDO do all zip checks before starting any reading?
def is_zip(file: str) -> bool:
    if not os.path.isfile(file):
        raise FileNotFoundError(f"{file=}")

    if zipfile.is_zipfile(file):
        if ".zip" in file:
            return True
        else:
            logger.debug(f"ZIP file without .zip:\n\t{file=}")
            return True
    return False


def read_files(files: list[str], AuthorIsUser: bool):
    files_data = {}
    logger.info(f"Total files: {len(files)}   -   {get_timer()}")
    for index, file in enumerate(files):
        logger.info(f"Reading file {index} {get_timer()}  -   {file}")
        files_data[index] = FileData()
        file_data = files_data[index]
        file_data.file_name = file.split("\\")[-1]
        # files_data[index] = file_data = FileData()     # TODO will this work?
        # TODO check each file is actually a TacView File (both zip and non-zip)
        if is_zip(file):
            file_data.is_zip = True
            with zipfile.ZipFile(
                file, mode="r"
            ) as zipped_file:  # FUTUREDO better/shorter way to read zips?
                contents = zipped_file.namelist()
                if len(contents) != 1:  # FUTUREDO assert -> continue
                    # all acmi zips should only have 1 .txt.acmi (or .mod) file
                    # but assert will stop entire program, rather than just skipping (but good for testing)
                    # continue
                    raise ValueError(
                        f"ZIP has multiple compressed files\n{file=}\n{contents=}"
                    )
                with zipped_file.open(contents[0]) as unzipped:
                    file_text = unzipped.read()
                    file_decoded = file_text.decode("IBM437")  # default ZIP encoding
                    file_formatted = file_decoded.splitlines()
        else:
            file_data.is_zip = False
            with open(file) as open_file:
                file_formatted = [line for line in open_file]
        logger.debug(f"\n\t{file_data.file_name=}\n\t{file_data.is_zip=}\n")
        process_file(file_data, file_formatted, AuthorIsUser)
    return files_data


def process_file(file_data: FileData, file: list[str], AuthorIsUser: bool):
    if file_data.is_zip:
        file_start = "∩╗┐FileType="
    else:
        file_start = "ï»¿FileType="  # I have no idea what these characters are, I assume same as the .zip just extracted
    last_file_tick_processed = 0
    line_continued = False  # FUTUREDO distinguish between comments/briefing/debriefing
    for index, line in enumerate(file):
        line = line.rstrip("\n")
        if index == 0:
            if not line.startswith(file_start):
                raise TypeError(
                    f"File does not start with ∩╗┐\n\t{file_start=}\n\t{line=}"
                )
            file_data.file_type = line[
                len(file_start) :
            ]  # '∩╗┐' accounts for (I assume) the .zip identifier, not present if extracted
            # TODO check if actually acmi file
        elif (
            line_continued
            or line.startswith("0,Comments=")
            or line.startswith("0,Briefing=")
            or line.startswith("0,Debriefing=")
        ):  # TODO separate
            if line.endswith("\\"):
                line_continued = True
            else:
                line_continued = False
            file_data.comments.append(line)
        elif line.startswith("FileVersion="):  # not a global (doesn't start with 0)
            file_data.file_version = line[len("FileVersion=") :]
        elif line.startswith("0,"):
            global_line(line, file_data)
        elif line.startswith("#"):
            last_file_tick_processed = time_line(
                line, file_data, last_file_tick_processed
            )
            logger.trace(f"TIME: {file_data.time_stamp}")
        elif line.startswith("-"):
            obj_removed_line(line, file_data)
        else:
            # logger.trace("UPDATE OBJECT")
            object_line(line, file_data)
    return


# T = Longitude | Latitude | Altitude
# 104,T=5.0748323|3.9184389|9737.43|-3.3|5.9|44.1|-118663.92|-137639.81|44.9,Type=Air+FixedWing,Name=F-16C_50,Pilot=Spirit 1-1 \, Zen,Group=BVR F-16C,Color=Blue,Coalition=Enemies,Country=xb,Importance=1,IAS=161.9,AOA=5.3,Throttle=0.99,AirBrakes=0,LandingGear=0,FuelWeight=5461.234,FuelFlowWeight=2653,HDM=42.8,RollControlPosition=0,PitchControlPosition=0,YawControlPosition=0,PilotHeadRoll=-34.69,PilotHeadPitch=-67.75,PilotHeadYaw=-17.23
# 204,T=5.0691084|3.9131406|9740.41|-0.8|4.9|44.6|-119250.45|-138218.5|45.4,Type=Air+FixedWing,Name=F-16C_50,Pilot=Spirit 1-1 \, Zen,Group=BVR F-16C,Color=Blue,Coalition=Enemies,Country=xb,Importance=1,IAS=162.3,AOA=6.3,Throttle=1.01,AirBrakes=0,LandingGear=0,FuelWeight=5464.921,FuelFlowWeight=2295,HDM=43.3,RollControlPosition=0,PitchControlPosition=0,YawControlPosition=0,PilotHeadRoll=20.69,PilotHeadPitch=-54.37,PilotHeadYaw=16.38
# 27203,T=5.0748563|3.9191907|9738.07|-3.1|6|44.1|-118660.32|-137556.58|45,Type=Air+FixedWing,Name=F-16C_50,Pilot=Brody,Group=BVR F-16C,Color=Blue,Coalition=Enemies,Country=xb
# 27303,T=5.0695246|3.9142486|9746.65|-0.3|1.6|44.7|-119206.66|-138096.36|45.5,Type=Air+FixedWing,Name=F-16C_50,Pilot=Brody,Group=BVR F-16C,Color=Blue,Coalition=Enemies,Country=xb
# 27403,T=5.406326|4.2691396|10204.17|-2.1|18.8|46.9|-84722.34|-99230.39|47.6,Type=Weapon+Missile,Name=AIM_120C,Color=Blue,Coalition=Enemies,Country=xb

if __name__ == "__main__":
    logger.info(get_timer())
