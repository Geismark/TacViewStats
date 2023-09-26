# https://www.tacview.net/documentation/acmi/en/
# T = Longitude | Latitude | Altitude
# T = Longitude | Latitude | Altitude | U | V
# T = Longitude | Latitude | Altitude | Roll | Pitch | Yaw
# T = Longitude | Latitude | Altitude | Roll | Pitch | Yaw | U | V | Heading

# emailed the TacView team, they use 3D pythagorean theorem to calculate distance using U,V,Alt

# ======================================== NOTE ========================================
# This file is a complete mess - please ignore for now, will be completed in the future
# ======================================== NOTE ========================================


from src.managers.logHandler import logger
from math import radians, cos, sin, asin, sqrt
from src.classes.DCSObject import DCSObject
from src.data.valueReferences import closest_obj_alt_division


def get_closest_obj(obj: DCSObject, other_objs: list) -> tuple[DCSObject, float]:
    if not isinstance(obj, DCSObject):
        raise TypeError(f"Reference object is not DCSObject: {type(obj)=}")
    if not isinstance(other_objs, list):
        raise TypeError(f"other_objs is not list: {type(other_objs)=} {other_objs=}")
    if obj.check_is_dead():
        logger.warning(f"Trying to get closest obj of dead obj: {obj.info(all=True)}")
        return None, None
    if len(other_objs) <= 1:
        logger.trace(f"len(other_objs) <= 1: {len(other_objs)=}")
        return None, None
    closest_obj = None
    closest_dist = None
    if obj.check_is_alive():
        obj_pos = obj.get_pos()
    elif obj.check_is_dying() or obj.check_is_dead():
        obj_pos = obj.get_death_pos()
    else:
        raise ValueError(
            f"closest_obj reference object is not alive/dying: {obj.id=} {obj.state=} {obj.name=} {obj.type=}"
        )
    for other in other_objs:
        if other == obj:
            continue
        elif not isinstance(other, DCSObject):
            raise TypeError(
                f"Comparison object is not DCSObject: {other.id=} {type(obj)=}"
            )
        elif other.check_is_dead():
            continue
        if other.check_is_alive():
            other_pos = other.get_pos()
        elif other.check_is_dying():
            other_pos = other.get_death_pos()
        else:
            raise ValueError(
                f"Invalid comparison object state: {other.id=} {other.state=} {other.name=} {other.type=}"
            )
        current_dist_list = [
            abs(obj_pos[0] - other_pos[0]),
            abs(obj_pos[1] - other_pos[1]),
            abs(obj_pos[2] - other_pos[2])
            / closest_obj_alt_division,  # FUTUREDO find appropriate alt division value, OR change to euclidean/haversine
        ]
        avg_dist = sum(current_dist_list)
        if closest_dist is None or avg_dist < closest_dist:
            closest_obj = other
            closest_dist = avg_dist
    return closest_obj, closest_dist


def coords_to_euclidean_distance(point1: list, point2: list, distance_unit="nm"):
    """Not currently implemented/working as intended - will be revisited"""
    # euclidean - accuracy with midpoint?: https://math.stackexchange.com/a/29162
    # euclidean: https://math.stackexchange.com/a/29162
    """From [lat, long, alt]x2 -> euclidean (3d straight line) distance"""
    distance_unit = distance_unit.lower()
    # TODO need to go through this function again, hasn't been checked since transform updates have been fixes (and accuracy has never been tested)
    for p in point1 + point2:
        if p in [None, ""]:
            raise ValueError(
                f"None or '' in coords_to_distance point list:\n\t{point1=} {point2=}"
            )
        if not (isinstance(p, float) or isinstance(p, int)):
            raise ValueError(
                f"Non-INT in coords_to_great_circle_distance point list:\n\t{point1=} {point2=}"
            )
    # Radius of earth in kilometres (6371). Use 3956 for miles
    r = 6371

    lat1, long1, alt1 = point1
    lat2, long2, alt2 = point2

    lat1_rad, long1_rad, lat2_rad, long2_rad = map(radians, [lat1, long1, lat2, long2])

    # euclidean: https://math.stackexchange.com/a/29162
    cx1, cy1, cz1 = [
        r * cos(lat1_rad) * cos(long1_rad),
        r * cos(lat1_rad) * sin(long1_rad),
        r * sin(lat1_rad),
    ]
    cx2, cy2, cz2 = [
        r * cos(lat2_rad) * cos(long2_rad),
        r * cos(lat2_rad) * sin(long2_rad),
        r * sin(lat2_rad),
    ]
    cartesian_distance = sqrt(
        (cx2 - cx1) ** 2 + (cy2 - cy1) ** 2 + (cz2 - cz1) ** 2
    )  # km
    distance = sqrt(cartesian_distance**2 + ((alt2 - alt1) / 1000) ** 2)

    # convert to desired distance (default=nm) from kilometre
    if distance_unit in ["nautical mile", "nautical miles", "nm", "nmi"]:
        convert_units_ratio = 0.539957
    elif distance_unit in ["kilometres", "kilometre", "km"]:
        convert_units_ratio = 1
    elif distance_unit in ["mile", "miles", "mi"]:
        convert_units_ratio = 0.621371
    elif distance_unit in ["meter", "meters", "m"]:
        convert_units_ratio = 1_000
    elif distance_unit in ["feet", "ft"]:
        convert_units_ratio = 3280.84
    else:
        raise ValueError(f"{distance_unit=}")
    return distance * convert_units_ratio


