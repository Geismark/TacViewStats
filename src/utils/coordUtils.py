# https://www.tacview.net/documentation/acmi/en/
# T = Longitude | Latitude | Altitude
# T = Longitude | Latitude | Altitude | U | V
# T = Longitude | Latitude | Altitude | Roll | Pitch | Yaw
# T = Longitude | Latitude | Altitude | Roll | Pitch | Yaw | U | V | Heading

from src.managers.logHandler import logger
from math import radians, cos, sin, asin, sqrt
from src.classes.DCSObject import DCSObject


def get_closest_obj(obj: DCSObject, other_objs: list) -> tuple[DCSObject, float]:
    if not isinstance(obj, DCSObject):
        raise TypeError(f"Reference object is not DCSObject: {type(obj)=}")
    if not isinstance(other_objs, list):
        raise TypeError(f"other_objs is not list: {type(other_objs)=} {other_objs=}")
    if not obj.check_state():
        raise ValueError(
            f"Reference object is not alive/dying/dead: {obj.id=} {obj.state=}"
        )
    if obj.check_state("Dead"):
        logger.debug(f"Trying to get closest obj of dead obj: {obj.id=}")
        return None, None
    if len(other_objs) <= 1:
        logger.trace(f"len(other_objs) <= 1: {len(other_objs)=}")
        return None, None
    closest_obj = None
    closest_dist = None
    if obj.check_state("Dying"):
        obj_pos = obj.get_death_pos()
    elif obj.check_state("Alive"):
        obj_pos = obj.get_pos()
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
        elif other.check_state("Dead"):
            continue
        if other.check_state("Alive"):
            other_pos = other.get_pos()
        elif other.check_state("Dying"):
            other_pos = other.get_death_pos()
        else:
            raise ValueError(
                f"Invalid comparison object state: {other.id=} {other.state=} {other.name=} {other.type=}"
            )
        current_dist_list = [
            abs(obj_pos[0] - other_pos[0]),
            abs(obj_pos[1] - other_pos[1]),
            abs(obj_pos[2] - other_pos[2])
            / 1_000,  # FUTUREDO find appropriate alt division value, OR change to euclidean/haversine
        ]
        avg_dist = sum(current_dist_list)
        if closest_dist is None or avg_dist < closest_dist:
            closest_obj = other
            closest_dist = avg_dist
    return closest_obj, closest_dist


def coords_to_euclidean_distance(point1: list, point2: list, distance_unit="nm"):
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


if __name__ == "__main__":
    units = ["nm", "km", "mi", "m", "ft"]
    unit = "nm"

    # p1 = [29.4973704, 54.8285196, 4869.91]
    # p2 = [25.9652969, 51.4766983, 10058.56]
    # TV_shown = 277.01  # nm
    # print(f'"E - {unit}": {coords_to_euclidean_distance(p1, p2, unit)},')
    # print(f'"H - {unit}": {coords_to_haversine_distance(p1, p2, unit)},')
    # print(f'"U - {unit}": {coords_to_haversine_distance_updated(p1, p2, unit)},')
    # print(f"{TV_shown = }\n")
    p1 = [44.1756191, 37.8692512, 0]
    p2 = [44.4734395, 39.7265547, 9801.65]
    TV_shown = 82.32  # nm
    print(f'"E - {unit}": {coords_to_euclidean_distance(p1, p2, unit)},')
    print(f'"H - {unit}": {coords_to_haversine_distance(p1, p2, unit)},')
    print(f'"U - {unit}": {coords_to_haversine_distance_updated(p1, p2, unit)},')
    print(f"{TV_shown = }\n")
    p1 = [44.2305133, 37.2661646, 0]
    p2 = [44.498904, 37.1760557, 0]
    TV_shown = 16.58  # nm
    print(f'"E - {unit}": {coords_to_euclidean_distance(p1, p2, unit)},')
    print(f'"H - {unit}": {coords_to_haversine_distance(p1, p2, unit)},')
    print(f'"U - {unit}": {coords_to_haversine_distance_updated(p1, p2, unit)},')
    print(f"{TV_shown = }\n")
    # p1 = [p1[0] + ReferenceLatitude, p1[1] + ReferenceLongitude, p1[2]]
    # p2 = [p2[0] + ReferenceLatitude, p2[1] + ReferenceLongitude, p2[2]]
    # for unit in units:
    #     print(f'"E - {unit}": {coords_to_euclidean_distance(p1, p2, unit)},')
    #     print(f'"H - {unit}": {coords_to_haversine_distance(p1, p2, unit)},')
    p1 = [44.498904, 37.1760557, 0]
    p2 = [42.774945, 40.5869716, 0]
    TV_shown = 181.49
    print(f'"E - {unit}": {coords_to_euclidean_distance(p1, p2, unit)},')
    print(f'"H - {unit}": {coords_to_haversine_distance(p1, p2, unit)},')
    print(f'"U - {unit}": {coords_to_haversine_distance_updated(p1, p2, unit)},')
    print(f"{TV_shown = }\n")
    p1 = [44.498904, 37.1760557, 0]
    p2 = [45.5450485, 40.5079512, 7620.42]
    TV_shown = 155.46
    print(f'"E - {unit}": {coords_to_euclidean_distance(p1, p2, unit)},')
    print(f'"H - {unit}": {coords_to_haversine_distance(p1, p2, unit)},')
    print(f'"U - {unit}": {coords_to_haversine_distance_updated(p1, p2, unit)},')
    print(f"{TV_shown = }\n")


# https://www.tacview.net/documentation/acmi/en/
# T = Longitude | Latitude | Altitude
# T = Longitude | Latitude | Altitude | U | V
# T = Longitude | Latitude | Altitude | Roll | Pitch | Yaw
# T = Longitude | Latitude | Altitude | Roll | Pitch | Yaw | U | V | Heading


# 0,ReferenceLongitude=34
# 0,ReferenceLatitude=40

# TV_shown = 181.49 #nm
# LHA-1 [44.498904, 37.1760557, 0]
# a02,T=3.1760557|4.498904|-0.03
# Admiral Kuznetsov [42.774945, 40.5869716, 0]
# 802,T=6.5869716|2.774945|0.03

# TV_shown = 155.46 #nm
# LHA-1 [44.498904, 37.1760557, 0]
# a02,T=3.1760557|4.498904|-0.03
# A-50 [45.5450485, 40.5079512, 7620.42]
# 36d02,T=6.5079512|5.5450485|7620.42
