"""
Analizador Semántico e Intérprete de Ejecución Cartográfica de TOUR-LANG.
Valida las reglas sensibles al contexto (unicidad, tipos, rangos como [0, 100],
coherencia espacial origen-paradas-destino) y construye el modelo ejecutable del mapa.
"""

import csv
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from .lexico import (
    ALLAVE_CUAD, CADENA, CLLAVE_CUAD, COMA, COSTO, DESCRIPCION, DESTINO,
    DISTANCIA, DISTINTO, DURACION, FIN, FIN_CODIGO, FIN_PARADA, FIN_RUTA,
    ID, IGUAL, IGUALDAD, INICIO_PARADA, INICIO_RUTA, MAYOR, MAYOR_IGUAL,
    MENOR, MENOR_IGUAL, MOSTRAR, MOSTRAR_RUTA, NUM, ORIGEN,
    PROBABILIDAD_LLUVIA, PRONOSTICO, RECOMENDAR, SI, SINO, TEMPERATURA,
    TERMINADOR, TIPO, TRANSPORTE, UBICACION, VISTA, Token,
)

# Catálogo geográfico oficial de localidades turísticas del Altiplano y Región Puno
CATALOGO_LUGARES_PUNO: Dict[str, Tuple[float, float]] = {
    "PUNO": (-15.8402, -70.0219),
    "SILLUSTANI": (-15.7230, -70.1470),
    "UROS": (-15.8188, -69.9722),
    "ISLAS UROS": (-15.8330, -69.9660),
    "TAQUILE": (-15.7719, -69.6842),
    "AMANTANI": (-15.6619, -69.7192),
    "CHUCUITO": (-15.8940, -69.8890),
    "JULI": (-16.2125, -69.4594),
    "POMATA": (-16.2650, -69.2931),
    "YUNGUYO": (-16.2447, -69.0919),
    "KASANI": (-16.2241, -69.0958),
    "COPACABANA": (-16.1664, -69.0861),
    "ARAMU MURU": (-16.1150, -69.4250),
    "ATUNCOLLA": (-15.6897, -70.1469),
    "UMAYO": (-15.7369, -70.1683),
    "JULIACA": (-15.4997, -70.1333),
    "CABANILLAS": (-15.6394, -70.3514),
    "LAMPA": (-15.3620, -70.3650),
    "PUCARA": (-15.0410, -70.3700),
    "AYAVIRI": (-14.8819, -70.5897),
    "TINAJANI": (-14.9330, -70.5660),
    "CANON DE TINAJANI": (-14.9330, -70.5660),
    "CAPACHICA": (-15.6425, -69.8331),
    "LLACHON": (-15.7222, -69.7764),
    "AZANGARO": (-14.9086, -70.1961),
    "ILAVE": (-16.0869, -69.6383),
    "DESAGUADERO": (-16.5656, -69.0417),
}

TIPOS_PERMITIDOS = {
    "CULTURAL", "HISTORICO", "ARQUEOLOGICO", "NATURAL",
    "VIVENCIAL", "RELIGIOSO", "ARQUITECTONICO", "MISTICO",
    "ECOLOGICO", "GASTRONOMICO",
}
VISTAS_PERMITIDAS = {"MAPA", "3D", "SATELITE"}
TRANSPORTES_PERMITIDOS = {
    "BUS", "LANCHA", "AUTO", "MINIVAN", "CAMINATA", "BICICLETA", "TREN", "BOTE"
}
PRONOSTICOS_PERMITIDOS = {
    "SOLEADO", "NUBLADO", "LLUVIOSO", "DESPEJADO", "VENTOSO", "FRIO", "TEMPLADO"
}

# Límites geográficos aproximados de la Región Puno
PUNO_LAT_MIN, PUNO_LAT_MAX = -17.5, -13.0
PUNO_LON_MIN, PUNO_LON_MAX = -71.5, -68.5