def coords_to_haversine_distance(point1: list, point2: list, distance_unit="nm"):
    # info: www.movable-type.co.uk/scripts/latlong.html   &&   www.movable-type.co.uk/scripts/geodesy-library.html#latlon-spherical
    # code0: https://www.geeksforgeeks.org/program-distance-two-points-earth/
    # code1:https://stackoverflow.com/a/15737218
    # optimise: https://stackoverflow.com/a/21623206

    """Not currently implemented/working as intended - will be revisited"""
    """From [lat, long, alt]x2 -> Haversine (curved across 3d sphere) distance"""
    distance_unit = distance_unit.lower()
    # TODO need to go through this function again, hasn't been checked since transform updates have been fixes (and accuracy has never been tested)
    for p in point1 + point2:
        if p in [None, ""]:
            raise ValueError(
                f"None in coords_to_distance point list:\n\t{point1=} {point2=}"
            )
        if not (isinstance(p, float) or isinstance(p, int)):
            raise ValueError(
                f"Non-INT in coords_to_great_circle_distance point list:\n\t{point1=} {point2=}"
            )

    # code: https://www.geeksforgeeks.org/program-distance-two-points-earth/
    lat1, long1, alt1 = point1
    lat2, long2, alt2 = point2
    # math.radians converts from decimal degrees to radians.
    lat1_rad, long1_rad, lat2_rad, long2_rad = map(radians, [lat1, long1, lat2, long2])
    # Haversine formula
    dlon = long2_rad - long1_rad
    dlat = lat2_rad - lat1_rad
    a = sin(dlat / 2) ** 2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    # Radius of earth in kilometres (6371). Use 3956 for miles
    r = 6371

    meter_xz_axis = c * r
    meter_y_axis = abs(alt1 - alt2) / 1_000  # alt stored as meters MSL

    distance = sqrt(meter_xz_axis**2 + meter_y_axis**2)

    # convert to desired distance (default=nm) from kilometre
    if distance_unit in ["nautical mile", "nautical miles", "nm", "nmi"]:
        convert_units = 0.539957
    elif distance_unit in ["kilometres", "kilometre", "km"]:
        convert_units = 1
    elif distance_unit in ["mile", "miles", "mi"]:
        convert_units = 0.621371
    elif distance_unit in ["meter", "meters", "m"]:
        convert_units = 1_000
    elif distance_unit in ["feet", "ft"]:
        convert_units = 3280.84
    else:
        raise ValueError(f"{distance_unit=}")
    # print(f"{point1=}\n{point2=}")
    return distance * convert_units


