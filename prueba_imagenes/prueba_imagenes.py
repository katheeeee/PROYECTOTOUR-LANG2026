import csv
import json
import re
import unicodedata
from pathlib import Path
from PIL import Image, UnidentifiedImageError
import streamlit as st

st.set_page_config(
    page_title="TOUR-LANG · Galería de Imágenes (Estilo LaTeX)",
    page_icon="🏔️",
    layout="wide",
)

EXTENSIONES_VALIDAS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp"}
ARCHIVOS_SISTEMA = {".gitkeep", "desktop.ini", "thumbs.db"}

PUNO_LAT_MIN, PUNO_LAT_MAX = -17.5, -13.0
PUNO_LON_MIN, PUNO_LON_MAX = -71.5, -68.5

BASE_DIR = Path(__file__).resolve().parent
PROYECTO_DIR = BASE_DIR.parent
IMAGENES_DIR = BASE_DIR / "imagenes"
LUGARES_EXTRA_PATH = BASE_DIR / "lugares_extra.json"
HOTELES_PATH = BASE_DIR / "hoteles_puno.json"
OSM_CSV_PATHS = (PROYECTO_DIR / "lugares_puno_osm.csv", BASE_DIR / "lugares_puno_osm.csv")

IMAGENES_DIR.mkdir(parents=True, exist_ok=True)


def normalizar_nombre(texto: str) -> str:
    """Normaliza un nombre de archivo o lugar a minúsculas con guiones bajos sin acentos."""
    sin_acentos = "".join(
        c for c in unicodedata.normalize("NFKD", texto.strip().lower()) if not unicodedata.combining(c)
    )
    limpio = re.sub(r"[^a-z0-9]+", "_", sin_acentos).strip("_")
    return limpio or "imagen_puno"