_PROYECTO_ROOT = Path(__file__).resolve().parent.parent
_RUTA_PRUEBA_IMAGENES = _PROYECTO_ROOT / "prueba_imagenes"
_ARCHIVOS_LUGARES_EXTRA = (
    _RUTA_PRUEBA_IMAGENES / "lugares_extra.json",
    _RUTA_PRUEBA_IMAGENES / "hoteles_puno.json",
)
_ARCHIVOS_LUGARES_CSV = (
    _PROYECTO_ROOT / "lugares_puno_osm.csv",
    _RUTA_PRUEBA_IMAGENES / "lugares_puno_osm.csv",
)


class AnalizadorSemantico:
    """Ejecuta las validaciones semánticas sobre la secuencia sintácticamente válida de tokens."""

    def __init__(self, tokens: List[Token]) -> None:
        self.tokens = [t for t in tokens if t.token != FIN_CODIGO]
        self.errores: List[Dict[str, Any]] = []
        self.advertencias: List[str] = []
        self.tabla_simbolos: List[Dict[str, Any]] = []
        self.modelo_ruta: Dict[str, Any] = {
            "nombre": "",
            "origen": "",
            "origen_coords": None,
            "destino": "",
            "destino_coords": None,
            "paradas": [],
            "globales": {},
            "condicionales": [],
            "mensajes_salida": [],
            "mostrar_ruta": False,
            "vista_predominante": "MAPA",
        }

    def _agregar_error(self, linea: int, sentencia: str, mensaje: str) -> None:
        self.errores.append({
            "Línea": linea,
            "Sentencia": sentencia,
            "Error Semántico": mensaje,
        })

    def _es_coordenada_puno(self, lat: float, lon: float) -> bool:
        return PUNO_LAT_MIN <= lat <= PUNO_LAT_MAX and PUNO_LON_MIN <= lon <= PUNO_LON_MAX

    def _cargar_lugares_desde_json(self, ruta: Path) -> Dict[str, Tuple[float, float]]:
        lugares: Dict[str, Tuple[float, float]] = {}
        if not ruta.exists():
            return lugares
        try:
            datos = json.loads(ruta.read_text(encoding="utf-8"))
        except (OSError, ValueError, TypeError):
            return lugares

        if isinstance(datos, list):
            for item in datos:
                if not isinstance(item, dict):
                    continue
                nombre = str(item.get("nombre", "")).strip().upper()
                lat = item.get("latitud")
                lon = item.get("longitud")
                if nombre and isinstance(lat, (int, float)) and isinstance(lon, (int, float)):
                    lugares[nombre] = (float(lat), float(lon))
        elif isinstance(datos, dict):
            for k, v in datos.items():
                nombre = str(k).strip().upper()
                if not nombre:
                    continue
                if isinstance(v, dict):
                    lat, lon = v.get("latitud"), v.get("longitud")
                    if isinstance(lat, (int, float)) and isinstance(lon, (int, float)):
                        lugares[nombre] = (float(lat), float(lon))
                elif isinstance(v, (list, tuple)) and len(v) == 2:
                    lat, lon = v[0], v[1]
                    if isinstance(lat, (int, float)) and isinstance(lon, (int, float)):
                        lugares[nombre] = (float(lat), float(lon))
        return lugares

    def _cargar_lugares_desde_csv(self, ruta: Path) -> Dict[str, Tuple[float, float]]:
        lugares: Dict[str, Tuple[float, float]] = {}
        if not ruta.exists():
            return lugares
        try:
            with ruta.open("r", encoding="utf-8", newline="") as f:
                lector = csv.DictReader(f)
                for fila in lector:
                    nombre = str(fila.get("nombre", "")).strip().upper()
                    lat_raw = fila.get("latitud")
                    lon_raw = fila.get("longitud")
                    if not nombre or lat_raw is None or lon_raw is None:
                        continue
                    try:
                        lat = float(str(lat_raw).strip())
                        lon = float(str(lon_raw).strip())
                    except ValueError:
                        continue
                    if self._es_coordenada_puno(lat, lon):
                        lugares[nombre] = (lat, lon)
        except OSError:
            return lugares
        return lugares

    def _buscar_en_diccionario(
        self, clave: str, diccionario: Dict[str, Tuple[float, float]], permitir_parcial: bool = True
    ) -> Optional[Tuple[float, float]]:
        if clave in diccionario:
            return diccionario[clave]
        if permitir_parcial and len(clave) >= 4:
            for k, coords in diccionario.items():
                if k in clave or clave in k:
                    return coords
        return None

    def _resolver_coordenadas(self, nombre_lugar: str) -> Optional[Tuple[float, float]]:
        clave = nombre_lugar.strip().upper()
        if not clave:
            return None

        # 1. Buscar en el catálogo oficial de Puno
        coords = self._buscar_en_diccionario(clave, CATALOGO_LUGARES_PUNO)
        if coords is not None:
            return coords

        # 2. Buscar en lugares_extra.json y hoteles_puno.json
        for ruta_json in _ARCHIVOS_LUGARES_EXTRA:
            extra = self._cargar_lugares_desde_json(ruta_json)
            coords = self._buscar_en_diccionario(clave, extra)
            if coords is not None:
                return coords

        # 3. Buscar en lugares_puno_osm.csv (hoteles y lugares OSM de Puno)
        for ruta_csv in _ARCHIVOS_LUGARES_CSV:
            osm = self._cargar_lugares_desde_csv(ruta_csv)
            coords = self._buscar_en_diccionario(clave, osm)
            if coords is not None:
                return coords

        return None

    def _es_numero(self, valor_tok: Token) -> Optional[float]:
        if valor_tok.token != NUM or valor_tok.lexema is None:
            return None
        try:
            return float(valor_tok.lexema)
        except ValueError:
            return None

    def analizar(self) -> bool:
        i = 0
        n = len(self.tokens)
        nombres_paradas_vistos = set()
        atributos_globales_vistos = set()
        lugares_pendientes: List[Tuple[int, str, str]] = []

        while i < n:
            tok = self.tokens[i]

            # 1. INICIO_RUTA "nombre" :>
            if tok.token == INICIO_RUTA:
                nombre_tok = self.tokens[i + 1]
                nombre = (nombre_tok.lexema or "").strip()
                if not nombre:
                    self._agregar_error(tok.linea, 'INICIO_RUTA "" :>', "El nombre de la ruta está vacío.")
                self.modelo_ruta["nombre"] = nombre
                self.tabla_simbolos.append({
                    "Ámbito": "Global",
                    "Símbolo": "INICIO_RUTA",
                    "Tipo": "CADENA",
                    "Valor": nombre,
                    "Línea": tok.linea,
                })
                i += 3
                continue

            # 2. ORIGEN "lugar" :>
            if tok.token == ORIGEN:
                lugar_tok = self.tokens[i + 1]
                lugar = (lugar_tok.lexema or "").strip()
                if not lugar:
                    self._agregar_error(tok.linea, 'ORIGEN "" :>', "El lugar de origen está vacío.")
                coords = self._resolver_coordenadas(lugar)
                if lugar and coords is None:
                    lugares_pendientes.append((tok.linea, "ORIGEN", lugar))
                self.modelo_ruta["origen"] = lugar
                self.modelo_ruta["origen_coords"] = coords
                self.tabla_simbolos.append({
                    "Ámbito": "Global",
                    "Símbolo": "ORIGEN",
                    "Tipo": "LUGAR",
                    "Valor": f"{lugar} {coords or ''}",
                    "Línea": tok.linea,
                })
                i += 3
                continue

            # 3. Bloque INICIO_PARADA "nombre" :> ... FIN_PARADA :>
            if tok.token == INICIO_PARADA:
                nom_tok = self.tokens[i + 1]
                nom_parada = (nom_tok.lexema or "").strip()
                lin_parada = tok.linea
                if not nom_parada:
                    self._agregar_error(lin_parada, 'INICIO_PARADA "" :>', "El nombre de la parada está vacío.")
                elif nom_parada.upper() in nombres_paradas_vistos:
                    self._agregar_error(
                        lin_parada,
                        f'INICIO_PARADA "{nom_parada}" :>',
                        f"La parada '{nom_parada}' está repetida dentro de la misma ruta.",
                    )
                else:
                    nombres_paradas_vistos.add(nom_parada.upper())

                parada_info: Dict[str, Any] = {
                    "nombre": nom_parada,
                    "atributos": {},
                    "coords": self._resolver_coordenadas(nom_parada),
                    "linea": lin_parada,
                }
                atributos_vistos = set()
                i += 3

                while i < n and self.tokens[i].token != FIN_PARADA:
                    attr_tok = self.tokens[i]
                    attr_nom = attr_tok.nombre
                    lin_attr = attr_tok.linea

                    if attr_nom in atributos_vistos:
                        self._agregar_error(
                            lin_attr,
                            f"{attr_nom} = ... :>",
                            f"El atributo '{attr_nom}' está repetido en la parada '{nom_parada}'.",
                        )
                    atributos_vistos.add(attr_nom)

                    # Avanzar attr y '='
                    i += 2
                    if self.tokens[i].token == ALLAVE_CUAD:
                        # Lista [x, y]
                        i += 1
                        elementos: List[Token] = []
                        while i < n and self.tokens[i].token != CLLAVE_CUAD:
                            if self.tokens[i].token != COMA:
                                elementos.append(self.tokens[i])
                            i += 1
                        i += 1  # consumir ']'
                        i += 1  # consumir ':>'

                        if attr_tok.token != UBICACION:
                            self._agregar_error(
                                lin_attr,
                                f"{attr_nom} = [...] :>",
                                f"El atributo '{attr_nom}' no admite listas de coordenadas; solo UBICACION acepta [lat, lon].",
                            )
                        elif len(elementos) != 2:
                            self._agregar_error(
                                lin_attr,
                                f"UBICACION = [...] :>",
                                f"UBICACION requiere exactamente 2 coordenadas [latitud, longitud], pero recibió {len(elementos)}.",
                            )
                        else:
                            lat = self._es_numero(elementos[0])
                            lon = self._es_numero(elementos[1])
                            if lat is None or lon is None:
                                self._agregar_error(
                                    lin_attr,
                                    "UBICACION = [x, y] :>",
                                    "Las coordenadas de UBICACION deben ser valores numéricos.",
                                )
                            elif not (-90.0 <= lat <= 90.0 and -180.0 <= lon <= 180.0):
                                self._agregar_error(
                                    lin_attr,
                                    f"UBICACION = [{lat}, {lon}] :>",
                                    "Coordenadas geográficas fuera de rango válido (latitud [-90,90], longitud [-180,180]).",
                                )
                            else:
                                parada_info["coords"] = (lat, lon)
                                parada_info["atributos"]["UBICACION"] = [lat, lon]
                                self.tabla_simbolos.append({
                                    "Ámbito": f"Parada:{nom_parada}",
                                    "Símbolo": "UBICACION",
                                    "Tipo": "COORDENADAS",
                                    "Valor": f"[{lat}, {lon}]",
                                    "Línea": lin_attr,
                                })
                    else:
                        val_tok = self.tokens[i]
                        i += 2  # consumir valor y ':>'
                        self._validar_atributo_parada(nom_parada, attr_tok, val_tok, parada_info)

                # En FIN_PARADA :>
                lin_fin_p = self.tokens[i].linea if i < n else lin_parada
                if "TIPO" not in parada_info["atributos"] and "DESCRIPCION" not in parada_info["atributos"] and len(parada_info["atributos"]) == 0:
                    self._agregar_error(
                        lin_fin_p,
                        "FIN_PARADA :>",
                        f"La parada '{nom_parada}' no contiene los atributos mínimos obligatorios (ej. TIPO o DESCRIPCION).",
                    )
                if parada_info["coords"] is None:
                    # Coordenada aproximada por defecto en Puno si el usuario declaró una parada local nueva con atributos válidos
                    parada_info["coords"] = (-15.8402, -70.0219)

                vista_p = parada_info["atributos"].get("VISTA")
                if vista_p in ("3D", "SATELITE"):
                    self.modelo_ruta["vista_predominante"] = vista_p

                self.modelo_ruta["paradas"].append(parada_info)
                i += 2  # consumir FIN_PARADA y ':>'
                continue

            # 4. DESTINO "lugar" :>
            if tok.token == DESTINO:
                dest_tok = self.tokens[i + 1]
                destino = (dest_tok.lexema or "").strip()
                if not destino:
                    self._agregar_error(tok.linea, 'DESTINO "" :>', "El lugar de destino está vacío.")
                coords = self._resolver_coordenadas(destino)
                if destino and coords is None:
                    lugares_pendientes.append((tok.linea, "DESTINO", destino))
                if (
                    destino
                    and destino.upper() == self.modelo_ruta["origen"].upper()
                    and len(self.modelo_ruta["paradas"]) == 0
                ):
                    self._agregar_error(
                        tok.linea,
                        f'DESTINO "{destino}" :>',
                        "El destino coincide con el origen sin ninguna parada intermedia definida.",
                    )
                self.modelo_ruta["destino"] = destino
                self.modelo_ruta["destino_coords"] = coords
                self.tabla_simbolos.append({
                    "Ámbito": "Global",
                    "Símbolo": "DESTINO",
                    "Tipo": "LUGAR",
                    "Valor": f"{destino} {coords or ''}",
                    "Línea": tok.linea,
                })
                i += 3
                continue

            # 5. Atributos globales: COSTO, TRANSPORTE, DISTANCIA, DURACION
            if tok.token in (COSTO, TRANSPORTE, DISTANCIA, DURACION):
                attr_nom = tok.nombre
                val_tok = self.tokens[i + 2]
                if attr_nom in atributos_globales_vistos:
                    self._agregar_error(
                        tok.linea,
                        f"{attr_nom} = {val_tok.lexema} :>",
                        f"El atributo global '{attr_nom}' está repetido.",
                    )
                atributos_globales_vistos.add(attr_nom)
                self._validar_atributo_global(tok, val_tok)
                i += 4
                continue

            # 6. MOSTRAR_RUTA :>
            if tok.token == MOSTRAR_RUTA:
                if not self.modelo_ruta["origen"] or not self.modelo_ruta["destino"]:
                    self._agregar_error(
                        tok.linea,
                        "MOSTRAR_RUTA :>",
                        "Se intenta mostrar la ruta antes de definir sus datos mínimos (origen y destino).",
                    )
                self.modelo_ruta["mostrar_ruta"] = True
                i += 2
                continue

            # 7. Condicional SI var op valor :> ... [SINO :>] ... FIN :>
            if tok.token == SI:
                i = self._procesar_condicional(i)
                continue

            # 8. FIN_RUTA :>
            if tok.token == FIN_RUTA:
                if not self.modelo_ruta["origen"] or not self.modelo_ruta["destino"]:
                    self._agregar_error(
                        tok.linea,
                        "FIN_RUTA :>",
                        "La ruta está incompleta: falta origen o destino.",
                    )
                i += 2
                continue

            i += 1

        # Verificar lugares en ORIGEN / DESTINO que no estaban en catálogo, lugares_extra.json ni hoteles_puno.json
        for lin_lug, rol_lug, nom_lug in lugares_pendientes:
            coords_puno_parada: Optional[Tuple[float, float]] = None
            # Priorizar una parada con el mismo nombre y UBICACION válida en Puno
            for p in self.modelo_ruta["paradas"]:
                ubic = p["atributos"].get("UBICACION")
                if (
                    p["nombre"].strip().upper() == nom_lug.strip().upper()
                    and isinstance(ubic, list)
                    and len(ubic) == 2
                    and self._es_coordenada_puno(ubic[0], ubic[1])
                ):
                    coords_puno_parada = (float(ubic[0]), float(ubic[1]))
                    break

            # Si no coincide por nombre, aceptar si alguna parada o la ruta trae UBICACION válida dentro de Puno
            if coords_puno_parada is None:
                for p in self.modelo_ruta["paradas"]:
                    ubic = p["atributos"].get("UBICACION")
                    if isinstance(ubic, list) and len(ubic) == 2 and self._es_coordenada_puno(ubic[0], ubic[1]):
                        coords_puno_parada = (float(ubic[0]), float(ubic[1]))
                        break

            if coords_puno_parada is not None:
                clave_coord = "origen_coords" if rol_lug == "ORIGEN" else "destino_coords"
                self.modelo_ruta[clave_coord] = coords_puno_parada
                for sym in self.tabla_simbolos:
                    if sym.get("Ámbito") == "Global" and sym.get("Símbolo") == rol_lug:
                        sym["Valor"] = f"{nom_lug} {coords_puno_parada}"
            else:
                self._agregar_error(
                    lin_lug,
                    f'{rol_lug} "{nom_lug}" :>',
                    f"El lugar '{nom_lug}' en {rol_lug} no se encontró en CATALOGO_LUGARES_PUNO, lugares_extra.json ni hoteles_puno.json, y no cuenta con UBICACION = [lat, lon] válida dentro de la región Puno (lat [{PUNO_LAT_MIN}, {PUNO_LAT_MAX}], lon [{PUNO_LON_MIN}, {PUNO_LON_MAX}]). Regístralo en prueba_imagenes/lugares_extra.json desde prueba_imagenes.py o agrega UBICACION = [lat, lon] :> en una parada.",
                )

        return len(self.errores) == 0

    def _validar_atributo_parada(
        self, nom_parada: str, attr_tok: Token, val_tok: Token, parada_info: Dict[str, Any]
    ) -> None:
        cod = attr_tok.token
        nom = attr_tok.nombre
        lin = attr_tok.linea
        lex = val_tok.lexema or ""

        if cod == TIPO:
            if val_tok.token != CADENA or lex.upper() not in TIPOS_PERMITIDOS:
                self._agregar_error(
                    lin,
                    f'TIPO = "{lex}" :>',
                    f"El tipo '{lex}' no es válido. Permitidos: {', '.join(sorted(TIPOS_PERMITIDOS))}.",
                )
            else:
                parada_info["atributos"]["TIPO"] = lex.upper()

        elif cod == DESCRIPCION:
            if val_tok.token != CADENA or not lex.strip():
                self._agregar_error(lin, 'DESCRIPCION = "" :>', "La descripción de la parada está vacía o no es texto.")
            else:
                parada_info["atributos"]["DESCRIPCION"] = lex

        elif cod == UBICACION:
            self._agregar_error(
                lin,
                f"UBICACION = {lex} :>",
                "UBICACION debe declararse como una lista de coordenadas [latitud, longitud].",
            )

        elif cod == VISTA:
            if val_tok.token != CADENA or lex.upper() not in VISTAS_PERMITIDAS:
                self._agregar_error(
                    lin,
                    f'VISTA = "{lex}" :>',
                    f"La vista '{lex}' no es válida. Permitidas: MAPA, 3D, SATELITE.",
                )
            else:
                parada_info["atributos"]["VISTA"] = lex.upper()

        elif cod in (COSTO, DISTANCIA, DURACION):
            num = self._es_numero(val_tok)
            if num is None or num < 0:
                self._agregar_error(
                    lin,
                    f"{nom} = {lex} :>",
                    f"El atributo '{nom}' debe ser numérico y no negativo (>= 0).",
                )
            else:
                parada_info["atributos"][nom] = num

        elif cod == TRANSPORTE:
            if val_tok.token != CADENA or lex.upper() not in TRANSPORTES_PERMITIDOS:
                self._agregar_error(
                    lin,
                    f'TRANSPORTE = "{lex}" :>',
                    f"El medio de transporte '{lex}' no es válido en el dominio turístico.",
                )
            else:
                parada_info["atributos"]["TRANSPORTE"] = lex.upper()

        elif cod == PRONOSTICO:
            if val_tok.token != CADENA or lex.upper() not in PRONOSTICOS_PERMITIDOS:
                self._agregar_error(
                    lin,
                    f'PRONOSTICO = "{lex}" :>',
                    f"El pronóstico '{lex}' no tiene un valor permitido ({', '.join(sorted(PRONOSTICOS_PERMITIDOS))}).",
                )
            else:
                parada_info["atributos"]["PRONOSTICO"] = lex.upper()

        elif cod == TEMPERATURA:
            num = self._es_numero(val_tok)
            if num is None or not (-30.0 <= num <= 50.0):
                self._agregar_error(
                    lin,
                    f"TEMPERATURA = {lex} :>",
                    "La temperatura debe ser un valor numérico válido en °C (entre -30 y 50).",
                )
            else:
                parada_info["atributos"]["TEMPERATURA"] = num

        elif cod == PROBABILIDAD_LLUVIA:
            num = self._es_numero(val_tok)
            if num is None or not (0.0 <= num <= 100.0):
                self._agregar_error(
                    lin,
                    f"PROBABILIDAD_LLUVIA = {lex} :>",
                    f"PROBABILIDAD_LLUVIA = {lex} está fuera del rango semántico permitido [0, 100].",
                )
            else:
                parada_info["atributos"]["PROBABILIDAD_LLUVIA"] = num

        if nom in parada_info["atributos"]:
            self.tabla_simbolos.append({
                "Ámbito": f"Parada:{nom_parada}",
                "Símbolo": nom,
                "Tipo": val_tok.nombre,
                "Valor": str(parada_info["atributos"][nom]),
                "Línea": lin,
            })

    def _validar_atributo_global(self, attr_tok: Token, val_tok: Token) -> None:
        cod = attr_tok.token
        nom = attr_tok.nombre
        lin = attr_tok.linea
        lex = val_tok.lexema or ""

        if cod in (COSTO, DISTANCIA, DURACION):
            num = self._es_numero(val_tok)
            if num is None or num < 0:
                self._agregar_error(
                    lin,
                    f"{nom} = {lex} :> (global)",
                    f"El atributo global '{nom}' debe ser numérico y no negativo (>= 0).",
                )
            else:
                # Coherencia con suma de paradas si existen valores parciales
                suma_paradas = sum(
                    float(p["atributos"].get(nom, 0.0)) for p in self.modelo_ruta["paradas"]
                )
                if suma_paradas > 0 and num < suma_paradas:
                    self._agregar_error(
                        lin,
                        f"{nom} = {lex} :> (global)",
                        f"El valor global de {nom} ({num}) es inconsistente (menor que la suma de las paradas: {suma_paradas}).",
                    )
                else:
                    self.modelo_ruta["globales"][nom] = num
                    self.tabla_simbolos.append({
                        "Ámbito": "Global",
                        "Símbolo": nom,
                        "Tipo": "NUMERO",
                        "Valor": str(num),
                        "Línea": lin,
                    })
        elif cod == TRANSPORTE:
            if val_tok.token != CADENA or lex.upper() not in TRANSPORTES_PERMITIDOS:
                self._agregar_error(
                    lin,
                    f'TRANSPORTE = "{lex}" :> (global)',
                    f"El medio de transporte global '{lex}' no es válido.",
                )
            else:
                self.modelo_ruta["globales"]["TRANSPORTE"] = lex.upper()
                self.tabla_simbolos.append({
                    "Ámbito": "Global",
                    "Símbolo": "TRANSPORTE",
                    "Tipo": "CADENA",
                    "Valor": lex.upper(),
                    "Línea": lin,
                })

    def _obtener_valor_variable_condicion(self, var_nom: str) -> Optional[float]:
        if var_nom in self.modelo_ruta["globales"]:
            val = self.modelo_ruta["globales"][var_nom]
            if isinstance(val, (int, float)):
                return float(val)
        # Buscar en la última parada que lo haya definido
        for p in reversed(self.modelo_ruta["paradas"]):
            if var_nom in p["atributos"]:
                val = p["atributos"][var_nom]
                if isinstance(val, (int, float)):
                    return float(val)
        return None

    def _evaluar_comparacion(self, izq: float, op_tok: int, der: float) -> bool:
        if op_tok == MENOR:
            return izq < der
        if op_tok == MENOR_IGUAL:
            return izq <= der
        if op_tok == MAYOR:
            return izq > der
        if op_tok == MAYOR_IGUAL:
            return izq >= der
        if op_tok == IGUALDAD:
            return izq == der
        if op_tok == DISTINTO:
            return izq != der
        return False

    def _procesar_condicional(self, i: int) -> int:
        lin_si = self.tokens[i].linea
        var_tok = self.tokens[i + 1]
        op_tok = self.tokens[i + 2]
        val_tok = self.tokens[i + 3]

        var_nom = var_tok.nombre
        val_der = self._es_numero(val_tok)
        val_izq = self._obtener_valor_variable_condicion(var_nom)

        condicion_valida = True
        if val_der is None:
            self._agregar_error(
                lin_si,
                f"SI {var_nom} {op_tok.lexema} {val_tok.lexema} :>",
                f"Los tipos no coinciden en la condición: '{var_nom}' es numérico y no puede compararse con '{val_tok.lexema}'.",
            )
            condicion_valida = False
        elif val_izq is None:
            self._agregar_error(
                lin_si,
                f"SI {var_nom} {op_tok.lexema} {val_tok.lexema} :>",
                f"La variable '{var_nom}' usada en el condicional SI no fue declarada previamente en la ruta.",
            )
            condicion_valida = False

        i += 5  # saltar SI var op val :>

        acc_si: List[Tuple[str, str, int]] = []
        acc_sino: List[Tuple[str, str, int]] = []
        en_sino = False

        while i < len(self.tokens) and self.tokens[i].token != FIN:
            t_act = self.tokens[i]
            if t_act.token == SINO:
                en_sino = True
                i += 2  # SINO :>
                continue
            if t_act.token in (RECOMENDAR, MOSTRAR):
                txt_tok = self.tokens[i + 1]
                texto = (txt_tok.lexema or "").strip()
                if not texto:
                    self._agregar_error(
                        t_act.linea,
                        f'{t_act.nombre} "" :>',
                        f"El texto de la instrucción {t_act.nombre} está vacío.",
                    )
                destino_lista = acc_sino if en_sino else acc_si
                destino_lista.append((t_act.nombre, texto, t_act.linea))
                i += 3
                continue
            i += 1

        if len(acc_si) == 0:
            self._agregar_error(lin_si, "SI ... FIN :>", "La rama principal del condicional SI no contiene sentencias.")
        if en_sino and len(acc_sino) == 0:
            self._agregar_error(lin_si, "SINO :> FIN :>", "La rama SINO fue declarada pero no contiene sentencias.")

        if condicion_valida and val_izq is not None and val_der is not None:
            resultado_bool = self._evaluar_comparacion(val_izq, op_tok.token, val_der)
            rama_elegida = acc_si if resultado_bool else acc_sino
            self.modelo_ruta["condicionales"].append({
                "expresion": f"{var_nom} ({val_izq}) {op_tok.lexema} {val_der}",
                "resultado": resultado_bool,
            })
            for tipo_msg, txt_msg, _ in rama_elegida:
                if txt_msg:
                    self.modelo_ruta["mensajes_salida"].append({
                        "tipo": tipo_msg,
                        "texto": txt_msg,
                    })

        return i + 2  # consumir FIN y ':>'
