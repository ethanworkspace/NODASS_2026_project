from math import atan2, cos, radians, sin, degrees


def bearing_degrees(source_lon: float, source_lat: float, target_lon: float, target_lat: float) -> float:
    """Return initial bearing from source point to target point in degrees."""
    lon1 = radians(source_lon)
    lon2 = radians(target_lon)
    lat1 = radians(source_lat)
    lat2 = radians(target_lat)
    delta_lon = lon2 - lon1
    x = sin(delta_lon) * cos(lat2)
    y = cos(lat1) * sin(lat2) - sin(lat1) * cos(lat2) * cos(delta_lon)
    return (degrees(atan2(x, y)) + 360) % 360

