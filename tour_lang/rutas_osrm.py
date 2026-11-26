"""
Módulo de enrutamiento real por carreteras usando OSRM (Open Source Routing Machine)
con soporte de tramos lacustres (Lago Titicaca) y exportación a GeoJSON.
"""

from typing import Any, Dict, List, Tuple
import requests

ISLAS_TITICACA = {"UROS", "ISLAS UROS", "TAQUILE", "AMANTANI"}


def es_tramo_lacustre(nombre_a: str, nombre_b: str, transporte: str = "") -> bool:
    a = nombre_a.strip().upper()
    b = nombre_b.strip().upper()
    t = transporte.strip().upper()
    if t in ("LANCHA", "BOTE"):
        return True
    return any(isla in a or isla in b for isla in ISLAS_TITICACA)


def consultar_tramo_osrm(
    lat1: float, lon1: float, lat2: float, lon2: float, timeout: float = 4.5
) -> Dict[str, Any]:
    """
    Consulta la ruta real por carretera entre (lat1, lon1) y (lat2, lon2)
    mediante el servidor público OSRM. Devuelve lista de [lat, lon], distancia_km y duracion_min.
    """
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
                    "tipo": "carretera",
                    "coords": coords_latlon,
                    "distancia_km": round(ruta.get("distance", 0.0) / 1000.0, 2),
                    "duracion_min": round(ruta.get("duration", 0.0) / 60.0, 1),
                }
    except Exception:
        pass

    return {
        "ok": False,
        "tipo": "directo",
        "coords": [[lat1, lon1], [lat2, lon2]],
        "distancia_km": 0.0,
        "duracion_min": 0.0,
    }


def construir_geometria_ruta(puntos: List[Dict[str, Any]], transporte_global: str = "") -> Dict[str, Any]:
    """Construye los segmentos reales (carretera OSRM o tramo lacustre) para toda la ruta."""
    segmentos = []
    distancia_total_km = 0.0
    duracion_total_min = 0.0
    tiene_osrm = False

    for i in range(len(puntos) - 1):
        p1 = puntos[i]
        p2 = puntos[i + 1]
        if es_tramo_lacustre(p1["nombre"], p2["nombre"], transporte_global):
            seg = {
                "desde": p1["nombre"],
                "hacia": p2["nombre"],
                "tipo": "lacustre",
                "coords": [[p1["lat"], p1["lon"]], [p2["lat"], p2["lon"]]],
                "distancia_km": 0.0,
                "duracion_min": 0.0,
            }
        else:
            res = consultar_tramo_osrm(p1["lat"], p1["lon"], p2["lat"], p2["lon"])
            if res["ok"]:
                tiene_osrm = True
            seg = {
                "desde": p1["nombre"],
                "hacia": p2["nombre"],
                "tipo": res["tipo"],
                "coords": res["coords"],
                "distancia_km": res["distancia_km"],
                "duracion_min": res["duracion_min"],
            }
            distancia_total_km += res["distancia_km"]
            duracion_total_min += res["duracion_min"]
        segmentos.append(seg)

    return {
        "segmentos": segmentos,
        "distancia_osrm_km": round(distancia_total_km, 2),
        "duracion_osrm_min": round(duracion_total_min, 1),
        "osrm_activo": tiene_osrm,
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
                "distancia_km": seg["distancia_km"],
                "duracion_min": seg["duracion_min"],
            },
            "geometry": {
                "type": "LineString",
                "coordinates": [[c[1], c[0]] for c in seg["coords"]],
            },
        })

    return {"type": "FeatureCollection", "features": features}
