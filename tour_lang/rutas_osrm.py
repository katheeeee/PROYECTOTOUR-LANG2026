"""
Motor Híbrido de Enrutamiento Real: OSRM + Valhalla (FOSSGIS) con Fallback Automático.
- Vehicular (BUS, AUTO, MINIVAN): OSRM (Contraction Hierarchies) con respaldo Valhalla.
- Peatonal / Ciclismo (CAMINATA, BICICLETA): Valhalla (A* multimodal) con respaldo OSRM.
- Lacustre (LANCHA, BOTE o Islas del Lago Titicaca): Trazado acuático punteado.
"""

from typing import Any, Dict, List
import requests

ISLAS_TITICACA = {"UROS", "ISLAS UROS", "TAQUILE", "AMANTANI"}


def es_tramo_lacustre(nombre_a: str, nombre_b: str, transporte: str = "") -> bool:
    a = nombre_a.strip().upper()
    b = nombre_b.strip().upper()
    t = transporte.strip().upper()
    if t in ("LANCHA", "BOTE"):
        return True
    return any(isla in a or isla in b for isla in ISLAS_TITICACA)


def _decodificar_polyline6(encoded: str) -> List[List[float]]:
    """Decodifica formato Polyline6 de Valhalla (precisión 1e6) a [[lat, lon], ...]."""
    coords: List[List[float]] = []
    index = 0
    lat = 0
    lon = 0
    length = len(encoded)
    while index < length:
        for is_lon in (False, True):
            shift = 0
            result = 0
            while True:
                b = ord(encoded[index]) - 63
                index += 1
                result |= (b & 0x1F) << shift
                shift += 5
                if b < 0x20:
                    break
            delta = ~(result >> 1) if (result & 1) else (result >> 1)
            if is_lon:
                lon += delta
            else:
                lat += delta
        coords.append([lat / 1e6, lon / 1e6])
    return coords


def consultar_tramo_osrm(
    lat1: float, lon1: float, lat2: float, lon2: float, timeout: float = 4.5
) -> Dict[str, Any]:
    """Consulta la carretera real mediante OSRM (perfil driving)."""
    url = (
        f"https://router.project-osrm.org/route/v1/driving/"
        f"{lon1:.6f},{lat1:.6f};{lon2:.6f},{lat2:.6f}"
        f"?overview=full&geometries=geojson"
    )
    try:
        resp = requests.get(url, timeout=timeout, headers={"User-Agent": "TOUR-LANG-UNAP/2026"})
        if resp.status_code == 200:
            data = resp.json()
            if data.get("code") == "Ok" and data.get("routes"):
                ruta = data["routes"][0]
                coords_lonlat = ruta["geometry"]["coordinates"]
                coords_latlon = [[c[1], c[0]] for c in coords_lonlat]
                return {
                    "ok": True,
                    "motor": "OSRM",
                    "tipo": "carretera",
                    "coords": coords_latlon,
                    "distancia_km": round(ruta.get("distance", 0.0) / 1000.0, 2),
                    "duracion_min": round(ruta.get("duration", 0.0) / 60.0, 1),
                }
    except Exception:
        pass
    return {"ok": False}


def consultar_tramo_valhalla(
    lat1: float,
    lon1: float,
    lat2: float,
    lon2: float,
    costing: str = "auto",
    timeout: float = 5.5,
) -> Dict[str, Any]:
    """Consulta ruta multimodal mediante Valhalla FOSSGIS (auto, pedestrian, bicycle)."""
    url = "https://valhalla1.openstreetmap.de/route"
    payload = {
        "locations": [
            {"lat": lat1, "lon": lon1},
            {"lat": lat2, "lon": lon2},
        ],
        "costing": costing,
        "units": "kilometers",
        "language": "es-ES",
    }
    try:
        resp = requests.post(
            url,
            json=payload,
            timeout=timeout,
            headers={"User-Agent": "TOUR-LANG-UNAP/2026", "Content-Type": "application/json"},
        )
        if resp.status_code == 200:
            data = resp.json()
            trip = data.get("trip", {})
            legs = trip.get("legs", [])
            if legs and legs[0].get("shape"):
                coords_latlon = _decodificar_polyline6(legs[0]["shape"])
                summary = trip.get("summary", {})
                return {
                    "ok": True,
                    "motor": f"Valhalla ({costing})",
                    "tipo": "carretera",
                    "coords": coords_latlon,
                    "distancia_km": round(float(summary.get("length", 0.0)), 2),
                    "duracion_min": round(float(summary.get("time", 0.0)) / 60.0, 1),
                }
    except Exception:
        pass
    return {"ok": False}


