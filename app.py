"""
Plataforma Web Interactiva del Compilador Visual TOUR-LANG (UNA Puno - EPIS 2026-II)
Diseño pantalla dividida: Unidad de Compilación a la izquierda | Mapa Leaflet + OSRM a la derecha.
Ejecutar con: streamlit run app.py  (o doble clic en iniciar_web.bat / botón Play en VS Code)
"""

import json
import os
import subprocess
import sys

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
  const popupHtml = `
    <div class="popup-box">
      <div class="popup-hero"><div class="popup-circle">${{inicial}}</div></div>
      <div class="popup-title">${{p.orden}}. ${{p.nombre}} (${{p.rol}})</div>
      <div class="popup-tipo">Tipo: ${{p.tipo}}</div>
      <div class="popup-desc">${{p.descripcion}}</div>
      <div class="popup-meta">
        ${{p.clima ? p.clima + '<br/>' : ''}}
        Coords: [${{p.lat.toFixed(4)}}, ${{p.lon.toFixed(4)}}]<br/>
        Fuente: ${{p.fuente}}
      </div>
    </div>
  `;

  const mk = L.marker([p.lat, p.lon], {{ icon }}).addTo(map).bindPopup(popupHtml);
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

    tab_cod, tab_tok, tab_pda, tab_sem = st.tabs(["Código", "Tokens", "Traza PDA", "Semántica"])

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

with col_der:
    st.markdown(
        '<div class="panel-header"><span>SALIDA COMPILADA · MAPA DE EJECUCIÓN</span><span>LEAFLET · OSRM / VALHALLA</span></div>',
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
        html_mapa = renderizar_mapa_leaflet(
            nombre_ruta=ruta["nombre"],
            puntos=puntos_mapa,
            geom=geom_osrm,
            vista_inicial=ruta["vista_predominante"],
            globales=ruta["globales"],
            mensajes_salida=ruta["mensajes_salida"],
        )
        components.html(html_mapa, height=645, scrolling=False)
