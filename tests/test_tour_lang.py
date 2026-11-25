"""
Suite de pruebas automatizadas del compilador TOUR-LANG.
Verifica los 30 ejercicios oficiales (Básico, Intermedio y Avanzado)
y los 5 casos demostrativos de errores léxicos, sintácticos y semánticos.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tour_lang import AnalizadorSemantico, AnalizadorSintactico, TablaLexica
from tour_lang.ejemplos import EJERCICIOS_TOUR_LANG


def ejecutar_pruebas() -> None:
    tabla = TablaLexica()
    exitos_validos = 0
    exitos_errores = 0

    for nombre, datos in EJERCICIOS_TOUR_LANG.items():
        es_caso_error = "Demo Error" in nombre
        parser = AnalizadorSintactico(datos["codigo"], tabla)
        ok_sin = parser.analizar()

        if not es_caso_error:
            assert ok_sin, f"Fallo sintáctico inesperado en '{nombre}': {parser.error}"
            sem = AnalizadorSemantico(parser.tokens_leidos)
            ok_sem = sem.analizar()
            assert ok_sem, f"Fallo semántico inesperado en '{nombre}': {sem.errores}"
            exitos_validos += 1
        else:
            if "Error Semántico" in nombre:
                assert ok_sin, f"El caso semántico '{nombre}' debía pasar el PDA pero falló: {parser.error}"
                sem = AnalizadorSemantico(parser.tokens_leidos)
                ok_sem = sem.analizar()
                assert not ok_sem and len(sem.errores) >= 2, f"El caso '{nombre}' debía detectar errores semánticos."
            else:
                assert not ok_sin and parser.error is not None, f"El caso '{nombre}' debía fallar en Léxico/PDA."
            exitos_errores += 1

    assert exitos_validos == 30, f"Se esperaban 30 ejercicios válidos y pasaron {exitos_validos}"
    assert exitos_errores == 5, f"Se esperaban 5 casos de error y se validaron {exitos_errores}"
    print(f"OK: {exitos_validos}/30 ejercicios de Puno ACEPTADOS y {exitos_errores}/5 casos de error DETECTADOS con precisión.")


if __name__ == "__main__":
    ejecutar_pruebas()