def construir_geometria_ruta(puntos: List[Dict[str, Any]], transporte_global: str = "") -> Dict[str, Any]:
    """
    Selecciona automáticamente el motor óptimo según TRANSPORTE:
    - CAMINATA / BICICLETA -> Valhalla (pedestrian / bicycle), con respaldo OSRM.
    - BUS / AUTO / MINIVAN / default -> OSRM (driving), con respaldo Valhalla (auto).
    - LANCHA / BOTE / Islas Titicaca -> Tramo lacustre punteado.
    """
    transp_u = transporte_global.strip().upper()
    segmentos = []
    distancia_total_km = 0.0
    duracion_total_min = 0.0
    motores_usados = set()

    for i in range(len(puntos) - 1):
        p1 = puntos[i]
        p2 = puntos[i + 1]

        if es_tramo_lacustre(p1["nombre"], p2["nombre"], transp_u):
            seg = {
                "desde": p1["nombre"],
                "hacia": p2["nombre"],
                "tipo": "lacustre",
                "motor": "Lacustre",
                "coords": [[p1["lat"], p1["lon"]], [p2["lat"], p2["lon"]]],
                "distancia_km": 0.0,
                "duracion_min": 0.0,
            }
            segmentos.append(seg)
            continue

        if transp_u == "CAMINATA":
            res = consultar_tramo_valhalla(p1["lat"], p1["lon"], p2["lat"], p2["lon"], "pedestrian")
            if not res.get("ok"):
                res = consultar_tramo_osrm(p1["lat"], p1["lon"], p2["lat"], p2["lon"])
        elif transp_u == "BICICLETA":
            res = consultar_tramo_valhalla(p1["lat"], p1["lon"], p2["lat"], p2["lon"], "bicycle")
            if not res.get("ok"):
                res = consultar_tramo_osrm(p1["lat"], p1["lon"], p2["lat"], p2["lon"])
        else:
            res = consultar_tramo_osrm(p1["lat"], p1["lon"], p2["lat"], p2["lon"])
            if not res.get("ok"):
                res = consultar_tramo_valhalla(p1["lat"], p1["lon"], p2["lat"], p2["lon"], "auto")

        if res.get("ok"):
            motores_usados.add(res["motor"])
            seg = {
                "desde": p1["nombre"],
                "hacia": p2["nombre"],
                "tipo": res["tipo"],
                "motor": res["motor"],
                "coords": res["coords"],
                "distancia_km": res["distancia_km"],
                "duracion_min": res["duracion_min"],
            }
            distancia_total_km += res["distancia_km"]
            duracion_total_min += res["duracion_min"]
        else:
            seg = {
                "desde": p1["nombre"],
                "hacia": p2["nombre"],
                "tipo": "directo",
                "motor": "Directo",
                "coords": [[p1["lat"], p1["lon"]], [p2["lat"], p2["lon"]]],
                "distancia_km": 0.0,
                "duracion_min": 0.0,
            }
        segmentos.append(seg)

    motor_resumen = " + ".join(sorted(motores_usados)) if motores_usados else "Lacustre / Directo"
    return {
        "segmentos": segmentos,
        "distancia_osrm_km": round(distancia_total_km, 2),
        "duracion_osrm_min": round(duracion_total_min, 1),
        "osrm_activo": len(motores_usados) > 0,
        "motor_activo": motor_resumen,
    }


def exportar_geojson(nombre_ruta: str, puntos: List[Dict[str, Any]], geom: Dict[str, Any]) -> Dict[str, Any]:
    features = []
    for p in puntos:
        features.append({
            "type": "Feature",
            "properties": {
                "orden": p["orden"],
                "nombre": p["nombre"],
                "rol": p["rol"],
                "tipo": p["tipo"],
                "descripcion": p["descripcion"],
            },
            "geometry": {
                "type": "Point",
                "coordinates": [p["lon"], p["lat"]],
            },
        })

    for seg in geom["segmentos"]:
        features.append({
            "type": "Feature",
            "properties": {
                "ruta": nombre_ruta,
                "desde": seg["desde"],
                "hacia": seg["hacia"],
                "modo": seg["tipo"],
                "motor": seg.get("motor", "OSRM"),
                "distancia_km": seg["distancia_km"],
                "duracion_min": seg["duracion_min"],
            },
            "geometry": {
                "type": "LineString",
                "coordinates": [[c[1], c[0]] for c in seg["coords"]],
            },
        })

    return {"type": "FeatureCollection", "features": features}