def coords_to_haversine_distance_updated(
    point1: list, point2: list, distance_unit="nm"
):
    # info: www.movable-type.co.uk/scripts/latlong.html   &&   www.movable-type.co.uk/scripts/geodesy-library.html#latlon-spherical
    # code0: https://www.geeksforgeeks.org/program-distance-two-points-earth/
    # code1:https://stackoverflow.com/a/15737218
    # optimise: https://stackoverflow.com/a/21623206
    # UPDATED: https://www.omnicalculator.com/other/latitude-longitude-distance#obtaining-the-distance-between-two-points-on-earth-distance-between-coordinates

    """Not currently implemented/working as intended - will be revisited"""
    """From [lat, long, alt] points to Haversine (curved across 3d sphere) distance"""
    distance_unit = distance_unit.lower()
    for p in point1 + point2:
        if p in [None, ""]:
            raise ValueError(
                f"None in coords_to_distance point list:\n\t{point1=} {point2=}"
            )
        if not (isinstance(p, float) or isinstance(p, int)):
            raise ValueError(
                f"Non-INT in coords_to_great_circle_distance point list:\n\t{point1=} {point2=}"
            )

    # code: https://www.geeksforgeeks.org/program-distance-two-points-earth/
    lat1, long1, alt1 = point1
    lat2, long2, alt2 = point2
    # math.radians converts from decimal degrees to radians.
    lat1_rad, long1_rad, lat2_rad, long2_rad = map(radians, [lat1, long1, lat2, long2])
    # Radius of earth in kilometres (6371). Use 3956 for miles
    earth_radius = 6371  # km
    # Haversine formula
    lat_dif = abs(lat2_rad - lat1_rad)
    long_dif = abs(long2_rad - long1_rad)
    xz_stage1 = (
        sin((lat_dif) / 2) ** 2
        + cos(lat1_rad) * cos(lat2_rad) * sin((long_dif) / 2) ** 2
    )
    xz_distance = 2 * earth_radius * asin(sqrt(xz_stage1))

    y_distance = abs(alt1 - alt2) / 1_000  # alt stored as meters MSL

    distance = sqrt(xz_distance**2 + y_distance**2)

    # convert to desired distance (default=nm) from kilometre
    if distance_unit in ["nautical mile", "nautical miles", "nm", "nmi"]:
        convert_units = 0.539957
    elif distance_unit in ["kilometres", "kilometre", "km"]:
        convert_units = 1
    elif distance_unit in ["mile", "miles", "mi"]:
        convert_units = 0.621371
    elif distance_unit in ["meter", "meters", "m"]:
        convert_units = 1_000
    elif distance_unit in ["feet", "ft"]:
        convert_units = 3280.84
    else:
        raise ValueError(f"{distance_unit=}")
    return distance * convert_units


def coords_to_distance(position1, position2, output_unit="nm"):
    # takes [U,V,alt] and returns distance in meters
    meter_distance = sqrt(
        (position2[0] - position1[0]) ** 2
        + (position2[1] - position1[1]) ** 2
        + (position2[2] - position1[2]) ** 2
    )
    distance = meters_to_unit(meter_distance, output_unit)
    return distance


def objs_to_distance(obj1, obj2, output_unit="nm"):
    meter_distance = sqrt(
        (obj2.u - obj1.u) ** 2 + (obj2.v - obj1.v) ** 2 + (obj2.alt - obj1.alt) ** 2
    )
    distance = meters_to_unit(meter_distance, output_unit)
    return distance


def meters_to_unit(meters: float, unit: str):
    if unit in ["nautical mile", "nautical miles", "nm", "nmi"]:
        convert_units = 0.000539957
    elif unit in ["kilometres", "kilometre", "km"]:
        convert_units = 0.001
    elif unit in ["mile", "miles", "mi"]:
        convert_units = 0.000621371
    elif unit in ["meter", "meters", "m"]:
        convert_units = 1
    elif unit in ["feet", "ft"]:
        convert_units = 3.28084
    else:
        raise ValueError(f"{unit=}")
    return meters * convert_units


if __name__ == "__main__":
    units = ["nm", "km", "mi", "m", "ft"]
    unit = "nm"

# Distance Brody=><=A_380 279.90
# 12203,T=4.8420852|6.5974405|2969.81|-18.3|1.2|298.6|-133230.23|381191.19|299.7,Type=Air+FixedWing,Color=Blue,Coalition=Enemies,Name=F-14A-135-GR,Country=xb,Pilot=Brody,Group=80's F-14A,Importance=1,IAS=246.3,AOA=1.3,Flaps=0,LandingGear=0,HDM=296.7,PilotHeadRoll=5.24,PilotHeadPitch=13.22,PilotHeadYaw=-25.93,AOAUnits=4.85
# fe02,T=1.4663775|3.0186413|10058.4||4.1|177.5|-478482.09|-5420.09|180,Type=Air+FixedWing,Color=Red,Coalition=Allies,Name=A_380,Country=xr,Pilot=A380,Group=A380