def cargar_json_lista(ruta: Path) -> list[dict]:
    if not ruta.exists():
        return []
    try:
        data = json.loads(ruta.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except (OSError, ValueError):
        return []


def cargar_lugares_osm() -> list[dict]:
    registros = []
    for ruta in OSM_CSV_PATHS:
        if not ruta.exists():
            continue
        try:
            with ruta.open("r", encoding="utf-8", newline="") as f:
                for fila in csv.DictReader(f):
                    nom = str(fila.get("nombre", "")).strip()
                    cat = str(fila.get("categoria", "Lugar")).strip()
                    try:
                        lat = float(str(fila.get("latitud", "")).strip())
                        lon = float(str(fila.get("longitud", "")).strip())
                    except ValueError:
                        continue
                    if nom:
                        registros.append({
                            "nombre": nom,
                            "categoria": cat,
                            "latitud": lat,
                            "longitud": lon,
                        })
            break
        except OSError:
            continue
    return registros


def guardar_lugar_extra(nombre: str, latitud: float, longitud: float, archivo_foto: str = "") -> None:
    lugares = cargar_json_lista(LUGARES_EXTRA_PATH)
    slug = normalizar_nombre(nombre)
    actualizado = False
    for item in lugares:
        if str(item.get("nombre", "")).strip().lower() == nombre.strip().lower():
            item["latitud"] = round(latitud, 6)
            item["longitud"] = round(longitud, 6)
            if archivo_foto:
                item["foto"] = archivo_foto
            item["nombre_normalizado"] = slug
            actualizado = True
            break
    if not actualizado:
        lugares.append({
            "nombre": nombre.strip(),
            "nombre_normalizado": slug,
            "latitud": round(latitud, 6),
            "longitud": round(longitud, 6),
            "foto": archivo_foto,
        })
    LUGARES_EXTRA_PATH.write_text(json.dumps(lugares, ensure_ascii=False, indent=2), encoding="utf-8")


def mostrar_imagen(imagen: Image.Image) -> None:
    try:
        st.image(imagen, use_container_width=True)
    except TypeError:
        st.image(imagen, use_column_width=True)


st.title("🏔️ TOUR-LANG · Imágenes de Puno (Estilo LaTeX)")
st.caption(
    "Sube tus fotos a `imagenes/` y llámalas directo por su nombre en tu ruta, "
    "sin APIs externas. Compatible con `lugares_puno_osm.csv` y `lugares_extra.json`."
)

# ==========================================================
# 1. SUBIDA RÁPIDA ESTILO LATEX (SOLO SUBIR Y LLAMAR)
# ==========================================================
col_subir, col_extra = st.columns([1.4, 1.0])

with col_subir:
    with st.container(border=True):
        st.subheader("📤 Subir imagen (rápido, como en LaTeX)")
        st.caption(
            "Sube una o varias fotos (`.jpg`, `.jpeg`, `.png`, `.webp`, `.gif`, `.bmp`). "
            "Se guardan en `imagenes/` listas para llamarlas por su nombre."
        )
        with st.form("form_subida_rapida", clear_on_submit=True):
            archivos_subidos = st.file_uploader(
                "Selecciona tus fotos",
                type=["jpg", "jpeg", "png", "webp", "gif", "bmp"],
                accept_multiple_files=True,
            )
            nombre_alias = st.text_input(
                "Nombre opcional (si subes 1 foto; si lo dejas vacío usa el nombre del archivo)",
                placeholder="Ej. sillustani, hotel_munay_tambo, uros...",
            )
            btn_subir = st.form_submit_button("⬆️ Subir a imagenes/", type="primary")

        if btn_subir:
            if not archivos_subidos:
                st.error("⚠️ Selecciona al menos una imagen antes de subir.")
            else:
                guardadas = 0
                for idx_f, f in enumerate(archivos_subidos):
                    ext = Path(f.name).suffix.lower()
                    if ext not in EXTENSIONES_VALIDAS:
                        st.error(f"⚠️ `{f.name}`: extensión no permitida.")
                        continue
                    try:
                        img_test = Image.open(f)
                        img_test.verify()
                        f.seek(0)
                    except (UnidentifiedImageError, OSError, Exception) as exc:
                        st.error(f"⚠️ No se pudo abrir `{f.name}`: {exc}")
                        continue

                    base_nombre = (
                        normalizar_nombre(nombre_alias)
                        if (nombre_alias.strip() and len(archivos_subidos) == 1)
                        else normalizar_nombre(Path(f.name).stem)
                    )
                    nombre_final = f"{base_nombre}{ext}"
                    (IMAGENES_DIR / nombre_final).write_bytes(f.getbuffer())
                    guardadas += 1

                if guardadas > 0:
                    st.success(f"✅ Se guardaron **{guardadas}** imagen(es) en `imagenes/`. Ya puedes llamarlas abajo.")

with col_extra:
    with st.container(border=True):
        st.subheader("📍 Registrar lugar extra (opcional)")
        st.caption("Solo si tu lugar o hotel no está en `lugares_puno_osm.csv`.")
        with st.form("form_lugar_extra", clear_on_submit=True):
            nombre_lugar = st.text_input("Nombre del lugar", placeholder="Ej. Mirador Puma Uta")
            c_lat, c_lon = st.columns(2)
            with c_lat:
                latitud = st.number_input("Latitud", min_value=-90.0, max_value=90.0, value=-15.840200, format="%.6f")
            with c_lon:
                longitud = st.number_input("Longitud", min_value=-180.0, max_value=180.0, value=-70.021900, format="%.6f")
            btn_lugar = st.form_submit_button("💾 Guardar en lugares_extra.json")

        if btn_lugar:
            if not nombre_lugar.strip():
                st.error("⚠️ Escribe el nombre del lugar.")
            else:
                guardar_lugar_extra(nombre_lugar, float(latitud), float(longitud))
                if not (PUNO_LAT_MIN <= latitud <= PUNO_LAT_MAX and PUNO_LON_MIN <= longitud <= PUNO_LON_MAX):
                    st.warning("⚠️ Guardado, pero las coordenadas están fuera del rango típico de Puno.")
                st.success(f"✅ **{nombre_lugar.strip()}** registrado en `lugares_extra.json`.")

st.divider()

# ==========================================================
# 2. GALERÍA DE IMÁGENES EN imagenes/
# ==========================================================
st.subheader("🖼️ Galería de Imágenes (`imagenes/`)")

lugares_extra = cargar_json_lista(LUGARES_EXTRA_PATH)
hoteles_json = cargar_json_lista(HOTELES_PATH)
lugares_osm = cargar_lugares_osm()

archivos = sorted(
    [
        p
        for p in IMAGENES_DIR.iterdir()
        if p.is_file() and p.name.lower() not in ARCHIVOS_SISTEMA and not p.name.startswith(".")
    ],
    key=lambda p: p.name.lower(),
)

imagenes_validas: list[tuple[Path, Image.Image]] = []
mapa_fotos_por_slug: dict[str, tuple[Path, Image.Image]] = {}

if not archivos:
    st.info(
        "📂 La carpeta **`imagenes/`** está vacía.\n\n"
        "Sube tu primera imagen arriba (como en LaTeX) o copia archivos `.jpg`, `.png`, `.webp` "
        "dentro de `prueba_imagenes/imagenes/`."
    )
else:
    errores: list[str] = []
    for archivo in archivos:
        if archivo.suffix.lower() not in EXTENSIONES_VALIDAS:
            errores.append(
                f"El archivo **{archivo.name}** no tiene una extensión permitida "
                f"({', '.join(sorted(EXTENSIONES_VALIDAS))})."
            )
            continue
        try:
            with Image.open(archivo) as img:
                img.load()
                copia = img.copy()
                imagenes_validas.append((archivo, copia))
                mapa_fotos_por_slug[normalizar_nombre(archivo.stem)] = (archivo, copia)
        except (UnidentifiedImageError, OSError, Exception) as exc:
            errores.append(f"No se pudo abrir **{archivo.name}**: `{exc}`")

    for msg in errores:
        st.error(f"⚠️ {msg}")

    if not imagenes_validas:
        st.warning("No se encontraron imágenes válidas que se puedan abrir en `imagenes/`.")
    else:
        st.success(f"**{len(imagenes_validas)}** imagen(es) disponible(s). Copia su nombre para llamarla:")
        cols = st.columns(3)
        for idx, (archivo, imagen) in enumerate(imagenes_validas):
            with cols[idx % 3]:
                with st.container(border=True):
                    mostrar_imagen(imagen)
                    st.markdown(f"**📄 {archivo.name}**")
                    st.code(archivo.name, language=None)

# ==========================================================
# 3. PROBAR LLAMADA DE IMAGEN EN UNA RUTA
# ==========================================================
st.divider()
st.subheader("🧪 Llamar imagen en tu ruta (vista previa)")

todos_lugares = lugares_osm + [
    {"nombre": h.get("nombre", ""), "categoria": "Hotel (JSON)", "latitud": h.get("latitud"), "longitud": h.get("longitud")}
    for h in hoteles_json
] + [
    {"nombre": e.get("nombre", ""), "categoria": "Lugar Extra", "latitud": e.get("latitud"), "longitud": e.get("longitud")}
    for e in lugares_extra
]

if imagenes_validas and todos_lugares:
    c1, c2 = st.columns(2)
    with c1:
        nombres_lugares = [l["nombre"] for l in todos_lugares if l.get("nombre")]
        lugar_sel = st.selectbox("1. Elige el lugar o hotel de tu ruta", nombres_lugares)
    with c2:
        nombres_fotos = [a.name for a, _ in imagenes_validas]
        foto_sel = st.selectbox("2. Elige la imagen a llamar", nombres_fotos)

    lugar_obj = next((l for l in todos_lugares if l["nombre"] == lugar_sel), None)
    foto_obj = next(((a, im) for a, im in imagenes_validas if a.name == foto_sel), None)

    if lugar_obj and foto_obj:
        p_col1, p_col2 = st.columns([1, 1.4])
        with p_col1:
            mostrar_imagen(foto_obj[1])
            st.caption(f"📄 Imagen llamada: `{foto_obj[0].name}`")
        with p_col2:
            st.markdown(f"### 📍 {lugar_obj['nombre']}")
            st.write(f"**Categoría:** {lugar_obj.get('categoria', 'Lugar')}")
            st.write(f"**Coordenadas:** `{lugar_obj['latitud']}, {lugar_obj['longitud']}`")
            st.code(
                f'INICIO_PARADA "{lugar_obj["nombre"]}" :>\n'
                f'  UBICACION = [{lugar_obj["latitud"]}, {lugar_obj["longitud"]}] :>\n'
                f'  TIPO = "CULTURAL" :>\n'
                f'  DESCRIPCION = "Foto: {foto_obj[0].name}" :>\n'
                f'FIN_PARADA :>',
                language="text",
            )
elif not imagenes_validas:
    st.caption("Sube al menos una imagen arriba para probar cómo se llama junto a un lugar o hotel.")

# ==========================================================
# 4. BUSCADOR DE HOTELES Y LUGARES (lugares_puno_osm.csv)
# ==========================================================
st.divider()
st.subheader("🏨 Lugares y Hoteles de Puno (`lugares_puno_osm.csv`)")

if not todos_lugares:
    st.info("No se encontró `lugares_puno_osm.csv` ni `hoteles_puno.json`.")
else:
    f1, f2 = st.columns([2, 1])
    with f1:
        busqueda = st.text_input("🔍 Buscar lugar o hotel por nombre", placeholder="Ej. Hotel, Uros, Munay Tambo...")
    with f2:
        categorias = sorted({str(l.get("categoria", "Lugar")) for l in todos_lugares})
        cat_sel = st.selectbox("Categoría", ["Todas"] + categorias)

    filtrados = [
        l
        for l in todos_lugares
        if (not busqueda.strip() or busqueda.strip().lower() in l["nombre"].lower())
        and (cat_sel == "Todas" or l.get("categoria") == cat_sel)
    ]

    st.caption(f"Mostrando **{min(len(filtrados), 18)}** de **{len(filtrados)}** resultado(s).")
    cols_h = st.columns(3)
    for idx, item in enumerate(filtrados[:18]):
        nom_i = item["nombre"]
        slug_i = normalizar_nombre(nom_i)
        with cols_h[idx % 3]:
            with st.container(border=True):
                if slug_i in mapa_fotos_por_slug:
                    arch_i, img_i = mapa_fotos_por_slug[slug_i]
                    mostrar_imagen(img_i)
                    st.caption(f"📄 `{arch_i.name}`")
                st.markdown(f"**{nom_i}**")
                st.caption(f"{item.get('categoria', '')} · 📍 `{item['latitud']}, {item['longitud']}`")
