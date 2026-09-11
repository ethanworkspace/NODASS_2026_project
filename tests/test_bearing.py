from src.geospatial.bearing import bearing_degrees


def test_bearing_eastward() -> None:
    assert 80 <= bearing_degrees(120.0, 22.0, 121.0, 22.0) <= 100

