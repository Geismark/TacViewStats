import re, logging
from math import radians, cos, sin, asin, sqrt
from statistics import fmean
from src.classes.FileData import FileData
from src.classes.DCSObject import DCSObject
from src.classes.DCSEvent import DCSEvent

# https://www.tacview.net/documentation/acmi/en/
# T = Longitude | Latitude | Altitude
# T = Longitude | Latitude | Altitude | U | V
# T = Longitude | Latitude | Altitude | Roll | Pitch | Yaw
# T = Longitude | Latitude | Altitude | Roll | Pitch | Yaw | U | V | Heading


def attr_split(string):  # regex look-behind not (easily?) applicable
    splits = [0]
    for i, char in enumerate(string):
        if char == "," and string[i - 1] != "\\":
            splits.append(i)
    splits.append(len(string))
    slices = [
        string[i + 1 : j] for i, j in zip(splits, splits[1:])
    ]  # i+1 to remove preceding comma
    if slices == []:
        raise ValueError(
            f"attr_split has empty slices:\n\t{string=}\n\t{splits=}\n\t{slices=}"
        )
    else:
        slices[0] = (
            string[0] + slices[0]
        )  # adds back 1st char of line (because of the i+1 above)

    return slices


def get_launcher(file_data: FileData, origin_obj: DCSObject):
    all_objs = file_data.objects.values()
    closest_coords = [0, 0, 0]
    closest_obj = None
    closest_avg = None
    ordinance_coords = origin_obj.get_real_pos()
    # can use simple numerical comparison as relative difference is all that matters, can check if within a certain distance afterwards
    for obj in all_objs:
        if (not is_unit(obj)) or (obj is origin_obj):
            continue
        launcher_coords = obj.get_real_pos()
        current = [abs(ordinance_coords[i] - launcher_coords[i]) for i in range(3)]
        current_avg = (
            current[0] + current[1] + current[2] / 10_000
        ) / 3  # altitude unit is relatively far greater and less significant
        if (closest_obj == None) or (current_avg < closest_avg):
            closest_coords = current
            closest_obj = obj
            closest_avg = current_avg

    if closest_obj == None or closest_avg > 1:
        logging.info(
            f"LAUNCHER NOT FOUND:\n\t{origin_obj.name=} {origin_obj.type=} {origin_obj.get_pos()=}\n\t{closest_obj.name=} {closest_obj.type=} {closest_obj.get_pos()=}"
        )
    return closest_obj, closest_coords, closest_avg


def get_nearest_obj(file_data: FileData, origin_obj: DCSObject, max_dist):
    all_objs = file_data.objects.values()
    closest = [0, 0, 0]
    closest_avg = None
    closest_obj = None
    for obj in all_objs:
        if not is_unit(obj):
            continue
        elif obj.id == origin_obj.id:
            continue
        current_obj = [None, None, None]
        points = obj.get_pos()
        for i, p in enumerate(points):
            current_obj[i] = abs(origin_obj.get_pos()[i] - p)
        current_avg = fmean(current_obj)
        if closest_obj == None:
            closest = current_obj
            closest_avg = current_avg
            closest_obj = obj
        else:
            if current_avg < closest_avg:
                closest = current_obj
                closest_avg = current_avg
                closest_obj = obj
    distance_1 = coords_to_distance(origin_obj.get_pos(), closest_obj.get_pos())
    within_max = True if distance_1 <= max_dist else False
    return closest_obj.id, distance_1, within_max, closest_avg


def coords_to_distance(point1: list, point2: list, meters=True):
    # TODO need to go through this function again, hasn't been checked since transform updates have been fixes (and accuracy has never been tested)
    if not meters:
        raise NotImplemented
    all_points = point1 + point2
    for p in all_points:
        if p == None:
            raise ValueError(
                f"None in coords_to_distance point list: {point1=} {point2=}"
            )
        if not (isinstance(p, float) or isinstance(p, int)):
            raise ValueError(
                f"Non-INT in coords_to_distance point list: {point1=} {point2=}"
            )

    lat1, long1, alt1 = point1
    lat2, long2, alt2 = point2
    # https://www.geeksforgeeks.org/program-distance-two-points-earth/
    # The math module contains a function named
    # radians which converts from degrees to radians.
    long1_rad = radians(long1)
    long2_rad = radians(long2)
    lat1_rad = radians(lat1)
    lat2_rad = radians(lat2)
    # Haversine formula
    dlon = long2_rad - long1_rad
    dlat = lat2_rad - lat1_rad
    a = sin(dlat / 2) ** 2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    # Radius of earth in kilometres. Use 3956 for miles
    r = 6371

    meter_xz_axis = (c * r) / 1000
    meter_y_axis = abs(alt1 - alt2)

    distance = sqrt(meter_xz_axis**2 + meter_y_axis**2)

    return distance


def is_unit(obj_data, ignore_types=[], ground=True, air=True):
    unit_types = ["Air", "Ground", "Sea"]
    non_units = [
        "Decoy",
        "Flare",
        "Shrapnel",
        "Weapon",
        "Projectile",
        "Shell",
        "Parachutist",
        "Building",
        "Navaid",
        "Bullseye",
        "Container",
    ]
    for type in ignore_types:
        non_units.append(type)  # TODO add checks here
    for non_unit_type in non_units:
        if non_unit_type in obj_data.type:
            return False
    return True


# def is_float(string:str) -> bool:
# 	try:
# 		float(string)
# 		return True
# 	except ValueError:
# 		return False


if __name__ == "__main__":
    test_str = "1102,T=1.421312|5.9462587||-478516.88|97803.12"
    print(attr_split(test_str))
    test_str = "1402,T=5.3188736|5.2597919|9.93|-1.2|-1.6|133.2|-92130.2|10611.6|134,Type=Ground+AntiAircraft,Name=S-300PS 54K6 cp,Pilot=Ground-6-3,Group=Ground-6,Color=Red,Coalition=Allies,Country=ru"
    print(attr_split(test_str))
