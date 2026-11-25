"""
Analizador Léxico de TOUR-LANG basado en Autómata Finito Determinista (AFD).
Implementa los 37 tipos de tokens oficiales, reconocimiento Maximal Munch
y detección de los 5 estados de error léxico (E1 a E5).
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

# Palabras reservadas (0 - 22)
INICIO_RUTA         = 0
FIN_RUTA            = 1
ORIGEN              = 2
DESTINO             = 3
INICIO_PARADA       = 4
FIN_PARADA          = 5
TIPO                = 6
DESCRIPCION         = 7
UBICACION           = 8
VISTA               = 9
COSTO               = 10
TRANSPORTE          = 11
DISTANCIA           = 12
DURACION            = 13
PRONOSTICO          = 14
TEMPERATURA         = 15
PROBABILIDAD_LLUVIA = 16
SI                  = 17
SINO                = 18
FIN                 = 19
RECOMENDAR          = 20
MOSTRAR             = 21
MOSTRAR_RUTA        = 22

# Símbolos, separadores y operadores (23 - 33)
IGUAL               = 23  # =
COMA                = 24  # ,
ALLAVE_CUAD         = 25  # [
CLLAVE_CUAD         = 26  # ]
MENOR               = 27  # <
MAYOR               = 28  # >
MENOR_IGUAL         = 29  # <=
MAYOR_IGUAL         = 30  # >=
IGUALDAD            = 31  # ==
DISTINTO            = 32  # !=
TERMINADOR          = 33  # :>

# Tokens dinámicos (34 - 36)
ID                  = 34
NUM                 = 35
CADENA              = 36

# Tokens de control interno
FIN_CODIGO          = 666
ERROR               = 999


@dataclass
class Token:
    token: int
    lexema: Optional[str]
    linea: int
    columna: int
    nombre: str
    categoria: str
    rama_afd: str = ""
    codigo_error_afd: Optional[str] = None
    detalle_error: Optional[str] = None


class TablaLexica:
    """Tabla léxica fija con las 23 palabras reservadas y 11 operadores/delimitadores."""

    def __init__(self) -> None:
        self._por_token: Dict[int, Dict] = {}
        self._por_lexema: Dict[str, Dict] = {}
        self._nombres_dinamicos = {
            ID: ("IDENTIFICADOR", "identificador"),
            NUM: ("NUMERO", "numero"),
            CADENA: ("CADENA", "cadena"),
            FIN_CODIGO: ("FIN_CODIGO", "control"),
            ERROR: ("ERROR", "error_lexico"),
        }
        self._inicializar()

    def _agregar(self, codigo: int, lexema: str, categoria: str, nombre: str = "") -> None:
        info = {
            "token": codigo,
            "lexema": lexema,
            "categoria": categoria,
            "nombre": nombre if nombre else lexema.upper(),
        }
        self._por_token[codigo] = info
        self._por_lexema[lexema] = info

    def _inicializar(self) -> None:
        reservadas = [
            (INICIO_RUTA, "INICIO_RUTA"),
            (FIN_RUTA, "FIN_RUTA"),
            (ORIGEN, "ORIGEN"),
            (DESTINO, "DESTINO"),
            (INICIO_PARADA, "INICIO_PARADA"),
            (FIN_PARADA, "FIN_PARADA"),
            (TIPO, "TIPO"),
            (DESCRIPCION, "DESCRIPCION"),
            (UBICACION, "UBICACION"),
            (VISTA, "VISTA"),
            (COSTO, "COSTO"),
            (TRANSPORTE, "TRANSPORTE"),
            (DISTANCIA, "DISTANCIA"),
            (DURACION, "DURACION"),
            (PRONOSTICO, "PRONOSTICO"),
            (TEMPERATURA, "TEMPERATURA"),
            (PROBABILIDAD_LLUVIA, "PROBABILIDAD_LLUVIA"),
            (SI, "SI"),
            (SINO, "SINO"),
            (FIN, "FIN"),
            (RECOMENDAR, "RECOMENDAR"),
            (MOSTRAR, "MOSTRAR"),
            (MOSTRAR_RUTA, "MOSTRAR_RUTA"),
        ]
        for cod, lex in reservadas:
            self._agregar(cod, lex, "palabra_reservada")

        simbolos = [
            (IGUAL, "=", "operador", "IGUAL"),
            (COMA, ",", "separador", "COMA"),
            (ALLAVE_CUAD, "[", "simbolo", "ALLAVE_CUADRADA"),
            (CLLAVE_CUAD, "]", "simbolo", "CLLAVE_CUADRADA"),
            (MENOR, "<", "operador_relacional", "MENOR"),
            (MAYOR, ">", "operador_relacional", "MAYOR"),
            (MENOR_IGUAL, "<=", "operador_relacional", "MENOR_IGUAL"),
            (MAYOR_IGUAL, ">=", "operador_relacional", "MAYOR_IGUAL"),
            (IGUALDAD, "==", "operador_relacional", "IGUALDAD"),
            (DISTINTO, "!=", "operador_relacional", "DISTINTO"),
            (TERMINADOR, ":>", "terminador", "TERMINADOR"),
        ]
        for cod, lex, cat, nom in simbolos:
            self._agregar(cod, lex, cat, nom)

    def buscar_por_lexema(self, lexema: str) -> Optional[Dict]:
        return self._por_lexema.get(lexema)

    def buscar_por_token(self, token: int) -> Optional[Dict]:
        return self._por_token.get(token)

    def nombre_de(self, token: int) -> str:
        if token in self._nombres_dinamicos:
            return self._nombres_dinamicos[token][0]
        info = self._por_token.get(token)
        return info["nombre"] if info else f"TOKEN_{token}"

    def categoria_de(self, token: int) -> str:
        if token in self._nombres_dinamicos:
            return self._nombres_dinamicos[token][1]
        info = self._por_token.get(token)
        return info["categoria"] if info else "desconocido"

    def buscar_lexema_mas_largo(self, codigo: str, posicion: int) -> Optional[Dict]:
        """Principio Maximal Munch para distinguir '=' de '==', '<' de '<=' y ':>'."""
        encontrado = None
        for lexema, datos in self._por_lexema.items():
            if lexema[0].isalpha():
                continue
            lon = len(lexema)
            if codigo[posicion:posicion + lon] == lexema:
                if encontrado is None or lon > encontrado["longitud"]:
                    encontrado = {
                        "token": datos["token"],
                        "lexema": lexema,
                        "categoria": datos["categoria"],
                        "longitud": lon,
                    }
        return encontrado


class Tokenizador:
    """Simula el AFD de 4 ramas (estados q0..q140 y errores E1..E5) sobre el código fuente."""

    def __init__(self, codigo: str, tabla_lexica: Optional[TablaLexica] = None) -> None:
        self.codigo = codigo.replace("\r\n", "\n")
        self.tabla = tabla_lexica or TablaLexica()
        self.indice = 0
        self.linea = 1
        self.columna = 1

    def _fin_codigo(self) -> bool:
        return self.indice >= len(self.codigo)

    def _avanzar(self) -> None:
        if self._fin_codigo():
            return
        if self.codigo[self.indice] == "\n":
            self.linea += 1
            self.columna = 1
        else:
            self.columna += 1
        self.indice += 1

    def _omitir_espacios_y_comentarios(self) -> None:
        while not self._fin_codigo():
            ch = self.codigo[self.indice]
            if ch.isspace():
                self._avanzar()
                continue
            # Soporte de comentarios de línea // ...
            if ch == "/" and self.indice + 1 < len(self.codigo) and self.codigo[self.indice + 1] == "/":
                while not self._fin_codigo() and self.codigo[self.indice] != "\n":
                    self._avanzar()
                continue
            break

    def _crear_token(
        self,
        codigo_tok: int,
        lexema: Optional[str],
        lin: int,
        col: int,
        rama: str,
        err_cod: Optional[str] = None,
        err_msg: Optional[str] = None,
    ) -> Token:
        return Token(
            token=codigo_tok,
            lexema=lexema,
            linea=lin,
            columna=col,
            nombre=self.tabla.nombre_de(codigo_tok),
            categoria=self.tabla.categoria_de(codigo_tok),
            rama_afd=rama,
            codigo_error_afd=err_cod,
            detalle_error=err_msg,
        )

    def get_token(self) -> Token:
        self._omitir_espacios_y_comentarios()

        if self._fin_codigo():
            return self._crear_token(FIN_CODIGO, None, self.linea, self.columna, "EOF")

        lin_ini, col_ini = self.linea, self.columna
        ch = self.codigo[self.indice]

        # RAMA 1: Palabras reservadas e identificadores (q1..q126)
        if ch.isalpha() or ch == "_":
            lexema = []
            while not self._fin_codigo() and (self.codigo[self.indice].isalnum() or self.codigo[self.indice] == "_"):
                lexema.append(self.codigo[self.indice])
                self._avanzar()
            palabra = "".join(lexema)
            elem = self.tabla.buscar_por_lexema(palabra)
            if elem is not None:
                return self._crear_token(elem["token"], palabra, lin_ini, col_ini, "Rama 1 (Reservada)")
            return self._crear_token(ID, palabra, lin_ini, col_ini, "Rama 1 (q126 - ID)")

        # RAMA 2: Cadenas de texto entre comillas dobles (q127..q128 | Error E1)
        if ch == '"':
            self._avanzar()  # consumir comilla inicial
            contenido = []
            while not self._fin_codigo():
                actual = self.codigo[self.indice]
                if actual == '"':
                    self._avanzar()
                    return self._crear_token(CADENA, "".join(contenido), lin_ini, col_ini, "Rama 2 (q128 - Cadena)")
                if actual == "\n":
                    return self._crear_token(
                        ERROR,
                        '"' + "".join(contenido),
                        lin_ini,
                        col_ini,
                        "Rama 2 (Error E1)",
                        "E1",
                        "E1: Cadena de texto sin comilla doble de cierre antes del salto de línea.",
                    )
                contenido.append(actual)
                self._avanzar()
            return self._crear_token(
                ERROR,
                '"' + "".join(contenido),
                lin_ini,
                col_ini,
                "Rama 2 (Error E1)",
                "E1",
                "E1: Cadena de texto sin comilla doble de cierre al llegar al fin del archivo (EOF).",
            )

        # RAMA 3: Números enteros y decimales con signo opcional (q129..q132 | Errores E2, E3)
        if ch == "-" or ch.isdigit():
            lex_num = []
            if ch == "-":
                lex_num.append("-")
                self._avanzar()
                if self._fin_codigo() or not self.codigo[self.indice].isdigit():
                    return self._crear_token(
                        ERROR,
                        "-",
                        lin_ini,
                        col_ini,
                        "Rama 3 (Error E2)",
                        "E2",
                        "E2: Signo negativo '-' no seguido de dígitos numéricos.",
                    )

            puntos = 0
            while not self._fin_codigo():
                c = self.codigo[self.indice]
                if c.isdigit():
                    lex_num.append(c)
                    self._avanzar()
                elif c == ".":
                    puntos += 1
                    lex_num.append(c)
                    self._avanzar()
                    if puntos > 1 or self._fin_codigo() or not self.codigo[self.indice].isdigit():
                        return self._crear_token(
                            ERROR,
                            "".join(lex_num),
                            lin_ini,
                            col_ini,
                            "Rama 3 (Error E3)",
                            "E3",
                            "E3: Número decimal mal formado (punto decimal sin dígitos válidos o múltiples puntos).",
                        )
                else:
                    break
            rama_txt = "Rama 3 (q132 - Decimal)" if puntos == 1 else "Rama 3 (q130 - Entero)"
            return self._crear_token(NUM, "".join(lex_num), lin_ini, col_ini, rama_txt)

        # RAMA 4: Operadores, delimitadores y terminador :> (q133..q140 | Errores E4, E5)
        fijo = self.tabla.buscar_lexema_mas_largo(self.codigo, self.indice)
        if fijo is not None:
            for _ in range(fijo["longitud"]):
                self._avanzar()
            rama_op = "Rama 4 (q140 - Terminador)" if fijo["token"] == TERMINADOR else "Rama 4 (Operador/Símbolo)"
            return self._crear_token(fijo["token"], fijo["lexema"], lin_ini, col_ini, rama_op)

        if ch == ":":
            self._avanzar()
            return self._crear_token(
                ERROR,
                ":",
                lin_ini,
                col_ini,
                "Rama 4 (Error E4)",
                "E4",
                "E4: Carácter ':' sin '>' (el terminador válido en TOUR-LANG es ':>').",
            )

        # Error E5: Carácter fuera del alfabeto
        self._avanzar()
        return self._crear_token(
            ERROR,
            ch,
            lin_ini,
            col_ini,
            "Rama 4 (Error E5)",
            "E5",
            f"E5: Carácter '{ch}' fuera del alfabeto permitido por TOUR-LANG.",
        )

    def tokenizar_todo(self) -> List[Token]:
        tokens: List[Token] = []
        while True:
            tok = self.get_token()
            tokens.append(tok)
            if tok.token in (FIN_CODIGO, ERROR):
                break
        return tokens
