"""
Plataforma Web Interactiva del Compilador TOUR-LANG (UNA Puno - EPIS 2026-II)
Ejecutar con: streamlit run app.py
"""

import os
import sys
import subprocess

# Auto-arranque inteligente: permite ejecutar con el botón Play de VS Code (python app.py)
# además del comando tradicional (streamlit run app.py)
if __name__ == "__main__":
    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx
        if get_script_run_ctx() is None:
            sys.exit(subprocess.call([sys.executable, "-m", "streamlit", "run", os.path.abspath(__file__)]))
    except ImportError:
        pass

import pandas as pd
import pydeck as pdk
import streamlit as st

from tour_lang import AnalizadorSemantico, AnalizadorSintactico, TablaLexica
from tour_lang.ejemplos import EJERCICIOS_TOUR_LANG

st.set_page_config(
    page_title="TOUR-LANG | Compilador y Visor de Rutas Turísticas de Puno",
    page_icon="🗺️",
    layout="wide",
)

# Estilos institucionales UNA Puno - EPIS
st.markdown(
    """
    <style>
    .hero-banner {
        background: linear-gradient(135deg, #0B4160 0%, #185E82 60%, #23799D 100%);
        color: white;
        padding: 1.3rem 1.8rem;
        border-radius: 12px;
        margin-bottom: 1rem;
        box-shadow: 0 4px 14px rgba(11, 65, 96, 0.18);
    }
    .hero-banner h1 {
        margin: 0;
        font-size: 1.75rem;
        color: #FFFFFF;
    }
    .hero-banner p {
        margin: 0.35rem 0 0 0;
        font-size: 0.95rem;
        color: #EBF5FB;
    }
    .badge-ok {
        background-color: #D4EFDF;
        color: #145A32;
        padding: 0.35rem 0.75rem;
        border-radius: 8px;
        font-weight: 700;
        display: inline-block;
    }
    .badge-err {
        background-color: #FADBD8;
        color: #78281F;
        padding: 0.35rem 0.75rem;
        border-radius: 8px;
        font-weight: 700;
        display: inline-block;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero-banner">
        <h1>🗺️ TOUR-LANG — Compilador e Intérprete de Rutas Turísticas en Puno</h1>
        <p><b>Universidad Nacional del Altiplano (UNA Puno)</b> · Escuela Profesional de Ingeniería de Sistemas ·
        Curso: <b>Compiladores (V Semestre - Grupo A)</b> · Área: Ciencias de la Computación</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# Barra lateral: Selector de ejercicios y equipo
with st.sidebar:
    st.markdown("### 📚 Banco de 30 Ejercicios + Pruebas")
    niveles = sorted(list({v["nivel"] for v in EJERCICIOS_TOUR_LANG.values()}))
    nivel_sel = st.selectbox("Filtrar por categoría:", ["Todos"] + niveles, index=0)

    claves_filtradas = [
        k for k, v in EJERCICIOS_TOUR_LANG.items()
        if nivel_sel == "Todos" or v["nivel"] == nivel_sel
    ]
    indice_default = 0
    for idx, k in enumerate(claves_filtradas):
        if "3.10" in k:
            indice_default = idx
            break

    ejemplo_sel = st.selectbox("Seleccionar programa TOUR-LANG:", claves_filtradas, index=indice_default)

    st.markdown("---")
    modo_mapa_override = st.radio(
        "Modo de cámara cartográfica:",
        ["Automático (según VISTA del código)", "Mapa 2D Estándar", "Perspectiva 3D Altiplano", "Vista Satelital"],
        index=0,
    )

    st.markdown("---")
    st.markdown(
        """
        **Equipo Desarrollador:**
        - Kriss Katherine Aico Ramos
        - Julissa Esther Mestas Huanca
        - Anthony Junior Quispe Cruz

        **Docente Asesor:**
        - Ing. Victor Hugo Bejar Gonzales
        """
    )

# Columnas superiores: Editor de código vs Resumen de compilación
col_editor, col_estado = st.columns([1.15, 0.85], gap="large")

with col_editor:
    st.subheader("💻 Editor de Código Fuente (.tour)")
    codigo_fuente = st.text_area(
        "Escribe o edita tu programa en TOUR-LANG:",
        value=EJERCICIOS_TOUR_LANG[ejemplo_sel]["codigo"],
        height=370,
    )
    compilar_btn = st.button("▶️ Compilar y Ejecutar Ruta", type="primary", use_container_width=True)

# Ejecutar pipeline completo: Léxico (AFD) -> Sintáctico (PDA) -> Semántico -> Mapa
tabla_lexica = TablaLexica()
parser = AnalizadorSintactico(codigo_fuente, tabla_lexica)
ok_sintactico = parser.analizar()
tokens_leidos = parser.tokens_leidos
ok_lexico = not (parser.error and parser.error["tipo"] == "léxico")

semantico = None
ok_semantico = False
if ok_sintactico:
    semantico = AnalizadorSemantico(tokens_leidos)
    ok_semantico = semantico.analizar()

with col_estado:
    st.subheader("⚙️ Diagnóstico en Pipeline del Compilador")

    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric("1. Fase Léxica (AFD)", "ACEPTADO" if ok_lexico else "RECHAZADO", f"{len(tokens_leidos)} tokens")
    with m2:
        st.metric(
            "2. Fase Sintáctica (PDA)",
            "ACEPTADO" if ok_sintactico else ("PENDIENTE" if not ok_lexico else "RECHAZADO"),
            f"Estado: {parser.estado_actual}",
        )
    with m3:
        estado_sem_txt = "ACEPTADO" if ok_semantico else ("NO EJECUTADO" if not ok_sintactico else "RECHAZADO")
        errores_sem_cnt = f"{len(semantico.errores)} errores" if semantico else "Requiere PDA OK"
        st.metric("3. Fase Semántica", estado_sem_txt, errores_sem_cnt)

    if not ok_sintactico and parser.error:
        st.error(f"**{parser.error['mensaje']}**")
        st.caption(f"Estado del PDA: `{parser.error['estado']}` | Contenido de la Pila: `{parser.error['pila']}`")
    elif semantico and not ok_semantico:
        st.warning(
            "El programa superó los análisis **Léxico (AFD)** y **Sintáctico (PDA en qF con pila vacía)**, "
            "pero fue rechazado por el **Analizador Semántico**:"
        )
        for err in semantico.errores:
            st.error(f"**Línea {err['Línea']}** (`{err['Sentencia']}`): {err['Error Semántico']}")
    else:
        ruta = semantico.modelo_ruta
        st.success(
            f"✅ **Compilación Exitosa en las 3 Fases** — Ruta `{ruta['nombre']}` validada "
            f"({ruta['origen']} ➔ {len(ruta['paradas'])} parada(s) ➔ {ruta['destino']})."
        )
        if ruta["globales"]:
            partes_glob = [f"**{k}:** `{v}`" for k, v in ruta["globales"].items()]
            st.info(" | ".join(partes_glob))
        for msg in ruta["mensajes_salida"]:
            icono = "🌟 RECOMENDACIÓN:" if msg["tipo"] == "RECOMENDAR" else "📢 MENSAJE:"
            st.success(f"{icono} *{msg['texto']}*")

st.markdown("---")

# Pestañas detalladas de resultados
tab_mapa, tab_lexico, tab_sintactico, tab_semantico, tab_modelos = st.tabs([
    "🗺️ 1. Visor Cartográfico (2D / 3D / Satélite)",
    "🔤 2. Flujo de Tokens (AFD)",
    "🥞 3. Traza del Autómata de Pila (PDA)",
    "📐 4. Tabla de Símbolos y Semántica",
    "📊 5. Diagramas Formales (AFD y JFLAP)",
])

with tab_mapa:
    if ok_sintactico and ok_semantico and semantico:
        ruta = semantico.modelo_ruta
        puntos = []

        if ruta["origen_coords"]:
            puntos.append({
                "orden": 0,
                "etiqueta": f"ORIGEN: {ruta['origen']}",
                "nombre": ruta["origen"],
                "tipo": "ORIGEN",
                "descripcion": "Punto de partida oficial del circuito turístico",
                "lat": ruta["origen_coords"][0],
                "lon": ruta["origen_coords"][1],
                "color": [46, 204, 113, 230],
                "altura": 3200,
                "clima": "",
            })

        for idx_p, p in enumerate(ruta["paradas"], start=1):
            atrs = p["atributos"]
            clima_partes = []
            if "PRONOSTICO" in atrs:
                clima_partes.append(str(atrs["PRONOSTICO"]))
            if "TEMPERATURA" in atrs:
                clima_partes.append(f"{atrs['TEMPERATURA']} °C")
            if "PROBABILIDAD_LLUVIA" in atrs:
                clima_partes.append(f"Lluvia: {atrs['PROBABILIDAD_LLUVIA']}%")

            puntos.append({
                "orden": idx_p,
                "etiqueta": f"PARADA {idx_p}: {p['nombre']}",
                "nombre": p["nombre"],
                "tipo": atrs.get("TIPO", "PARADA INTERMEDIA"),
                "descripcion": atrs.get("DESCRIPCION", "Parada intermedia registrada en TOUR-LANG"),
                "lat": p["coords"][0],
                "lon": p["coords"][1],
                "color": [243, 156, 18, 235],
                "altura": 4800,
                "clima": " · ".join(clima_partes) if clima_partes else "Clima estándar altiplánico",
            })

        if ruta["destino_coords"]:
            puntos.append({
                "orden": len(puntos),
                "etiqueta": f"DESTINO: {ruta['destino']}",
                "nombre": ruta["destino"],
                "tipo": "DESTINO FINAL",
                "descripcion": "Punto de culminación del circuito",
                "lat": ruta["destino_coords"][0],
                "lon": ruta["destino_coords"][1],
                "color": [231, 76, 60, 230],
                "altura": 3200,
                "clima": "",
            })

        if len(puntos) >= 2:
            df_pts = pd.DataFrame(puntos)
            segmentos = []
            for s_i in range(len(puntos) - 1):
                segmentos.append({
                    "from_name": puntos[s_i]["nombre"],
                    "to_name": puntos[s_i + 1]["nombre"],
                    "from_lon": puntos[s_i]["lon"],
                    "from_lat": puntos[s_i]["lat"],
                    "to_lon": puntos[s_i + 1]["lon"],
                    "to_lat": puntos[s_i + 1]["lat"],
                })
            df_seg = pd.DataFrame(segmentos)

            vista_codigo = ruta["vista_predominante"]
            if modo_mapa_override == "Mapa 2D Estándar":
                modo_efectivo = "MAPA"
            elif modo_mapa_override == "Perspectiva 3D Altiplano":
                modo_efectivo = "3D"
            elif modo_mapa_override == "Vista Satelital":
                modo_efectivo = "SATELITE"
            else:
                modo_efectivo = vista_codigo

            pitch_val = 54 if modo_efectivo in ("3D", "SATELITE") else 0
            bearing_val = -15 if modo_efectivo == "3D" else 0

            capas = []
            if modo_efectivo == "SATELITE":
                capas.append(
                    pdk.Layer(
                        "TileLayer",
                        data="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
                        min_zoom=0,
                        max_zoom=19,
                        tile_size=256,
                    )
                )

            capas.extend([
                pdk.Layer(
                    "ArcLayer",
                    data=df_seg,
                    get_source_position="[from_lon, from_lat]",
                    get_target_position="[to_lon, to_lat]",
                    get_source_color=[24, 188, 156, 220],
                    get_target_color=[241, 196, 15, 220],
                    get_width=5,
                    pickable=True,
                ),
                pdk.Layer(
                    "ScatterplotLayer",
                    data=df_pts,
                    get_position="[lon, lat]",
                    get_fill_color="color",
                    get_radius=1800,
                    radius_min_pixels=8,
                    radius_max_pixels=22,
                    stroked=True,
                    get_line_color=[255, 255, 255, 255],
                    line_width_min_pixels=2,
                    pickable=True,
                ),
            ])

            if modo_efectivo == "3D":
                capas.append(
                    pdk.Layer(
                        "ColumnLayer",
                        data=df_pts,
                        get_position="[lon, lat]",
                        get_elevation="altura",
                        elevation_scale=1,
                        radius=1100,
                        get_fill_color="color",
                        pickable=True,
                        extruded=True,
                    )
                )

            view_state = pdk.ViewState(
                latitude=float(df_pts["lat"].mean()),
                longitude=float(df_pts["lon"].mean()),
                zoom=8.4,
                pitch=pitch_val,
                bearing=bearing_val,
            )

            estilo_base = (
                None if modo_efectivo == "SATELITE"
                else "https://basemaps.cartocdn.com/gl/voyager-gl-style/style.json"
            )

            st.caption(
                f"**Modo Visual Activo:** `{modo_efectivo}` · "
                f"**Puntos trazados:** `{len(df_pts)}` · **Tramos:** `{len(df_seg)}`"
            )

            st.pydeck_chart(
                pdk.Deck(
                    layers=capas,
                    initial_view_state=view_state,
                    map_style=estilo_base,
                    tooltip={
                        "html": (
                            "<b>{etiqueta}</b><br/>"
                            "Tipo: {tipo}<br/>"
                            "{descripcion}<br/>"
                            "<i>{clima}</i><br/>"
                            "Coords: [{lat}, {lon}]"
                        ),
                        "style": {"backgroundColor": "#0B4160", "color": "white"},
                    },
                ),
                use_container_width=True,
            )

            st.markdown("#### 📍 Resumen Estructurado del Itinerario Compilado")
            st.dataframe(
                df_pts[["orden", "etiqueta", "tipo", "descripcion", "clima", "lat", "lon"]],
                use_container_width=True,
                hide_index=True,
            )
    else:
        st.info(
            "Corrige los errores reportados en el panel superior (o selecciona uno de los 30 ejercicios válidos "
            "en la barra lateral) para renderizar el mapa interactivo de la ruta."
        )

with tab_lexico:
    st.markdown("#### 🔤 Tabla de Tokens Generados por el Analizador Léxico (AFD)")
    filas_lex = [
        {
            "#": idx,
            "Código": t.token,
            "Token": t.nombre,
            "Lexema": t.lexema if t.lexema is not None else "EOF",
            "Categoría": t.categoria,
            "Rama AFD": t.rama_afd,
            "Línea": t.linea,
            "Columna": t.columna,
        }
        for idx, t in enumerate(tokens_leidos, start=1)
    ]
    st.dataframe(pd.DataFrame(filas_lex), use_container_width=True, hide_index=True)

with tab_sintactico:
    st.markdown("#### 🥞 Traza Paso a Paso del Autómata de Pila Determinista (PDA - 36 estados)")
    st.caption("Símbolos de pila Γ = { Z (fondo/ruta), P (bloque de parada), A (arreglo [lat, lon]), S (condicional SI) }")
    st.dataframe(pd.DataFrame(parser.seguimiento), use_container_width=True, hide_index=True)

with tab_semantico:
    if semantico:
        col_s1, col_s2 = st.columns([1.2, 0.8])
        with col_s1:
            st.markdown("#### 📋 Tabla de Símbolos por Ámbito (Global vs. Local por Parada)")
            if semantico.tabla_simbolos:
                st.dataframe(pd.DataFrame(semantico.tabla_simbolos), use_container_width=True, hide_index=True)
        with col_s2:
            st.markdown("#### 🔍 Evaluación de Condicionales y Reglas")
            if semantico.errores:
                st.dataframe(pd.DataFrame(semantico.errores), use_container_width=True, hide_index=True)
            else:
                st.success("0 errores semánticos detectados. Todos los tipos, dominios, rangos [0,100] y unicidades son válidos.")
                if semantico.modelo_ruta["condicionales"]:
                    st.json(semantico.modelo_ruta["condicionales"])
    else:
        st.warning("El Análisis Semántico se ejecuta una vez que el Autómata de Pila (PDA) acepta la estructura sintáctica.")

with tab_modelos:
    st.markdown("#### 📊 Arquitectura y Diagramas Formales del Compilador")
    ruta_arq = os.path.join(os.path.dirname(__file__), "docs", "arquitectura_tourlang.png")
    ruta_afd = os.path.join(os.path.dirname(__file__), "docs", "afd_resumen.png")
    if os.path.exists(ruta_arq):
        st.image(ruta_arq, caption="Arquitectura en Pipeline del Compilador TOUR-LANG y Visor Web en Python")
    if os.path.exists(ruta_afd):
        st.image(ruta_afd, caption="Resumen de las 4 Ramas del AFD Léxico (estados q0–q140 y errores E1–E5)")
