"""
Convierte un archivo Excel (.xlsx) de hoteles de Puno en prueba_imagenes/hoteles_puno.json.
Uso:
    python convertir_hoteles.py [ruta_al_excel.xlsx]
"""

import json
import sys
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
SALIDA_JSON = BASE_DIR / "hoteles_puno.json"

# Rango geográfico válido de la región Puno
PUNO_LAT_MIN, PUNO_LAT_MAX = -17.5, -13.0
PUNO_LON_MIN, PUNO_LON_MAX = -71.5, -68.5


def _buscar_columna(columnas: list[str], candidatas: tuple[str, ...]) -> str | None:
    mapa = {str(c).strip().lower(): c for c in columnas}
    for cand in candidatas:
        if cand in mapa:
            return mapa[cand]
    for col_lower, col_orig in mapa.items():
        if any(cand in col_lower for cand in candidatas):
            return col_orig
    return None


def convertir_excel_a_json(ruta_excel: Path) -> None:
    if not ruta_excel.exists():
        print(f"[ERROR] No se encontró el archivo Excel: {ruta_excel}")
        sys.exit(1)

    df = pd.read_excel(ruta_excel, engine="openpyxl")
    columnas = list(df.columns)

    col_nombre = _buscar_columna(columnas, ("nombre", "hotel", "lugar", "name"))
    col_lat = _buscar_columna(columnas, ("latitud", "lat", "latitude"))
    col_lon = _buscar_columna(columnas, ("longitud", "lon", "lng", "longitude"))

    if not col_nombre or not col_lat or not col_lon:
        print(
            "[ERROR] El Excel debe contener columnas de nombre, latitud y longitud. "
            f"Columnas encontradas: {columnas}"
        )
        sys.exit(1)

    hoteles = []
    avisos = 0

    for idx, fila in df.iterrows():
        num_fila = idx + 2  # +2 considerando encabezado en fila 1
        nombre_raw = fila[col_nombre]
        lat_raw = fila[col_lat]
        lon_raw = fila[col_lon]

        if pd.isna(nombre_raw) or not str(nombre_raw).strip():
            avisos += 1
            print(f"[AVISO] Fila {num_fila}: nombre vacío, se omite.")
            continue

        nombre = str(nombre_raw).strip()

        if pd.isna(lat_raw) or pd.isna(lon_raw):
            avisos += 1
            print(f"[AVISO] Fila {num_fila} ('{nombre}'): coordenadas vacías, se omite.")
            continue

        try:
            lat = float(str(lat_raw).replace(",", ".").strip())
            lon = float(str(lon_raw).replace(",", ".").strip())
        except ValueError:
            avisos += 1
            print(
                f"[AVISO] Fila {num_fila} ('{nombre}'): coordenadas no numéricas "
                f"({lat_raw}, {lon_raw}), se omite."
            )
            continue

        if not (-90.0 <= lat <= 90.0 and -180.0 <= lon <= 180.0):
            avisos += 1
            print(
                f"[AVISO] Fila {num_fila} ('{nombre}'): coordenadas globales fuera de rango "
                f"({lat}, {lon}), se omite."
            )
            continue

        if not (PUNO_LAT_MIN <= lat <= PUNO_LAT_MAX and PUNO_LON_MIN <= lon <= PUNO_LON_MAX):
            avisos += 1
            print(
                f"[AVISO] Fila {num_fila} ('{nombre}'): coordenadas ({lat}, {lon}) fuera de la región Puno "
                f"(lat [{PUNO_LAT_MIN}, {PUNO_LAT_MAX}], lon [{PUNO_LON_MIN}, {PUNO_LON_MAX}])."
            )

        hoteles.append({
            "nombre": nombre,
            "latitud": round(lat, 6),
            "longitud": round(lon, 6),
        })

    SALIDA_JSON.write_text(json.dumps(hoteles, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[OK] Se exportaron {len(hoteles)} hotel(es) a {SALIDA_JSON} ({avisos} aviso(s)).")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        excel_path = Path(sys.argv[1])
    else:
        excel_path = BASE_DIR / "hoteles_puno.xlsx"
        if not excel_path.exists():
            candidatos = list(BASE_DIR.glob("*.xlsx"))
            if candidatos:
                excel_path = candidatos[0]
    convertir_excel_a_json(excel_path)
