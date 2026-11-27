"""
Plataforma Web Interactiva del Compilador Visual TOUR-LANG (UNA Puno - EPIS 2026-II)
Diseño pantalla dividida: Unidad de Compilación a la izquierda | Mapa Leaflet + OSRM a la derecha.
Ejecutar con: streamlit run app.py  (o doble clic en iniciar_web.bat / botón Play en VS Code)
"""

import base64
import json
import os
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

# Auto-arranque inteligente al presionar Play en VS Code (python app.py)
if __name__ == "__main__":
    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx
        if get_script_run_ctx() is None:
            sys.exit(subprocess.call([sys.executable, "-m", "streamlit", "run", os.path.abspath(__file__)]))
    except ImportError:
        pass

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from PIL import Image, UnidentifiedImageError

from tour_lang import AnalizadorSemantico, AnalizadorSintactico, TablaLexica
from tour_lang.ejemplos import EJERCICIOS_TOUR_LANG
from tour_lang.rutas_osrm import construir_geometria_ruta, exportar_geojson

st.set_page_config(
    page_title="TOUR-LANG | Compilador Visual de Rutas",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Estilos Dark IDE (inspirado en compilador visual profesional)
st.markdown(
    """
    <style>
    .stApp {
        background-color: #08111e;
        color: #e2e8f0;
    }
    section[data-testid="stSidebar"] {
        background-color: #0b1626;
        border-right: 1px solid #1e293b;
    }
    header[data-testid="stHeader"],
    div[data-testid="stToolbar"],
    div[data-testid="stDecoration"] {
        display: none !important;
        height: 0 !important;
    }
    .block-container {
        padding-top: 1.1rem !important;
        padding-bottom: 0.6rem !important;
        padding-left: 1.2rem !important;
        padding-right: 1.2rem !important;
        max-width: 100% !important;
    }
    button[kind="primary"] {
        background-color: #2563eb !important;
        border: 1px solid #3b82f6 !important;
        color: #ffffff !important;
    }
    button[kind="primary"]:hover {
        background-color: #1d4ed8 !important;
    }
    .topbar-brand {
        font-family: 'Consolas', 'Courier New', monospace;
        font-size: 1.05rem;
        font-weight: 800;
        color: #7dd3fc;
        letter-spacing: 0.08em;
        margin: 0;
        line-height: 1.1;
    }
    .topbar-sub {
        font-size: 0.68rem;
        color: #64748b;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        margin: 0;
    }
    .panel-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background-color: #0d1a2d;
        border: 1px solid #1e2f47;
        border-bottom: none;
        border-radius: 10px 10px 0 0;
        padding: 0.5rem 0.9rem;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.12em;
        color: #94a3b8;
        text-transform: uppercase;
    }
    .status-strip {
        background-color: #0b1626;
        border-left: 1px solid #1e2f47;
        border-right: 1px solid #1e2f47;
        padding: 0.45rem 0.9rem;
        display: flex;
        flex-wrap: wrap;
        gap: 0.45rem;
        align-items: center;
    }
    .pill-ok {
        background: rgba(16, 185, 129, 0.16);
        color: #34d399;
        border: 1px solid rgba(16, 185, 129, 0.35);
        padding: 0.16rem 0.55rem;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 700;
    }
    .pill-err {
        background: rgba(239, 68, 68, 0.18);
        color: #f87171;
        border: 1px solid rgba(239, 68, 68, 0.4);
        padding: 0.16rem 0.55rem;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 700;
    }
    .pill-info {
        background: rgba(56, 189, 248, 0.14);
        color: #7dd3fc;
        border: 1px solid rgba(56, 189, 248, 0.3);
        padding: 0.16rem 0.55rem;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 600;
        font-family: 'Consolas', monospace;
    }
    .pill-file {
        color: #64748b;
        font-size: 0.75rem;
        font-family: 'Consolas', monospace;
        margin-left: 0.3rem;
    }
    textarea {
        font-family: 'Consolas', 'Fira Code', monospace !important;
        font-size: 0.86rem !important;
        line-height: 1.48 !important;
        background-color: #0a1422 !important;
        color: #e2e8f0 !important;
        border: 1px solid #1e2f47 !important;
        border-radius: 0 0 10px 10px !important;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        background-color: #0b1626;
        padding: 0.35rem 0.6rem;
        border-left: 1px solid #1e2f47;
        border-right: 1px solid #1e2f47;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #112238;
        color: #94a3b8;
        border-radius: 6px;
        padding: 0.3rem 0.8rem;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1d4ed8 !important;
        color: #ffffff !important;
    }
    div[data-testid="stDownloadButton"] button, div[data-testid="stButton"] button {
        border-radius: 7px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(ttl=3600, show_spinner=False)
def obtener_geometria_cacheada(puntos_json: str, transporte_global: str):
    puntos_list = json.loads(puntos_json)
    return construir_geometria_ruta(puntos_list, transporte_global)


# =========================================================================
# GESTIÓN DE IMÁGENES LOCALES (ESTILO LATEX) PARA PARADAS Y MAPA PYDECK
# =========================================================================
EXTENSIONES_IMAGEN = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp"}
MIME_POR_EXT = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".webp": "image/webp",
    ".gif": "image/gif",
    ".bmp": "image/bmp",
}
BASE_PROYECTO = Path(__file__).resolve().parent
DIR_PRUEBA_IMG = BASE_PROYECTO / "prueba_imagenes"
DIR_IMAGENES_LUGARES = DIR_PRUEBA_IMG / "imagenes"
ARCHIVO_IMAGENES_JSON = DIR_PRUEBA_IMG / "imagenes.json"


def normalizar_nombre_imagen(texto: str) -> str:
    sin_acentos = "".join(
        c for c in unicodedata.normalize("NFKD", texto.strip().lower()) if not unicodedata.combining(c)
    )
    limpio = re.sub(r"[^a-z0-9]+", "_", sin_acentos).strip("_")
    return limpio or "imagen_lugar"


def cargar_registro_imagenes() -> list:
    if not ARCHIVO_IMAGENES_JSON.exists():
        return []
    try:
        datos = json.loads(ARCHIVO_IMAGENES_JSON.read_text(encoding="utf-8"))
        return datos if isinstance(datos, list) else []
    except (OSError, ValueError):
        return []


def guardar_registro_imagenes(registros: list) -> None:
    DIR_PRUEBA_IMG.mkdir(parents=True, exist_ok=True)
    ARCHIVO_IMAGENES_JSON.write_text(json.dumps(registros, ensure_ascii=False, indent=2), encoding="utf-8")


def buscar_foto_para_lugar(nombre_lugar: str) -> str:
    """Busca una foto en imagenes.json o prueba_imagenes/imagenes/ y devuelve Data URI base64."""
    slug = normalizar_nombre_imagen(nombre_lugar)
    if not slug:
        return ""
    ruta_encontrada = None
    registros = cargar_registro_imagenes()

    # 1. Coincidencia exacta en imagenes.json
    for reg in registros:
        reg_slug = str(reg.get("nombre_normalizado", "")).strip()
        reg_lugar = normalizar_nombre_imagen(str(reg.get("lugar", reg.get("nombre", ""))))
        if slug in (reg_slug, reg_lugar):
            cand = BASE_PROYECTO / str(reg.get("ruta", ""))
            if cand.exists() and cand.is_file():
                ruta_encontrada = cand
                break

    # 2. Coincidencia parcial en imagenes.json (ej. "uros" <-> "isla_uros")
    if ruta_encontrada is None and len(slug) >= 3:
        for reg in registros:
            reg_slug = str(reg.get("nombre_normalizado", "")).strip()
            reg_lugar = normalizar_nombre_imagen(str(reg.get("lugar", reg.get("nombre", ""))))
            if (reg_slug and (slug in reg_slug or reg_slug in slug)) or (
                reg_lugar and (slug in reg_lugar or reg_lugar in slug)
            ):
                cand = BASE_PROYECTO / str(reg.get("ruta", ""))
                if cand.exists() and cand.is_file():
                    ruta_encontrada = cand
                    break

    # 3. Coincidencia directa o parcial en prueba_imagenes/imagenes/
    if ruta_encontrada is None and DIR_IMAGENES_LUGARES.exists():
        for ext in EXTENSIONES_IMAGEN:
            cand = DIR_IMAGENES_LUGARES / f"{slug}{ext}"
            if cand.exists() and cand.is_file():
                ruta_encontrada = cand
                break
        if ruta_encontrada is None and len(slug) >= 3:
            for p_img in sorted(DIR_IMAGENES_LUGARES.iterdir()):
                if p_img.is_file() and p_img.suffix.lower() in EXTENSIONES_IMAGEN:
                    stem_slug = normalizar_nombre_imagen(p_img.stem)
                    if slug in stem_slug or stem_slug in slug:
                        ruta_encontrada = p_img
                        break

    if ruta_encontrada is None:
        return ""

    try:
        mime = MIME_POR_EXT.get(ruta_encontrada.suffix.lower(), "image/png")
        b64 = base64.b64encode(ruta_encontrada.read_bytes()).decode("ascii")
        return f"data:{mime};base64,{b64}"
    except OSError:
        return ""


def renderizar_mapa_leaflet(
    nombre_ruta: str,
    puntos: list,
    geom: dict,
    vista_inicial: str,
    globales: dict,
    mensajes_salida: list,
) -> str:
    """Genera el HTML interactivo de Leaflet + OSRM siguiendo exactamente la carretera."""
    datos_js = json.dumps(
        {
            "nombre": nombre_ruta,
            "puntos": puntos,
            "segmentos": geom["segmentos"],
            "osrm_activo": geom["osrm_activo"],
            "motor_activo": geom.get("motor_activo", "OSRM"),
            "dist_osrm": geom["distancia_osrm_km"],
            "dur_osrm": geom["duracion_osrm_min"],
            "vista": vista_inicial,
            "globales": globales,
            "mensajes": mensajes_salida,
        },
        ensure_ascii=False,
    )

    return f"""
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>
  html, body {{
    margin: 0; padding: 0; height: 100%; width: 100%;
    background: #0a1422; font-family: 'Segoe UI', system-ui, sans-serif;
    overflow: hidden;
  }}
  #map {{
    height: 100%; width: 100%;
    border-radius: 0 0 10px 10px;
  }}
  .status-badge {{
    position: absolute; top: 12px; left: 54px; z-index: 1000;
    background: rgba(11, 22, 38, 0.90); color: #94a3b8;
    border: 1px solid #1e3a5f; border-radius: 8px;
    padding: 5px 10px; font-size: 11px; font-family: Consolas, monospace;
    box-shadow: 0 4px 12px rgba(0,0,0,0.35);
  }}
  .status-badge b {{ color: #38bdf8; }}
  .msg-overlay {{
    position: absolute; bottom: 16px; left: 14px; z-index: 1000;
    max-width: 340px;
    display: flex; flex-direction: column; gap: 6px;
  }}
  .msg-card {{
    background: rgba(11, 22, 38, 0.93);
    border-left: 4px solid #38bdf8;
    color: #e2e8f0; padding: 8px 12px; border-radius: 8px;
    font-size: 12px; box-shadow: 0 6px 18px rgba(0,0,0,0.4);
  }}
  .msg-card.rec {{ border-left-color: #10b981; }}
  .marker-pin {{
    width: 28px; height: 28px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-weight: 800; font-size: 12px; color: #0b1626;
    border: 2.5px solid #ffffff;
    box-shadow: 0 3px 10px rgba(0,0,0,0.45);
  }}
  .pin-origen {{ background: #22c55e; color: #052e16; }}
  .pin-parada {{ background: #facc15; color: #422006; }}
  .pin-destino {{ background: #10b981; color: #052e16; }}

  /* Popup oscuro estilo tarjeta elegante como en la referencia */
  .leaflet-popup-content-wrapper {{
    background: #0d1a2d !important;
    color: #e2e8f0 !important;
    border: 1px solid #264166;
    border-radius: 12px !important;
    box-shadow: 0 10px 28px rgba(0,0,0,0.55) !important;
  }}
  .leaflet-popup-tip {{ background: #0d1a2d !important; }}
  .popup-box {{ width: 215px; padding: 2px; }}
  .popup-hero {{
    height: 78px; border-radius: 8px; margin-bottom: 8px;
    background: linear-gradient(135deg, #102a43 0%, #155e75 100%);
    display: flex; align-items: center; justify-content: center;
  }}
  .popup-circle {{
    width: 38px; height: 38px; border-radius: 50%;
    background: rgba(11, 22, 38, 0.78); color: #e2e8f0;
    border: 1px solid rgba(125,211,252,0.4);
    display: flex; align-items: center; justify-content: center;
    font-weight: 800; font-size: 16px;
  }}
  .popup-title {{ font-size: 13.5px; font-weight: 700; color: #7dd3fc; margin-bottom: 3px; }}
  .popup-tipo {{ font-size: 11px; font-weight: 700; color: #f8fafc; margin-bottom: 3px; }}
  .popup-desc {{ font-size: 11.5px; color: #cbd5e1; margin-bottom: 5px; line-height: 1.35; }}
  .popup-meta {{ font-size: 10.5px; color: #94a3b8; font-family: Consolas, monospace; }}
</style>
</head>
<body>
<div id="map"></div>
<div class="status-badge" id="statusBadge"></div>
<div class="msg-overlay" id="msgOverlay"></div>

<script>
const DATA = {datos_js};

const osmLayer = L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
  maxZoom: 19,
  attribution: '&copy; OpenStreetMap'
}});

const satLayer = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{{z}}/{{y}}/{{x}}', {{
  maxZoom: 18,
  attribution: '&copy; Esri World Imagery'
}});

const topoLayer = L.tileLayer('https://{{s}}.tile.opentopomap.org/{{z}}/{{x}}/{{y}}.png', {{
  maxZoom: 17,
  attribution: '&copy; OpenTopoMap'
}});

let capaInicial = osmLayer;
if (DATA.vista === "SATELITE") capaInicial = satLayer;

const map = L.map('map', {{
  center: [-15.8402, -70.0219],
  zoom: 10,
  layers: [capaInicial]
}});

L.control.layers({{
  "Mapa Carreteras (OSM)": osmLayer,
  "Vista Satelital": satLayer,
  "Relieve / Topográfico": topoLayer
}}, null, {{ position: 'topright' }}).addTo(map);

const bounds = [];

// 1. Dibujar carreteras reales (OSRM) o tramos lacustres (Lago Titicaca)
DATA.segmentos.forEach((seg) => {{
  if (!seg.coords || seg.coords.length < 2) return;
  seg.coords.forEach(c => bounds.push(c));

  if (seg.tipo === "lacustre") {{
    L.polyline(seg.coords, {{
      color: '#38bdf8',
      weight: 4,
      opacity: 0.9,
      dashArray: '8, 8'
    }}).bindTooltip(`🚤 Tramo lacustre: ${{seg.desde}} ➔ ${{seg.hacia}}`).addTo(map);
  }} else {{
    // Borde oscuro suave + línea azul brillante de carretera real
    L.polyline(seg.coords, {{
      color: '#0369a1',
      weight: 7,
      opacity: 0.45
    }}).addTo(map);

    const etiqueta = seg.distancia_km > 0
      ? `🛣️ Carretera OSRM: ${{seg.desde}} ➔ ${{seg.hacia}} (${{seg.distancia_km}} km · ~${{seg.duracion_min}} min)`
      : `🛣️ Tramo: ${{seg.desde}} ➔ ${{seg.hacia}}`;

    L.polyline(seg.coords, {{
      color: '#38bdf8',
      weight: 4.2,
      opacity: 0.95
    }}).bindTooltip(etiqueta).addTo(map);
  }}
}});

// 2. Dibujar marcadores numerados (1, 2, 3, 4...)
let primerPopupMarker = null;

DATA.puntos.forEach((p, idx) => {{
  bounds.push([p.lat, p.lon]);
  const cls = p.rol === "ORIGEN" ? "pin-origen" : (p.rol === "DESTINO" ? "pin-destino" : "pin-parada");
  const icon = L.divIcon({{
    className: '',
    html: `<div class="marker-pin ${{cls}}">${{p.orden}}</div>`,
    iconSize: [28, 28],
    iconAnchor: [14, 14]
  }});

  const inicial = (p.nombre || "R").trim().charAt(0).toUpperCase();
  const heroHtml = p.foto_uri
    ? `<div class="popup-hero" style="padding:0;overflow:hidden;"><img src="${{p.foto_uri}}" style="width:100%;height:100%;object-fit:cover;border-radius:8px;"/></div>`
    : `<div class="popup-hero"><div class="popup-circle">${{inicial}}</div></div>`;
  const popupHtml = `
    <div class="popup-box">
      ${{heroHtml}}
      <div class="popup-title">${{p.orden}}. ${{p.nombre}} (${{p.rol}})</div>
      <div class="popup-tipo">Tipo: ${{p.tipo}}</div>
      <div class="popup-desc">${{p.descripcion}}</div>
      <div class="popup-meta">
        ${{p.costo_txt ? 'Costo: ' + p.costo_txt + ' · ' : ''}}${{p.duracion_txt ? 'Duración: ' + p.duracion_txt + '<br/>' : ''}}
        ${{p.transporte_txt ? 'Transporte: ' + p.transporte_txt + '<br/>' : ''}}
        ${{p.clima ? p.clima + '<br/>' : ''}}
        Coords: [${{p.lat.toFixed(4)}}, ${{p.lon.toFixed(4)}}]<br/>
        Fuente: ${{p.fuente}}
      </div>
    </div>
  `;

  const mk = L.marker([p.lat, p.lon], {{ icon }}).addTo(map).bindPopup(popupHtml);
  mk.on('mouseover', function () {{ this.openPopup(); }});
  if (p.rol === "PARADA" && !primerPopupMarker) {{
    primerPopupMarker = mk;
  }}
}});

if (bounds.length > 0) {{
  map.fitBounds(bounds, {{ padding: [45, 45] }});
}}

// Abrir automáticamente el popup de la primera parada destacada
if (primerPopupMarker) {{
  setTimeout(() => primerPopupMarker.openPopup(), 350);
}}

// Badge superior de estado OSRM
const badge = document.getElementById("statusBadge");
if (DATA.osrm_activo) {{
  badge.innerHTML = `Leaflet + ${{DATA.motor_activo}} · <b>${{DATA.dist_osrm}} km reales</b> (~${{Math.round(DATA.dur_osrm)}} min)`;
}} else {{
  badge.innerHTML = `Leaflet listo · <b>Ruta lacustre / trazado directo</b>`;
}}

// Tarjetas flotantes de recomendaciones/mensajes condicionales
const msgBox = document.getElementById("msgOverlay");
DATA.mensajes.forEach(m => {{
  const div = document.createElement("div");
  div.className = "msg-card " + (m.tipo === "RECOMENDAR" ? "rec" : "");
  const pref = m.tipo === "RECOMENDAR" ? "★ RECOMENDACIÓN:" : "ℹ MENSAJE:";
  div.innerHTML = `<b>${{pref}}</b> ${{m.texto}}`;
  msgBox.appendChild(div);
}});
</script>
</body>
</html>
"""




def renderizar_mapa_3d_maplibre(
    nombre_ruta: str,
    puntos: list,
    geom: dict,
    globales: dict,
    mensajes_salida: list,
) -> str:
    """Genera el visor 3D real con MapLibre GL JS + Relieve DEM Terrarium del Altiplano + Vuelo 3D."""
    features_linea = []
    for seg in geom["segmentos"]:
        if len(seg["coords"]) < 2:
            continue
        features_linea.append({
            "type": "Feature",
            "properties": {
                "tipo": seg["tipo"],
                "desde": seg["desde"],
                "hacia": seg["hacia"],
                "distancia_km": seg["distancia_km"],
            },
            "geometry": {
                "type": "LineString",
                "coordinates": [[c[1], c[0]] for c in seg["coords"]],
            },
        })

    datos_js = json.dumps(
        {
            "nombre": nombre_ruta,
            "puntos": puntos,
            "geojson_rutas": {"type": "FeatureCollection", "features": features_linea},
            "osrm_activo": geom["osrm_activo"],
            "motor_activo": geom.get("motor_activo", "OSRM"),
            "dist_osrm": geom["distancia_osrm_km"],
            "dur_osrm": geom["duracion_osrm_min"],
            "mensajes": mensajes_salida,
        },
        ensure_ascii=False,
    )

    return f"""
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<link href="https://unpkg.com/maplibre-gl@4.7.1/dist/maplibre-gl.css" rel="stylesheet"/>
<script src="https://unpkg.com/maplibre-gl@4.7.1/dist/maplibre-gl.js"></script>
<style>
  html, body {{
    margin: 0; padding: 0; height: 100%; width: 100%;
    background: #08111e; font-family: 'Segoe UI', system-ui, sans-serif;
    overflow: hidden;
  }}
  #map3d {{
    height: 100%; width: 100%;
    border-radius: 0 0 10px 10px;
  }}
  .hud-top {{
    position: absolute; top: 12px; left: 12px; z-index: 10;
    display: flex; flex-wrap: wrap; gap: 6px; align-items: center;
  }}
  .status-badge {{
    background: rgba(11, 22, 38, 0.90); color: #cbd5e1;
    border: 1px solid #1e3a5f; border-radius: 8px;
    padding: 5px 10px; font-size: 11px; font-family: Consolas, monospace;
    box-shadow: 0 4px 12px rgba(0,0,0,0.4);
  }}
  .status-badge b {{ color: #38bdf8; }}
  .hud-btn {{
    background: rgba(15, 29, 50, 0.92); color: #e2e8f0;
    border: 1px solid #2563eb; border-radius: 7px;
    padding: 5px 10px; font-size: 11.5px; font-weight: 700;
    cursor: pointer; box-shadow: 0 4px 12px rgba(0,0,0,0.35);
    transition: all 0.15s ease;
  }}
  .hud-btn:hover {{ background: #2563eb; color: #ffffff; }}
  .hud-btn.active {{ background: #10b981; border-color: #34d399; color: #052e16; }}
  .msg-overlay {{
    position: absolute; bottom: 16px; left: 14px; z-index: 10;
    max-width: 340px; display: flex; flex-direction: column; gap: 6px;
  }}
  .msg-card {{
    background: rgba(11, 22, 38, 0.93);
    border-left: 4px solid #38bdf8;
    color: #e2e8f0; padding: 8px 12px; border-radius: 8px;
    font-size: 12px; box-shadow: 0 6px 18px rgba(0,0,0,0.45);
  }}
  .msg-card.rec {{ border-left-color: #10b981; }}
  .marker-pin {{
    width: 30px; height: 30px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-weight: 800; font-size: 12.5px; cursor: pointer;
    border: 2.5px solid #ffffff;
    box-shadow: 0 4px 14px rgba(0,0,0,0.55);
  }}
  .pin-origen {{ background: #22c55e; color: #052e16; }}
  .pin-parada {{ background: #facc15; color: #422006; }}
  .pin-destino {{ background: #10b981; color: #052e16; }}

  .maplibregl-popup-content {{
    background: #0d1a2d !important; color: #e2e8f0 !important;
    border: 1px solid #264166; border-radius: 12px !important;
    padding: 10px !important; box-shadow: 0 10px 28px rgba(0,0,0,0.6) !important;
  }}
  .maplibregl-popup-tip {{ border-top-color: #0d1a2d !important; }}
  .maplibregl-popup-close-button {{ color: #94a3b8; font-size: 16px; }}
  .popup-box {{ width: 215px; }}
  .popup-hero {{
    height: 68px; border-radius: 8px; margin-bottom: 8px;
    background: linear-gradient(135deg, #0f2942 0%, #0e7490 100%);
    display: flex; align-items: center; justify-content: center;
  }}
  .popup-circle {{
    width: 36px; height: 36px; border-radius: 50%;
    background: rgba(11, 22, 38, 0.8); color: #e2e8f0;
    border: 1px solid rgba(125,211,252,0.45);
    display: flex; align-items: center; justify-content: center;
    font-weight: 800; font-size: 15px;
  }}
  .popup-title {{ font-size: 13px; font-weight: 700; color: #7dd3fc; margin-bottom: 3px; }}
  .popup-tipo {{ font-size: 11px; font-weight: 700; color: #f8fafc; margin-bottom: 3px; }}
  .popup-desc {{ font-size: 11.5px; color: #cbd5e1; margin-bottom: 5px; line-height: 1.35; }}
  .popup-meta {{ font-size: 10.5px; color: #94a3b8; font-family: Consolas, monospace; }}
</style>
</head>
<body>
<div id="map3d"></div>
<div class="hud-top">
  <div class="status-badge" id="statusBadge"></div>
  <button class="hud-btn" id="btnVuelo" onclick="iniciarVuelo3D()">✈️ Vuelo 3D</button>
  <button class="hud-btn" id="btnTextura" onclick="alternarTextura()">🗺️ Mapa / 🛰️ Satélite</button>
  <button class="hud-btn" id="btnOrbita" onclick="alternarOrbita()">↻ Rotar 360°</button>
</div>
<div class="msg-overlay" id="msgOverlay"></div>

<script>
const DATA = {datos_js};

const avgLon = DATA.puntos.length ? DATA.puntos.reduce((s, p) => s + p.lon, 0) / DATA.puntos.length : -70.0219;
const avgLat = DATA.puntos.length ? DATA.puntos.reduce((s, p) => s + p.lat, 0) / DATA.puntos.length : -15.8402;

const map = new maplibregl.Map({{
  container: 'map3d',
  center: [avgLon, avgLat],
  zoom: 9.8,
  pitch: 62,
  bearing: -22,
  maxPitch: 85,
  antialias: true,
  style: {{
    version: 8,
    sources: {{
      'sat-tiles': {{
        type: 'raster',
        tiles: ['https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{{z}}/{{y}}/{{x}}'],
        tileSize: 256,
        maxzoom: 17,
        attribution: 'Esri World Imagery'
      }},
      'osm-tiles': {{
        type: 'raster',
        tiles: ['https://tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png'],
        tileSize: 256,
        maxzoom: 19,
        attribution: 'OpenStreetMap'
      }},
      'terrain-dem': {{
        type: 'raster-dem',
        tiles: ['https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{{z}}/{{x}}/{{y}}.png'],
        encoding: 'terrarium',
        tileSize: 256,
        maxzoom: 14
      }}
    }},
    layers: [
      {{ id: 'capa-sat', type: 'raster', source: 'sat-tiles', layout: {{ visibility: 'visible' }} }},
      {{ id: 'capa-osm', type: 'raster', source: 'osm-tiles', layout: {{ visibility: 'none' }} }},
      {{
        id: 'relieve-sombra',
        type: 'hillshade',
        source: 'terrain-dem',
        paint: {{
          'hillshade-shadow-color': '#0b1626',
          'hillshade-highlight-color': '#ffffff',
          'hillshade-exaggeration': 0.35
        }}
      }}
    ],
    terrain: {{
      source: 'terrain-dem',
      exaggeration: 1.85
    }}
  }}
}});

map.addControl(new maplibregl.NavigationControl({{ visualizePitch: true }}), 'top-right');

let marcadores = [];

map.on('load', () => {{
  // Fuente GeoJSON de carreteras reales OSRM / Valhalla
  map.addSource('rutas-reales', {{
    type: 'geojson',
    data: DATA.geojson_rutas
  }});

  // Borde azul oscuro para contraste 3D
  map.addLayer({{
    id: 'ruta-casing',
    type: 'line',
    source: 'rutas-reales',
    layout: {{ 'line-join': 'round', 'line-cap': 'round' }},
    paint: {{ 'line-color': '#0369a1', 'line-width': 8, 'line-opacity': 0.55 }}
  }});

  // Línea principal celeste brillante sobre la carretera 3D
  map.addLayer({{
    id: 'ruta-carretera',
    type: 'line',
    source: 'rutas-reales',
    filter: ['!=', ['get', 'tipo'], 'lacustre'],
    layout: {{ 'line-join': 'round', 'line-cap': 'round' }},
    paint: {{ 'line-color': '#38bdf8', 'line-width': 4.5, 'line-opacity': 0.96 }}
  }});

  // Línea punteada para tramos lacustres sobre el Lago Titicaca
  map.addLayer({{
    id: 'ruta-lacustre',
    type: 'line',
    source: 'rutas-reales',
    filter: ['==', ['get', 'tipo'], 'lacustre'],
    layout: {{ 'line-join': 'round', 'line-cap': 'round' }},
    paint: {{
      'line-color': '#7dd3fc',
      'line-width': 4,
      'line-dasharray': [2, 2]
    }}
  }});

  // Marcadores numerados con popups oscuros
  const bounds = new maplibregl.LngLatBounds();
  DATA.puntos.forEach((p) => {{
    bounds.extend([p.lon, p.lat]);
    const el = document.createElement('div');
    const cls = p.rol === 'ORIGEN' ? 'pin-origen' : (p.rol === 'DESTINO' ? 'pin-destino' : 'pin-parada');
    el.className = 'marker-pin ' + cls;
    el.innerText = p.orden;

    const inicial = (p.nombre || 'R').trim().charAt(0).toUpperCase();
    const heroHtml = p.foto_uri
      ? `<div class="popup-hero" style="padding:0;overflow:hidden;"><img src="${{p.foto_uri}}" style="width:100%;height:100%;object-fit:cover;border-radius:8px;"/></div>`
      : `<div class="popup-hero"><div class="popup-circle">${{inicial}}</div></div>`;
    const popup = new maplibregl.Popup({{ offset: 18 }}).setHTML(`
      <div class="popup-box">
        ${{heroHtml}}
        <div class="popup-title">${{p.orden}}. ${{p.nombre}} (${{p.rol}})</div>
        <div class="popup-tipo">Tipo: ${{p.tipo}}</div>
        <div class="popup-desc">${{p.descripcion}}</div>
        <div class="popup-meta">
          ${{p.costo_txt ? 'Costo: ' + p.costo_txt + ' · ' : ''}}${{p.duracion_txt ? 'Duración: ' + p.duracion_txt + '<br/>' : ''}}
          ${{p.transporte_txt ? 'Transporte: ' + p.transporte_txt + '<br/>' : ''}}
          ${{p.clima ? p.clima + '<br/>' : ''}}
          Coords: [${{p.lat.toFixed(4)}}, ${{p.lon.toFixed(4)}}]<br/>
          Fuente: ${{p.fuente}}
        </div>
      </div>
    `);

    const mk = new maplibregl.Marker({{ element: el }})
      .setLngLat([p.lon, p.lat])
      .setPopup(popup)
      .addTo(map);
    marcadores.push({{ mk, p }});
  }});

  if (DATA.puntos.length > 0) {{
    map.fitBounds(bounds, {{ padding: 70, pitch: 62, bearing: -22, maxZoom: 12.2, duration: 900 }});
  }}
}});

// Badge de estado 3D
const badge = document.getElementById('statusBadge');
if (DATA.osrm_activo) {{
  badge.innerHTML = `Terreno 3D · ${{DATA.motor_activo}} · <b>${{DATA.dist_osrm}} km reales</b> (~${{Math.round(DATA.dur_osrm)}} min)`;
}} else {{
  badge.innerHTML = `Terreno 3D Altiplano · <b>Ruta lacustre / directa</b>`;
}}

// Mensajes condicionales flotantes
const msgBox = document.getElementById('msgOverlay');
DATA.mensajes.forEach(m => {{
  const div = document.createElement('div');
  div.className = 'msg-card ' + (m.tipo === 'RECOMENDAR' ? 'rec' : '');
  const pref = m.tipo === 'RECOMENDAR' ? '★ RECOMENDACIÓN:' : 'ℹ MENSAJE:';
  div.innerHTML = `<b>${{pref}}</b> ${{m.texto}}`;
  msgBox.appendChild(div);
}});

// Botón: Alternar textura Satélite <-> Mapa OSM sobre el terreno 3D
let usandoSatelite = true;
function alternarTextura() {{
  usandoSatelite = !usandoSatelite;
  map.setLayoutProperty('capa-sat', 'visibility', usandoSatelite ? 'visible' : 'none');
  map.setLayoutProperty('capa-osm', 'visibility', usandoSatelite ? 'none' : 'visible');
}}

// Botón: Vuelo 3D cinematográfico por cada parada
let volando = false;
async function iniciarVuelo3D() {{
  if (volando || marcadores.length === 0) return;
  volando = true;
  const btn = document.getElementById('btnVuelo');
  btn.classList.add('active');
  btn.innerText = '✈️ Volando...';

  for (let i = 0; i < marcadores.length; i++) {{
    const {{ mk, p }} = marcadores[i];
    marcadores.forEach(m => m.mk.getPopup().remove());
    map.flyTo({{
      center: [p.lon, p.lat],
      zoom: 12.6,
      pitch: 68,
      bearing: -25 + i * 28,
      speed: 0.65,
      curve: 1.4,
      essential: true
    }});
    await new Promise(r => setTimeout(r, 2600));
    mk.togglePopup();
    await new Promise(r => setTimeout(r, 2000));
  }}

  volando = false;
  btn.classList.remove('active');
  btn.innerText = '✈️ Vuelo 3D';
}}

// Botón: Rotación orbital 360°
let orbitando = false;
let animId = null;
function rotarFrame() {{
  if (!orbitando) return;
  map.rotateTo((map.getBearing() + 0.25) % 360, {{ duration: 0 }});
  animId = requestAnimationFrame(rotarFrame);
}}
function alternarOrbita() {{
  orbitando = !orbitando;
  const btn = document.getElementById('btnOrbita');
  if (orbitando) {{
    btn.classList.add('active');
    rotarFrame();
  }} else {{
    btn.classList.remove('active');
    if (animId) cancelAnimationFrame(animId);
  }}
}}
</script>
</body>
</html>
"""


# =========================================================================
# ESTADO INICIAL Y BARRA SUPERIOR (ESTILO IDE)
# =========================================================================
claves_ejemplos = list(EJERCICIOS_TOUR_LANG.keys())
idx_defecto = next((i for i, k in enumerate(claves_ejemplos) if "3.10" in k), 0)

if "ejemplo_actual" not in st.session_state:
    st.session_state.ejemplo_actual = claves_ejemplos[idx_defecto]
if "codigo_editor" not in st.session_state:
    st.session_state.codigo_editor = EJERCICIOS_TOUR_LANG[st.session_state.ejemplo_actual]["codigo"]

# Top bar con marca, selector de ruta (30 ejercicios + 5 errores), botón Compilar y descargas
t_brand, t_sel, t_btn, t_dl1, t_dl2, t_dl3 = st.columns([2.1, 3.2, 1.1, 0.7, 0.8, 1.0])

with t_brand:
    st.markdown(
        '<p class="topbar-brand">TOUR-LANG</p>'
        '<p class="topbar-sub">COMPILADOR VISUAL DE RUTAS · UNA PUNO</p>',
        unsafe_allow_html=True,
    )

with t_sel:
    seleccion = st.selectbox(
        "Seleccionar ruta o ejercicio:",
        claves_ejemplos,
        index=claves_ejemplos.index(st.session_state.ejemplo_actual),
        label_visibility="collapsed",
    )
    if seleccion != st.session_state.ejemplo_actual:
        st.session_state.ejemplo_actual = seleccion
        st.session_state.codigo_editor = EJERCICIOS_TOUR_LANG[seleccion]["codigo"]
        st.rerun()

with t_btn:
    st.button("Compilar >", type="primary", use_container_width=True)

# Ejecutar pipeline de compilación sobre el texto actual del editor
codigo_actual = st.session_state.codigo_editor
tabla_lexica = TablaLexica()
parser = AnalizadorSintactico(codigo_actual, tabla_lexica)
ok_sintactico = parser.analizar()
tokens_leidos = parser.tokens_leidos
ok_lexico = not (parser.error and parser.error["tipo"] == "léxico")

semantico = None
ok_semantico = False
if ok_sintactico:
    semantico = AnalizadorSemantico(tokens_leidos)
    ok_semantico = semantico.analizar()

# Construir puntos y geometría real OSRM si compiló bien
puntos_mapa = []
geom_osrm = {"segmentos": [], "distancia_osrm_km": 0.0, "duracion_osrm_min": 0.0, "osrm_activo": False}
geojson_data = {"type": "FeatureCollection", "features": []}

if ok_sintactico and ok_semantico and semantico:
    ruta = semantico.modelo_ruta
    glob = ruta.get("globales", {})
    costo_g = f"S/ {glob['COSTO']}" if "COSTO" in glob else "No especificado"
    dur_g = f"{glob['DURACION']:g} h" if "DURACION" in glob else "No especificada"
    transp_g = str(glob.get("TRANSPORTE", "No especificado"))

    if ruta["origen_coords"]:
        puntos_mapa.append({
            "orden": 1,
            "nombre": ruta["origen"],
            "rol": "ORIGEN",
            "tipo": "PUNTO DE PARTIDA",
            "descripcion": "Inicio oficial de la ruta turística",
            "lat": ruta["origen_coords"][0],
            "lon": ruta["origen_coords"][1],
            "clima": "",
            "fuente": "catálogo",
            "costo_txt": costo_g,
            "duracion_txt": dur_g,
            "transporte_txt": transp_g,
            "foto_uri": buscar_foto_para_lugar(ruta["origen"]),
        })
    for idx_p, p in enumerate(ruta["paradas"], start=2):
        atrs = p["atributos"]
        clima_parts = []
        if "PRONOSTICO" in atrs:
            clima_parts.append(str(atrs["PRONOSTICO"]))
        if "TEMPERATURA" in atrs:
            clima_parts.append(f"{atrs['TEMPERATURA']}°C")
        if "PROBABILIDAD_LLUVIA" in atrs:
            clima_parts.append(f"Lluvia {atrs['PROBABILIDAD_LLUVIA']}%")
        costo_p = f"S/ {atrs['COSTO']}" if "COSTO" in atrs else costo_g
        dur_p = f"{atrs['DURACION']:g} h" if "DURACION" in atrs else dur_g
        transp_p = str(atrs.get("TRANSPORTE", transp_g))
        puntos_mapa.append({
            "orden": idx_p,
            "nombre": p["nombre"],
            "rol": "PARADA",
            "tipo": atrs.get("TIPO", "PARADA"),
            "descripcion": atrs.get("DESCRIPCION", "Parada intermedia registrada"),
            "lat": p["coords"][0],
            "lon": p["coords"][1],
            "clima": " · ".join(clima_parts),
            "fuente": "código [lat, lon]" if "UBICACION" in atrs else "catálogo",
            "costo_txt": costo_p,
            "duracion_txt": dur_p,
            "transporte_txt": transp_p,
            "foto_uri": buscar_foto_para_lugar(p["nombre"]),
        })
    if ruta["destino_coords"]:
        puntos_mapa.append({
            "orden": len(puntos_mapa) + 1,
            "nombre": ruta["destino"],
            "rol": "DESTINO",
            "tipo": "PUNTO DE LLEGADA",
            "descripcion": "Cierre oficial del circuito turístico",
            "lat": ruta["destino_coords"][0],
            "lon": ruta["destino_coords"][1],
            "clima": "",
            "fuente": "catálogo",
            "costo_txt": costo_g,
            "duracion_txt": dur_g,
            "transporte_txt": transp_g,
            "foto_uri": buscar_foto_para_lugar(ruta["destino"]),
        })

    if len(puntos_mapa) >= 2:
        transp = str(ruta["globales"].get("TRANSPORTE", ""))
        geom_osrm = obtener_geometria_cacheada(json.dumps(puntos_mapa, sort_keys=True), transp)
        geojson_data = exportar_geojson(ruta["nombre"], puntos_mapa, geom_osrm)

# Botones de exportación en la barra superior (.tl, .json, .geojson)
with t_dl1:
    st.download_button(".tl", data=codigo_actual, file_name="ruta_tour_lang.tl", mime="text/plain", use_container_width=True)
with t_dl2:
    modelo_json = json.dumps(semantico.modelo_ruta if semantico else {"error": parser.error}, indent=2, ensure_ascii=False)
    st.download_button(".json", data=modelo_json, file_name="ruta_compilada.json", mime="application/json", use_container_width=True)
with t_dl3:
    st.download_button(".geojson", data=json.dumps(geojson_data, indent=2, ensure_ascii=False), file_name="ruta_carretera.geojson", mime="application/geo+json", use_container_width=True)

# =========================================================================
# PANEL PRINCIPAL DIVIDIDO 50% / 50% (IZQUIERDA CÓDIGO | DERECHA MAPA)
# =========================================================================
col_izq, col_der = st.columns([1.0, 1.05], gap="small")

with col_izq:
    st.markdown(
        '<div class="panel-header"><span>UNIDAD DE COMPILACIÓN</span><span>EDITABLE</span></div>',
        unsafe_allow_html=True,
    )

    p_lex = '<span class="pill-ok">✓ Léxico</span>' if ok_lexico else '<span class="pill-err">✗ Léxico</span>'
    p_sin = '<span class="pill-ok">✓ Sintaxis</span>' if ok_sintactico else '<span class="pill-err">✗ Sintaxis</span>'
    p_sem = (
        '<span class="pill-ok">✓ Semántica</span>'
        if ok_semantico
        else ('<span class="pill-err">✗ Semántica</span>' if ok_sintactico else '<span class="pill-info">⋯ Semántica</span>')
    )
    p_pasos = f'<span class="pill-info">{len(parser.seguimiento)} pasos</span>'
    st.markdown(
        f'<div class="status-strip">{p_lex}{p_sin}{p_sem}{p_pasos}<span class="pill-file">ruta_demo.tl</span></div>',
        unsafe_allow_html=True,
    )

    tab_cod, tab_tok, tab_pda, tab_sem, tab_img = st.tabs(
        ["Código", "Tokens", "Traza PDA", "Semántica", "Imágenes de lugares"]
    )

    with tab_cod:
        st.text_area(
            "Código fuente TOUR-LANG",
            key="codigo_editor",
            height=560,
            label_visibility="collapsed",
        )

    with tab_tok:
        filas_lex = [
            {
                "#": i,
                "Cod": t.token,
                "Token": t.nombre,
                "Lexema": t.lexema if t.lexema is not None else "EOF",
                "Rama AFD": t.rama_afd,
                "Lin": t.linea,
                "Col": t.columna,
            }
            for i, t in enumerate(tokens_leidos, start=1)
        ]
        st.dataframe(pd.DataFrame(filas_lex), use_container_width=True, height=555, hide_index=True)

    with tab_pda:
        st.dataframe(pd.DataFrame(parser.seguimiento), use_container_width=True, height=555, hide_index=True)

    with tab_sem:
        if semantico:
            if semantico.errores:
                st.error(f"Se detectaron {len(semantico.errores)} error(es) semántico(s):")
                st.dataframe(pd.DataFrame(semantico.errores), use_container_width=True, hide_index=True)
            else:
                st.success("0 errores semánticos. Tabla de Símbolos por ámbito:")
            if semantico.tabla_simbolos:
                st.dataframe(pd.DataFrame(semantico.tabla_simbolos), use_container_width=True, height=430, hide_index=True)
        else:
            st.warning("La fase semántica se ejecuta cuando el Autómata de Pila (PDA) acepta la sintaxis.")

    with tab_img:
        st.markdown("#### 🖼️ Imágenes de lugares")
        DIR_IMAGENES_LUGARES.mkdir(parents=True, exist_ok=True)

        nombre_img_lugar = st.text_input(
            "Nombre del lugar o parada",
            placeholder="Ej. Sillustani, Islas Uros, Pucara...",
            key="input_nombre_img_lugar",
        )
        archivo_img = st.file_uploader(
            "Seleccionar foto (jpg, jpeg, png, webp, gif, bmp)",
            type=["jpg", "jpeg", "png", "webp", "gif", "bmp"],
            key="uploader_img_lugar",
        )

        reemplazar_confirmado = False
        slug_preview = normalizar_nombre_imagen(nombre_img_lugar) if nombre_img_lugar.strip() else ""
        archivo_existente = None
        if slug_preview:
            for ext_chk in EXTENSIONES_IMAGEN:
                cand_chk = DIR_IMAGENES_LUGARES / f"{slug_preview}{ext_chk}"
                if cand_chk.exists():
                    archivo_existente = cand_chk
                    break

        if archivo_existente is not None:
            st.warning(f"⚠️ Ya existe una foto registrada como `{archivo_existente.name}`.")
            reemplazar_confirmado = st.checkbox(
                "Sí, deseo reemplazar la foto existente",
                key="chk_reemplazar_img",
            )

        if st.button("💾 Guardar imagen", type="primary", key="btn_guardar_img_lugar"):
            if not nombre_img_lugar.strip():
                st.error("⚠️ Debes escribir el nombre del lugar.")
            elif archivo_img is None:
                st.error("⚠️ Debes seleccionar una imagen para subir.")
            else:
                ext_sub = Path(archivo_img.name).suffix.lower()
                if ext_sub not in EXTENSIONES_IMAGEN:
                    st.error(
                        f"⚠️ Formato `{ext_sub}` no permitido. Solo se aceptan: "
                        f"{', '.join(sorted(EXTENSIONES_IMAGEN))}."
                    )
                elif archivo_existente is not None and not reemplazar_confirmado:
                    st.error("⚠️ Marca la casilla de confirmación arriba si deseas reemplazar la foto existente.")
                else:
                    try:
                        img_verif = Image.open(archivo_img)
                        img_verif.verify()
                        archivo_img.seek(0)
                    except (UnidentifiedImageError, OSError, Exception) as exc:
                        st.error(f"⚠️ El archivo seleccionado no es una imagen válida o está dañado: {exc}")
                    else:
                        if archivo_existente is not None and archivo_existente.exists():
                            archivo_existente.unlink()
                        nombre_final = f"{slug_preview}{ext_sub}"
                        destino_final = DIR_IMAGENES_LUGARES / nombre_final
                        destino_final.write_bytes(archivo_img.getbuffer())

                        registros = cargar_registro_imagenes()
                        ruta_rel = f"prueba_imagenes/imagenes/{nombre_final}"
                        registros = [
                            r for r in registros if str(r.get("nombre_normalizado", "")) != slug_preview
                        ]
                        registros.append({
                            "nombre": nombre_img_lugar.strip(),
                            "nombre_normalizado": slug_preview,
                            "lugar": nombre_img_lugar.strip(),
                            "archivo": nombre_final,
                            "ruta": ruta_rel,
                        })
                        guardar_registro_imagenes(registros)
                        st.success(f"✅ Foto guardada como `{ruta_rel}` y registrada en `imagenes.json`.")
                        st.rerun()

        regs_actuales = cargar_registro_imagenes()
        if regs_actuales:
            st.markdown("**Imágenes registradas en `imagenes.json`:**")
            st.dataframe(pd.DataFrame(regs_actuales), use_container_width=True, height=220, hide_index=True)

with col_der:
    if "vista_selector" not in st.session_state or st.session_state.vista_selector not in ("2D", "Satélite", "3D"):
        st.session_state.vista_selector = "2D"

    mapa_vistas = {"MAPA": "2D", "SATELITE": "Satélite", "3D": "3D"}
    if ok_sintactico and ok_semantico and semantico:
        vista_codigo = mapa_vistas.get(
            semantico.modelo_ruta.get("vista_predominante", "MAPA"), "2D"
        )
        clave_fuente = (st.session_state.ejemplo_actual, codigo_actual)
        if st.session_state.get("ultima_fuente_vista") != clave_fuente:
            st.session_state.vista_selector = vista_codigo
            st.session_state.ultima_fuente_vista = clave_fuente

    c_v1, c_v2, c_v3 = st.columns(3, gap="small")
    with c_v1:
        if st.button(
            "🗺️ Vista 2D",
            type="primary" if st.session_state.vista_selector == "2D" else "secondary",
            use_container_width=True,
            key="btn_vista_2d",
        ):
            st.session_state.vista_selector = "2D"
            st.rerun()
    with c_v2:
        if st.button(
            "🛰️ Satélite",
            type="primary" if st.session_state.vista_selector == "Satélite" else "secondary",
            use_container_width=True,
            key="btn_vista_sat",
        ):
            st.session_state.vista_selector = "Satélite"
            st.rerun()
    with c_v3:
        if st.button(
            "🏔️ Terreno 3D",
            type="primary" if st.session_state.vista_selector == "3D" else "secondary",
            use_container_width=True,
            key="btn_vista_3d",
        ):
            st.session_state.vista_selector = "3D"
            st.rerun()

    modo_activo = st.session_state.vista_selector
    etiqueta_motor = {
        "3D": "MAPLIBRE GL 3D · RELIEVE DEM · OSRM / VALHALLA",
        "Satélite": "LEAFLET SATELITAL · OSRM / VALHALLA",
        "2D": "LEAFLET 2D · OSRM / VALHALLA",
    }.get(modo_activo, "LEAFLET 2D · OSRM / VALHALLA")
    st.markdown(
        f'<div class="panel-header"><span>SALIDA COMPILADA · MAPA DE EJECUCIÓN</span><span>{etiqueta_motor}</span></div>',
        unsafe_allow_html=True,
    )

    if not ok_sintactico and parser.error:
        st.error(f"**{parser.error['mensaje']}**")
        st.info(f"Estado PDA: `{parser.error['estado']}` | Pila actual: `{parser.error['pila']}`")
    elif semantico and not ok_semantico:
        st.warning("El programa superó el AFD Léxico y el PDA Sintáctico (`qF`), pero fue rechazado por el Analizador Semántico:")
        for err in semantico.errores:
            st.error(f"**Línea {err['Línea']}** (`{err['Sentencia']}`): {err['Error Semántico']}")
    else:
        ruta = semantico.modelo_ruta
        if modo_activo == "3D":
            html_mapa = renderizar_mapa_3d_maplibre(
                nombre_ruta=ruta["nombre"],
                puntos=puntos_mapa,
                geom=geom_osrm,
                globales=ruta["globales"],
                mensajes_salida=ruta["mensajes_salida"],
            )
        else:
            vista_leaflet = "SATELITE" if modo_activo == "Satélite" else "MAPA"
            html_mapa = renderizar_mapa_leaflet(
                nombre_ruta=ruta["nombre"],
                puntos=puntos_mapa,
                geom=geom_osrm,
                vista_inicial=vista_leaflet,
                globales=ruta["globales"],
                mensajes_salida=ruta["mensajes_salida"],
            )
        components.html(html_mapa, height=600, scrolling=False)
