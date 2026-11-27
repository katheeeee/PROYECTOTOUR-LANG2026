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


def verificar_pila_y_vistas(tabla: TablaLexica) -> None:
    """Valida el ciclo de vida de la pila Γ = {Z, R, P, A, S} y vista_predominante."""
    cod_310 = EJERCICIOS_TOUR_LANG["3.10 Avanzado - Gran Ruta Cultural Puno (Síntesis Total)"]["codigo"]
    parser = AnalizadorSintactico(cod_310, tabla)
    assert parser.analizar(), f"Fallo inesperado en 3.10: {parser.error}"

    pasos = parser.seguimiento
    assert pasos[0]["Operación"] == "pop Z, push R" and pasos[0]["Pila"] == "R", (
        f"El paso 1 debe reemplazar Z por R, obtenido: {pasos[0]}"
    )

    pilas = [p["Pila"] for p in pasos]
    assert "R P" in pilas, "La pila debe alcanzar 'R P' dentro de INICIO_PARADA."
    assert "R P A" in pilas, "La pila debe alcanzar 'R P A' dentro de UBICACION = [...]."
    assert "R S" in pilas, "La pila debe alcanzar 'R S' dentro del condicional SI."

    cierre = next((p for p in pasos if p["Estado"] == "q31" and p["Siguiente"] == "qF"), None)
    assert cierre is not None, "No se encontró la transición de cierre q31 -> qF."
    assert cierre["Operación"] == "pop R" and cierre["Pila"] == "(vacia)", (
        f"El cierre q31 -> qF debe ejecutar pop R y dejar pila vacía, obtenido: {cierre}"
    )

    esperados_vista = {
        "3.10 Avanzado - Gran Ruta Cultural Puno (Síntesis Total)": "3D",
        "3.9 Avanzado - Circuito Sur Místico (Demo Informe)": "SATELITE",
        "1.1 Básico - Ruta simple Puno - Sillustani": "MAPA",
    }
    for nombre_ej, vista_esp in esperados_vista.items():
        p_ej = AnalizadorSintactico(EJERCICIOS_TOUR_LANG[nombre_ej]["codigo"], tabla)
        assert p_ej.analizar()
        sem_ej = AnalizadorSemantico(p_ej.tokens_leidos)
        assert sem_ej.analizar()
        assert sem_ej.modelo_ruta["vista_predominante"] == vista_esp, (
            f"Vista esperada '{vista_esp}' en '{nombre_ej}', obtenida '{sem_ej.modelo_ruta['vista_predominante']}'"
        )


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
    verificar_pila_y_vistas(tabla)
    print(f"OK: {exitos_validos}/30 ejercicios de Puno ACEPTADOS, {exitos_errores}/5 casos de error DETECTADOS, pila [R] y vistas verificadas.")


if __name__ == "__main__":
    ejecutar_pruebas()
