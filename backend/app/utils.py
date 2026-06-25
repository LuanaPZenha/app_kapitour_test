from math import asin, cos, radians, sin, sqrt

EARTH_RADIUS_M = 6_371_000

# Raio padrao (em metros) para validar proximidade de um check-in.
DEFAULT_CHECKIN_RADIUS_M = 150


def haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Distancia em metros entre duas coordenadas (formula de Haversine)."""
    r_lat1, r_lat2 = radians(lat1), radians(lat2)
    d_lat = radians(lat2 - lat1)
    d_lon = radians(lon2 - lon1)
    a = sin(d_lat / 2) ** 2 + cos(r_lat1) * cos(r_lat2) * sin(d_lon / 2) ** 2
    return 2 * EARTH_RADIUS_M * asin(sqrt(a))
