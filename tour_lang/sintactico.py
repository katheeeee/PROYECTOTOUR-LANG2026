"""
Analizador Sintáctico de TOUR-LANG basado en Autómata de Pila Determinista (PDA).
Implementa los 36 estados del modelo JFLAP 7.1 y el alfabeto de pila Γ = {Z, P, A, S}.
"""

from typing import Dict, List, Optional
from .lexico import (
    ALLAVE_CUAD, CADENA, CLLAVE_CUAD, COMA, COSTO, DESCRIPCION, DESTINO,
    DISTANCIA, DISTINTO, DURACION, ERROR, FIN, FIN_CODIGO, FIN_PARADA,
    FIN_RUTA, ID, IGUAL, IGUALDAD, INICIO_PARADA, INICIO_RUTA, MAYOR,
    MAYOR_IGUAL, MENOR, MENOR_IGUAL, MOSTRAR, MOSTRAR_RUTA, NUM, ORIGEN,
    PROBABILIDAD_LLUVIA, PRONOSTICO, RECOMENDAR, SI, SINO, TEMPERATURA,
    TERMINADOR, TIPO, TRANSPORTE, UBICACION, VISTA, TablaLexica, Token,
    Tokenizador,
)


class AnalizadorSintactico:
    ESTADO_INICIAL = "q0"
    ESTADO_FINAL = "qF"
    FONDO_PILA = "Z"

    def __init__(self, codigo: str, tabla_lexica: Optional[TablaLexica] = None) -> None:
        self.tabla = tabla_lexica or TablaLexica()
        self.tokenizador = Tokenizador(codigo, self.tabla)
        self.estado_actual = self.ESTADO_INICIAL
        self.pila: List[str] = [self.FONDO_PILA]
        self.seguimiento: List[Dict] = []
        self.tokens_leidos: List[Token] = []
        self.error: Optional[Dict] = None
        self.transiciones: Dict[str, Dict[int, Dict]] = {}
        self._construir_transiciones()

    def registrar_regla_transicion(
        self,
        estado_origen: str,
        token_entrada: int,
        estado_destino: str,
        simbolo_desapilar: Optional[str] = None,
        simbolo_apilar: Optional[str] = None,
    ) -> None:
        """Registra una transición determinista δ(q, a, X) -> (p, γ) en la tabla del PDA."""
        if estado_origen not in self.transiciones:
            self.transiciones[estado_origen] = {}
        self.transiciones[estado_origen][token_entrada] = {
            "sig": estado_destino,
            "pop": simbolo_desapilar,
            "push": simbolo_apilar,
        }

    def registrar_grupo_transiciones(
        self,
        estado_origen: str,
        conjunto_tokens: List[int],
        estado_destino: str,
        simbolo_desapilar: Optional[str] = None,
        simbolo_apilar: Optional[str] = None,
    ) -> None:
        for tok in conjunto_tokens:
            self.registrar_regla_transicion(
                estado_origen, tok, estado_destino, simbolo_desapilar, simbolo_apilar
            )

    def _construir_transiciones(self) -> None:
        # 1. Cabecera de la ruta
        self.registrar_regla_transicion("q0", INICIO_RUTA, "q1")
        self.registrar_regla_transicion("q1", CADENA, "q2")
        self.registrar_regla_transicion("q2", TERMINADOR, "q3")
        self.registrar_regla_transicion("q3", ORIGEN, "q4")
        self.registrar_regla_transicion("q4", CADENA, "q5")
        self.registrar_regla_transicion("q5", TERMINADOR, "q6")

        # 2. Bloque de paradas intermedias (push P)
        self.registrar_regla_transicion("q6", INICIO_PARADA, "q7", None, "P")
        self.registrar_regla_transicion("q7", CADENA, "q8")
        self.registrar_regla_transicion("q8", TERMINADOR, "q9")

        # 3. Atributos locales de parada
        self.registrar_grupo_transiciones(
            "q9",
            [
                TIPO, DESCRIPCION, UBICACION, VISTA, COSTO,
                TRANSPORTE, DISTANCIA, DURACION,
                PRONOSTICO, TEMPERATURA, PROBABILIDAD_LLUVIA,
            ],
            "q10",
        )
        self.registrar_regla_transicion("q10", IGUAL, "q11")
        self.registrar_grupo_transiciones("q11", [CADENA, NUM, ID], "q12")

        # 4. Arreglo de coordenadas [lat, lon] (push/pop A)
        self.registrar_regla_transicion("q11", ALLAVE_CUAD, "qArr", None, "A")
        self.registrar_grupo_transiciones("qArr", [NUM, COMA, ID], "qArr")
        self.registrar_regla_transicion("qArr", CLLAVE_CUAD, "q12", "A", None)

        self.registrar_regla_transicion("q12", TERMINADOR, "q9")

        # 5. Fin de parada (pop P)
        self.registrar_regla_transicion("q9", FIN_PARADA, "q13", "P", None)
        self.registrar_regla_transicion("q13", TERMINADOR, "q6")

        # 6. Destino final
        self.registrar_regla_transicion("q6", DESTINO, "q14")
        self.registrar_regla_transicion("q14", CADENA, "q15")
        self.registrar_regla_transicion("q15", TERMINADOR, "q16")

        # 7. Atributos globales de la ruta
        self.registrar_grupo_transiciones(
            "q16", [COSTO, TRANSPORTE, DISTANCIA, DURACION], "q17"
        )
        self.registrar_regla_transicion("q17", IGUAL, "q18")
        self.registrar_grupo_transiciones("q18", [NUM, ID, CADENA], "q19")
        self.registrar_regla_transicion("q19", TERMINADOR, "q16")

        # 8. Instrucción de visualización
        self.registrar_regla_transicion("q16", MOSTRAR_RUTA, "q30")
        self.registrar_regla_transicion("q30", TERMINADOR, "q16")

        # 9. Condicional SI / SINO / FIN (push/pop S)
        self.registrar_regla_transicion("q16", SI, "q20", None, "S")
        self.registrar_grupo_transiciones(
            "q20",
            [COSTO, DISTANCIA, DURACION, TEMPERATURA, PROBABILIDAD_LLUVIA],
            "q21",
        )
        self.registrar_grupo_transiciones(
            "q21",
            [MENOR, MENOR_IGUAL, MAYOR, MAYOR_IGUAL, IGUALDAD, DISTINTO],
            "q22",
        )
        self.registrar_grupo_transiciones("q22", [NUM, ID, CADENA], "q23")
        self.registrar_regla_transicion("q23", TERMINADOR, "q24")

        # Sentencias dentro de SI
        self.registrar_grupo_transiciones("q24", [RECOMENDAR, MOSTRAR], "q25")
        self.registrar_regla_transicion("q25", CADENA, "q26")
        self.registrar_regla_transicion("q26", TERMINADOR, "q24")

        # Rama SINO
        self.registrar_regla_transicion("q24", SINO, "q27")
        self.registrar_regla_transicion("q27", TERMINADOR, "q28")
        self.registrar_grupo_transiciones("q28", [RECOMENDAR, MOSTRAR], "q25_2")
        self.registrar_regla_transicion("q25_2", CADENA, "q26_2")
        self.registrar_regla_transicion("q26_2", TERMINADOR, "q28")

        # Fin condicional
        self.registrar_regla_transicion("q24", FIN, "q29")
        self.registrar_regla_transicion("q28", FIN, "q29")
        self.registrar_regla_transicion("q29", TERMINADOR, "q16", "S", None)

        # 10. Cierre de la ruta (pop Z -> qF)
        self.registrar_regla_transicion("q16", FIN_RUTA, "q31")
        self.registrar_regla_transicion("q31", TERMINADOR, "qF", self.FONDO_PILA, None)

    def _pila_como_texto(self) -> str:
        return "(vacia)" if not self.pila else " ".join(self.pila)

    def _registrar_paso(
        self,
        paso: int,
        est_ant: str,
        tok: Token,
        est_sig: Optional[str],
        pop: Optional[str],
        push: Optional[str],
    ) -> None:
        ops = []
        if pop:
            ops.append(f"pop {pop}")
        if push:
            ops.append(f"push {push}")
        self.seguimiento.append(
            {
                "Paso": paso,
                "Estado": est_ant,
                "Token": tok.nombre,
                "Lexema": tok.lexema if tok.lexema is not None else "EOF",
                "Línea": tok.linea,
                "Columna": tok.columna,
                "Siguiente": est_sig if est_sig is not None else "ERROR",
                "Operación": ", ".join(ops),
                "Pila": self._pila_como_texto(),
            }
        )

    def _describir_token(self, cod_token: int) -> str:
        nombre = self.tabla.nombre_de(cod_token)
        dato = self.tabla.buscar_por_token(cod_token)
        if dato and not dato["lexema"][0].isalpha():
            return f"{nombre} ('{dato['lexema']}')"
        return nombre

    def _tokens_esperados(self, estado: str) -> List[str]:
        if estado == self.ESTADO_FINAL:
            return ["FIN_CODIGO"]
        cods = list(self.transiciones.get(estado, {}).keys())
        return [self._describir_token(c) for c in cods]

    def _mensaje_por_estado(self, estado: str) -> str:
        mensajes = {
            "q0": "El programa debe comenzar con INICIO_RUTA.",
            "q1": "Después de INICIO_RUTA debe ir el nombre de la ruta entre comillas.",
            "q2": "Falta el terminador :> después del nombre de la ruta.",
            "q3": "Después de la cabecera debe ir ORIGEN.",
            "q4": "Después de ORIGEN debe ir el nombre del lugar de origen entre comillas.",
            "q5": "Falta el terminador :> después del origen.",
            "q6": "Se esperaba INICIO_PARADA (nueva parada intermedia) o DESTINO.",
            "q7": "Después de INICIO_PARADA debe ir el nombre de la parada entre comillas.",
            "q8": "Falta el terminador :> después del nombre de la parada.",
            "q9": "Dentro de una parada se esperaba un atributo válido o FIN_PARADA.",
            "q10": "Después del atributo debe ir el operador de asignación '='.",
            "q11": "Después de '=' debe ir un valor (CADENA, NUM, ID) o una lista [lat, lon].",
            "qArr": "Dentro de la lista de coordenadas solo se admiten NUM, ID, ',' y el cierre ']'.",
            "q12": "Falta el terminador :> al final de la asignación del atributo.",
            "q13": "Falta el terminador :> después de FIN_PARADA.",
            "q14": "Después de DESTINO debe ir el nombre del destino entre comillas.",
            "q15": "Falta el terminador :> después del destino.",
            "q16": "Se esperaba un atributo global (COSTO, TRANSPORTE, DISTANCIA, DURACION), MOSTRAR_RUTA, SI o FIN_RUTA.",
            "q17": "Después del atributo global debe ir el operador '='.",
            "q18": "Después de '=' debe ir un valor (NUM, ID o CADENA).",
            "q19": "Falta el terminador :> al final de la asignación global.",
            "q30": "Falta el terminador :> después de MOSTRAR_RUTA.",
            "q20": "Después de SI debe ir COSTO, DISTANCIA, DURACION, TEMPERATURA o PROBABILIDAD_LLUVIA.",
            "q21": "Se esperaba un operador relacional (<, <=, >, >=, ==, !=).",
            "q22": "Después del operador relacional debe ir un valor a comparar.",
            "q23": "Falta el terminador :> al final de la condición del SI.",
            "q24": "Dentro del bloque SI se esperaba RECOMENDAR, MOSTRAR, SINO o FIN.",
            "q25": "Después de RECOMENDAR o MOSTRAR debe ir un mensaje entre comillas.",
            "q26": "Falta el terminador :> después del mensaje.",
            "q27": "Falta el terminador :> después de SINO.",
            "q28": "Dentro del bloque SINO se esperaba RECOMENDAR, MOSTRAR o FIN.",
            "q25_2": "Después de RECOMENDAR o MOSTRAR debe ir un mensaje entre comillas.",
            "q26_2": "Falta el terminador :> después del mensaje.",
            "q29": "Falta el terminador :> después de FIN.",
            "q31": "Falta el terminador :> después de FIN_RUTA.",
            "qF": "No se permite código adicional después de FIN_RUTA :>.",
        }
        return mensajes.get(estado, "El token recibido no tiene transición válida.")

    def _crear_error(self, tipo: str, tok: Token, descripcion: str) -> Dict:
        esperados = self._tokens_esperados(self.estado_actual)
        lista_esp = ", ".join(esperados) if esperados else "ninguno"
        lex = f"'{tok.lexema}'" if tok.lexema is not None else "EOF"
        return {
            "tipo": tipo,
            "linea": tok.linea,
            "columna": tok.columna,
            "estado": self.estado_actual,
            "token": tok.nombre,
            "lexema": tok.lexema,
            "esperados": esperados,
            "pila": self._pila_como_texto(),
            "descripcion": descripcion,
            "mensaje": (
                f"Error {tipo} en línea {tok.linea}, columna {tok.columna}: "
                f"recibido {tok.nombre} ({lex}) en el estado {self.estado_actual}; "
                f"se esperaba: {lista_esp}. {descripcion}"
            ),
        }

    def analizar(self) -> bool:
        self.estado_actual = self.ESTADO_INICIAL
        self.pila = [self.FONDO_PILA]
        self.seguimiento = []
        self.tokens_leidos = []
        self.error = None
        paso = 1

        while True:
            tok = self.tokenizador.get_token()
            self.tokens_leidos.append(tok)
            est_ant = self.estado_actual

            if tok.token == ERROR:
                self._registrar_paso(paso, est_ant, tok, None, None, None)
                self.error = self._crear_error(
                    "léxico",
                    tok,
                    tok.detalle_error or "El analizador léxico encontró un lexema inválido.",
                )
                return False

            if est_ant == self.ESTADO_FINAL:
                if tok.token == FIN_CODIGO:
                    self._registrar_paso(paso, est_ant, tok, est_ant, None, None)
                    if self.pila:
                        self.error = self._crear_error(
                            "de pila",
                            tok,
                            "La pila no quedó vacía al finalizar el programa.",
                        )
                        return False
                    return True
                self._registrar_paso(paso, est_ant, tok, None, None, None)
                self.error = self._crear_error(
                    "sintáctico", tok, self._mensaje_por_estado(est_ant)
                )
                return False

            trans = self.transiciones.get(est_ant, {}).get(tok.token)
            if trans is None:
                self._registrar_paso(paso, est_ant, tok, None, None, None)
                desc = self._mensaje_por_estado(est_ant)
                if tok.token == FIN_CODIGO:
                    desc = f"El programa terminó prematuramente; {desc}"
                self.error = self._crear_error("sintáctico", tok, desc)
                return False

            if trans["pop"] is not None:
                tope = self.pila[-1] if self.pila else None
                if tope != trans["pop"]:
                    self._registrar_paso(paso, est_ant, tok, None, None, None)
                    self.error = self._crear_error(
                        "de pila",
                        tok,
                        f"Se esperaba '{trans['pop']}' en el tope de la pila, pero se encontró '{tope or 'pila vacía'}'.",
                    )
                    return False
                self.pila.pop()

            if trans["push"] is not None:
                self.pila.append(trans["push"])

            self.estado_actual = trans["sig"]
            self._registrar_paso(
                paso, est_ant, tok, trans["sig"], trans["pop"], trans["push"]
            )
            paso += 1
