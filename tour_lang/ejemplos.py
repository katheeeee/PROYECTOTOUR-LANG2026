"""
Banco completo de los 30 ejercicios oficiales de rutas turísticas en Puno
(Niveles Básico, Intermedio y Avanzado) y casos demostrativos de errores
léxicos, sintácticos y semánticos para exposición ante el jurado.
"""

from typing import Dict

EJERCICIOS_TOUR_LANG: Dict[str, Dict[str, str]] = {
    # ==================== NIVEL BÁSICO (10) ====================
    "1.1 Básico - Ruta simple Puno - Sillustani": {
        "nivel": "Nivel 1: Básico",
        "codigo": """INICIO_RUTA "Puno - Sillustani" :>
    ORIGEN "Puno" :>
    DESTINO "Sillustani" :>
    MOSTRAR_RUTA :>
FIN_RUTA :>"""
    },
    "1.2 Básico - Ruta con transporte: Puno - Uros": {
        "nivel": "Nivel 1: Básico",
        "codigo": """INICIO_RUTA "Puno - Uros" :>
    ORIGEN "Puno" :>
    DESTINO "Uros" :>
    TRANSPORTE = "LANCHA" :>
    MOSTRAR_RUTA :>
FIN_RUTA :>"""
    },
    "1.3 Básico - Ruta con distancia: Puno - Chucuito": {
        "nivel": "Nivel 1: Básico",
        "codigo": """INICIO_RUTA "Puno - Chucuito" :>
    ORIGEN "Puno" :>
    DESTINO "Chucuito" :>
    TRANSPORTE = "BUS" :>
    DISTANCIA = 18 :>
    MOSTRAR_RUTA :>
FIN_RUTA :>"""
    },
    "1.4 Básico - Ruta con duración: Puno - Taquile": {
        "nivel": "Nivel 1: Básico",
        "codigo": """INICIO_RUTA "Puno - Taquile" :>
    ORIGEN "Puno" :>
    DESTINO "Taquile" :>
    TRANSPORTE = "LANCHA" :>
    DISTANCIA = 35 :>
    DURACION = 3 :>
    MOSTRAR_RUTA :>
FIN_RUTA :>"""
    },
    "1.5 Básico - Ruta con costo: Puno - Amantaní": {
        "nivel": "Nivel 1: Básico",
        "codigo": """INICIO_RUTA "Puno - Amantani" :>
    ORIGEN "Puno" :>
    DESTINO "Amantani" :>
    TRANSPORTE = "LANCHA" :>
    DISTANCIA = 40 :>
    DURACION = 3 :>
    COSTO = 35 :>
    MOSTRAR_RUTA :>
FIN_RUTA :>"""
    },
    "1.6 Básico - Ruta con mapa: Puno - Juli": {
        "nivel": "Nivel 1: Básico",
        "codigo": """INICIO_RUTA "Puno - Juli" :>
    ORIGEN "Puno" :>
    DESTINO "Juli" :>
    TRANSPORTE = "BUS" :>
    COSTO = 15 :>
    MOSTRAR_RUTA :>
FIN_RUTA :>"""
    },
    "1.7 Básico - Ruta con mensaje: Puno - Pomata": {
        "nivel": "Nivel 1: Básico",
        "codigo": """INICIO_RUTA "Puno - Pomata" :>
    ORIGEN "Puno" :>
    DESTINO "Pomata" :>
    TRANSPORTE = "BUS" :>
    COSTO = 12 :>
    SI COSTO <= 20 :>
        MOSTRAR "Ruta hacia el sur del lago" :>
    FIN :>
    MOSTRAR_RUTA :>
FIN_RUTA :>"""
    },
    "1.8 Básico - Ruta con comentario: Puno - Lampa": {
        "nivel": "Nivel 1: Básico",
        "codigo": """INICIO_RUTA "Puno - Lampa" :>
    // Ruta hacia la Ciudad Rosada
    ORIGEN "Puno" :>
    DESTINO "Lampa" :>
    TRANSPORTE = "BUS" :>
    DISTANCIA = 78 :>
    MOSTRAR_RUTA :>
FIN_RUTA :>"""
    },
    "1.9 Básico - Ruta económica: Puno - Capachica": {
        "nivel": "Nivel 1: Básico",
        "codigo": """INICIO_RUTA "Puno - Capachica" :>
    ORIGEN "Puno" :>
    DESTINO "Capachica" :>
    TRANSPORTE = "BUS" :>
    COSTO = 20 :>
    MOSTRAR_RUTA :>
FIN_RUTA :>"""
    },
    "1.10 Básico - Ruta completa: Puno - Llachón": {
        "nivel": "Nivel 1: Básico",
        "codigo": """INICIO_RUTA "Puno - Llachon" :>
    ORIGEN "Puno" :>
    DESTINO "Llachon" :>
    TRANSPORTE = "BUS" :>
    DISTANCIA = 65 :>
    DURACION = 2 :>
    COSTO = 18 :>
    SI COSTO <= 25 :>
        MOSTRAR "Ruta lista para iniciar" :>
    FIN :>
    MOSTRAR_RUTA :>
FIN_RUTA :>"""
    },

    # ==================== NIVEL INTERMEDIO (10) ====================
    "2.1 Intermedio - Una parada: Puno - Atuncolla - Sillustani": {
        "nivel": "Nivel 2: Intermedio",
        "codigo": """INICIO_RUTA "Puno - Sillustani" :>
    ORIGEN "Puno" :>
    INICIO_PARADA "Atuncolla" :>
        TIPO = "CULTURAL" :>
        DESCRIPCION = "Pueblo tradicional en la ruta a Sillustani" :>
    FIN_PARADA :>
    DESTINO "Sillustani" :>
    MOSTRAR_RUTA :>
FIN_RUTA :>"""
    },
    "2.2 Intermedio - Dos paradas: Puno - Pucará": {
        "nivel": "Nivel 2: Intermedio",
        "codigo": """INICIO_RUTA "Puno - Pucara" :>
    ORIGEN "Puno" :>
    INICIO_PARADA "Atuncolla" :>
        TIPO = "CULTURAL" :>
        DESCRIPCION = "Comunidad altoandina" :>
    FIN_PARADA :>
    INICIO_PARADA "Cabanillas" :>
        TIPO = "HISTORICO" :>
        DESCRIPCION = "Punto de conexion vial del altiplano" :>
    FIN_PARADA :>
    DESTINO "Pucara" :>
    MOSTRAR_RUTA :>
FIN_RUTA :>"""
    },
    "2.3 Intermedio - Tres paradas: Circuito Norte": {
        "nivel": "Nivel 2: Intermedio",
        "codigo": """INICIO_RUTA "Circuito Norte" :>
    ORIGEN "Puno" :>
    INICIO_PARADA "Atuncolla" :>
        TIPO = "CULTURAL" :>
    FIN_PARADA :>
    INICIO_PARADA "Cabanillas" :>
        TIPO = "HISTORICO" :>
    FIN_PARADA :>
    INICIO_PARADA "Lampa" :>
        TIPO = "ARQUITECTONICO" :>
    FIN_PARADA :>
    DESTINO "Pucara" :>
    MOSTRAR_RUTA :>
FIN_RUTA :>"""
    },
    "2.4 Intermedio - Paradas con transporte: Puno - Copacabana": {
        "nivel": "Nivel 2: Intermedio",
        "codigo": """INICIO_RUTA "Puno - Copacabana" :>
    ORIGEN "Puno" :>
    INICIO_PARADA "Chucuito" :>
        TIPO = "HISTORICO" :>
    FIN_PARADA :>
    INICIO_PARADA "Kasani" :>
        TIPO = "CULTURAL" :>
    FIN_PARADA :>
    DESTINO "Copacabana" :>
    TRANSPORTE = "BUS" :>
    MOSTRAR_RUTA :>
FIN_RUTA :>"""
    },
    "2.5 Intermedio - Paradas con distancia: Puno - Ayaviri": {
        "nivel": "Nivel 2: Intermedio",
        "codigo": """INICIO_RUTA "Puno - Ayaviri" :>
    ORIGEN "Puno" :>
    INICIO_PARADA "Cabanillas" :>
        TIPO = "CULTURAL" :>
    FIN_PARADA :>
    INICIO_PARADA "Lampa" :>
        TIPO = "ARQUITECTONICO" :>
    FIN_PARADA :>
    DESTINO "Ayaviri" :>
    DISTANCIA = 135 :>
    MOSTRAR_RUTA :>
FIN_RUTA :>"""
    },
    "2.6 Intermedio - Paradas con duración: Puno - Tinajani": {
        "nivel": "Nivel 2: Intermedio",
        "codigo": """INICIO_RUTA "Puno - Tinajani" :>
    ORIGEN "Puno" :>
    INICIO_PARADA "Ayaviri" :>
        TIPO = "GASTRONOMICO" :>
        DESCRIPCION = "Capital ganadera y del kankacho" :>
    FIN_PARADA :>
    DESTINO "Tinajani" :>
    DURACION = 6 :>
    MOSTRAR_RUTA :>
FIN_RUTA :>"""
    },
    "2.7 Intermedio - Paradas con costo: Puno - Umayo": {
        "nivel": "Nivel 2: Intermedio",
        "codigo": """INICIO_RUTA "Puno - Umayo" :>
    ORIGEN "Puno" :>
    INICIO_PARADA "Atuncolla" :>
        TIPO = "CULTURAL" :>
    FIN_PARADA :>
    INICIO_PARADA "Sillustani" :>
        TIPO = "ARQUEOLOGICO" :>
    FIN_PARADA :>
    DESTINO "Umayo" :>
    COSTO = 25 :>
    MOSTRAR_RUTA :>
FIN_RUTA :>"""
    },
    "2.8 Intermedio - Paradas con mapa: Circuito Sur": {
        "nivel": "Nivel 2: Intermedio",
        "codigo": """INICIO_RUTA "Circuito Sur" :>
    ORIGEN "Puno" :>
    INICIO_PARADA "Chucuito" :>
        TIPO = "HISTORICO" :>
    FIN_PARADA :>
    INICIO_PARADA "Juli" :>
        TIPO = "RELIGIOSO" :>
    FIN_PARADA :>
    INICIO_PARADA "Pomata" :>
        TIPO = "RELIGIOSO" :>
    FIN_PARADA :>
    DESTINO "Copacabana" :>
    MOSTRAR_RUTA :>
FIN_RUTA :>"""
    },
    "2.9 Intermedio - Circuito Islas del Titicaca": {
        "nivel": "Nivel 2: Intermedio",
        "codigo": """INICIO_RUTA "Circuito Islas" :>
    ORIGEN "Puno" :>
    INICIO_PARADA "Uros" :>
        TIPO = "VIVENCIAL" :>
    FIN_PARADA :>
    INICIO_PARADA "Taquile" :>
        TIPO = "CULTURAL" :>
    FIN_PARADA :>
    INICIO_PARADA "Amantani" :>
        TIPO = "VIVENCIAL" :>
    FIN_PARADA :>
    DESTINO "Puno" :>
    TRANSPORTE = "LANCHA" :>
    COSTO = 45 :>
    SI COSTO <= 60 :>
        MOSTRAR "Tour por las islas del Titicaca" :>
    FIN :>
    MOSTRAR_RUTA :>
FIN_RUTA :>"""
    },
    "2.10 Intermedio - Gran Circuito Puno": {
        "nivel": "Nivel 2: Intermedio",
        "codigo": """INICIO_RUTA "Gran Circuito Puno" :>
    ORIGEN "Puno" :>
    INICIO_PARADA "Atuncolla" :>
        TIPO = "CULTURAL" :>
    FIN_PARADA :>
    INICIO_PARADA "Sillustani" :>
        TIPO = "ARQUEOLOGICO" :>
    FIN_PARADA :>
    INICIO_PARADA "Cabanillas" :>
        TIPO = "HISTORICO" :>
    FIN_PARADA :>
    DESTINO "Lampa" :>
    TRANSPORTE = "BUS" :>
    DISTANCIA = 95 :>
    DURACION = 5 :>
    COSTO = 40 :>
    MOSTRAR_RUTA :>
FIN_RUTA :>"""
    },

    # ==================== NIVEL AVANZADO (10) ====================
    "3.1 Avanzado - Parada detallada con tipo y descripción": {
        "nivel": "Nivel 3: Avanzado",
        "codigo": """INICIO_RUTA "Puno - Sillustani" :>
    ORIGEN "Puno" :>
    INICIO_PARADA "Atuncolla" :>
        TIPO = "CULTURAL" :>
        DESCRIPCION = "Localidad tradicional de Puno" :>
    FIN_PARADA :>
    DESTINO "Sillustani" :>
    MOSTRAR_RUTA :>
FIN_RUTA :>"""
    },
    "3.2 Avanzado - Parada detallada con coordenadas": {
        "nivel": "Nivel 3: Avanzado",
        "codigo": """INICIO_RUTA "Puno - Chucuito" :>
    ORIGEN "Puno" :>
    INICIO_PARADA "Chucuito" :>
        UBICACION = [-15.894, -69.889] :>
        TIPO = "HISTORICO" :>
        DESCRIPCION = "Templo Inca Uyo y Plaza de Armas colonial" :>
    FIN_PARADA :>
    DESTINO "Juli" :>
    MOSTRAR_RUTA :>
FIN_RUTA :>"""
    },
    "3.3 Avanzado - Parada con Vista 3D (Sillustani)": {
        "nivel": "Nivel 3: Avanzado",
        "codigo": """INICIO_RUTA "Puno - Sillustani 3D" :>
    ORIGEN "Puno" :>
    INICIO_PARADA "Sillustani" :>
        UBICACION = [-15.723, -70.147] :>
        TIPO = "ARQUEOLOGICO" :>
        DESCRIPCION = "Chullpas funerarias de las culturas Kolla e Inca" :>
        VISTA = "3D" :>
        TEMPERATURA = 14 :>
        PROBABILIDAD_LLUVIA = 20 :>
    FIN_PARADA :>
    DESTINO "Umayo" :>
    MOSTRAR_RUTA :>
FIN_RUTA :>"""
    },
    "3.4 Avanzado - Dos paradas detalladas (Puno - Pucará 3D)": {
        "nivel": "Nivel 3: Avanzado",
        "codigo": """INICIO_RUTA "Puno - Pucara" :>
    ORIGEN "Puno" :>
    INICIO_PARADA "Atuncolla" :>
        TIPO = "CULTURAL" :>
        DESCRIPCION = "Pueblo tradicional camino a Pucara" :>
    FIN_PARADA :>
    INICIO_PARADA "Pucara" :>
        UBICACION = [-15.041, -70.370] :>
        TIPO = "ARQUEOLOGICO" :>
        DESCRIPCION = "Museo Litico y talleres de ceramica" :>
        VISTA = "3D" :>
    FIN_PARADA :>
    DESTINO "Ayaviri" :>
    MOSTRAR_RUTA :>
FIN_RUTA :>"""
    },
    "3.5 Avanzado - Circuito Cultural Colonial del Sur": {
        "nivel": "Nivel 3: Avanzado",
        "codigo": """INICIO_RUTA "Circuito Cultural del Altiplano" :>
    ORIGEN "Puno" :>
    INICIO_PARADA "Chucuito" :>
        TIPO = "HISTORICO" :>
        DESCRIPCION = "Plaza de Armas colonial" :>
    FIN_PARADA :>
    INICIO_PARADA "Juli" :>
        TIPO = "RELIGIOSO" :>
        DESCRIPCION = "Iglesias coloniales del siglo XVI" :>
    FIN_PARADA :>
    INICIO_PARADA "Pomata" :>
        TIPO = "RELIGIOSO" :>
        DESCRIPCION = "Templo de Santiago Apostol" :>
    FIN_PARADA :>
    DESTINO "Copacabana" :>
    MOSTRAR_RUTA :>
FIN_RUTA :>"""
    },
    "3.6 Avanzado - Cañón de Tinajani (Vista Satélite)": {
        "nivel": "Nivel 3: Avanzado",
        "codigo": """INICIO_RUTA "Puno - Tinajani" :>
    ORIGEN "Puno" :>
    INICIO_PARADA "Canon de Tinajani" :>
        UBICACION = [-14.933, -70.566] :>
        TIPO = "NATURAL" :>
        DESCRIPCION = "Formaciones rocosas y bosques de puya" :>
        VISTA = "SATELITE" :>
    FIN_PARADA :>
    DESTINO "Ayaviri" :>
    MOSTRAR_RUTA :>
FIN_RUTA :>"""
    },
    "3.7 Avanzado - Islas Uros con recomendación condicional": {
        "nivel": "Nivel 3: Avanzado",
        "codigo": """INICIO_RUTA "Puno - Uros" :>
    ORIGEN "Puno" :>
    INICIO_PARADA "Islas Uros" :>
        UBICACION = [-15.833, -69.966] :>
        TIPO = "VIVENCIAL" :>
        DESCRIPCION = "Tejido de totora y recorrido en balsa" :>
    FIN_PARADA :>
    DESTINO "Puno" :>
    COSTO = 30 :>
    SI COSTO <= 50 :>
        RECOMENDAR "Ruta accesible para todo publico" :>
    FIN :>
    MOSTRAR_RUTA :>
FIN_RUTA :>"""
    },
    "3.8 Avanzado - Lampa Ciudad Rosada 3D": {
        "nivel": "Nivel 3: Avanzado",
        "codigo": """INICIO_RUTA "Puno - Lampa" :>
    ORIGEN "Puno" :>
    INICIO_PARADA "Lampa" :>
        UBICACION = [-15.362, -70.365] :>
        TIPO = "ARQUITECTONICO" :>
        DESCRIPCION = "Ciudad Rosada y Templo Santiago Apostol" :>
        VISTA = "3D" :>
        PRONOSTICO = "SOLEADO" :>
        TEMPERATURA = 16 :>
        PROBABILIDAD_LLUVIA = 10 :>
    FIN_PARADA :>
    DESTINO "Pucara" :>
    TRANSPORTE = "BUS" :>
    DISTANCIA = 78 :>
    DURACION = 2 :>
    COSTO = 22 :>
    MOSTRAR_RUTA :>
FIN_RUTA :>"""
    },
    "3.9 Avanzado - Circuito Sur Místico (Demo Informe)": {
        "nivel": "Nivel 3: Avanzado",
        "codigo": """INICIO_RUTA "Circuito Sur Mistico" :>
    ORIGEN "Puno" :>
    INICIO_PARADA "Chucuito" :>
        TIPO = "HISTORICO" :>
        DESCRIPCION = "Parada fotografica y cultural" :>
    FIN_PARADA :>
    INICIO_PARADA "Aramu Muru" :>
        UBICACION = [-16.115, -69.425] :>
        TIPO = "MISTICO" :>
        DESCRIPCION = "Puerta interdimensional tallada en roca" :>
        VISTA = "SATELITE" :>
        PRONOSTICO = "DESPEJADO" :>
        TEMPERATURA = 15 :>
        PROBABILIDAD_LLUVIA = 15 :>
    FIN_PARADA :>
    DESTINO "Puno" :>
    COSTO = 55 :>
    SI COSTO <= 50 :>
        RECOMENDAR "Ruta economica" :>
    SINO :>
        MOSTRAR "Ruta fuera del presupuesto estandar" :>
    FIN :>
    MOSTRAR_RUTA :>
FIN_RUTA :>"""
    },
    "3.10 Avanzado - Gran Ruta Cultural Puno (Síntesis Total)": {
        "nivel": "Nivel 3: Avanzado",
        "codigo": """INICIO_RUTA "Gran Ruta Cultural Puno" :>
    ORIGEN "Puno" :>
    INICIO_PARADA "Sillustani" :>
        UBICACION = [-15.723, -70.147] :>
        TIPO = "ARQUEOLOGICO" :>
        DESCRIPCION = "Chullpas de las culturas Kolla e Inca" :>
        VISTA = "3D" :>
        PRONOSTICO = "SOLEADO" :>
        TEMPERATURA = 15 :>
        PROBABILIDAD_LLUVIA = 10 :>
    FIN_PARADA :>
    INICIO_PARADA "Pucara" :>
        UBICACION = [-15.041, -70.370] :>
        TIPO = "CULTURAL" :>
        DESCRIPCION = "Museo Litico y talleres de ceramica" :>
        VISTA = "3D" :>
        PRONOSTICO = "TEMPLADO" :>
        TEMPERATURA = 17 :>
        PROBABILIDAD_LLUVIA = 15 :>
    FIN_PARADA :>
    DESTINO "Puno" :>
    TRANSPORTE = "BUS" :>
    DISTANCIA = 150 :>
    DURACION = 8 :>
    COSTO = 90 :>
    SI COSTO <= 100 :>
        RECOMENDAR "Ruta recomendada para delegaciones y visitantes" :>
    SINO :>
        MOSTRAR "Ruta fuera del presupuesto" :>
    FIN :>
    MOSTRAR_RUTA :>
FIN_RUTA :>"""
    },

    # ==================== CASOS DE ERROR PARA EL JURADO (5) ====================
    "4.1 [Demo Error Léxico E1] Cadena sin comilla de cierre": {
        "nivel": "Casos de Error (Demo Jurado)",
        "codigo": """INICIO_RUTA "Circuito Inconcluso :>
    ORIGEN "Puno" :>
    DESTINO "Sillustani" :>
FIN_RUTA :>"""
    },
    "4.2 [Demo Error Léxico E4] Operador ':' sin '>'": {
        "nivel": "Casos de Error (Demo Jurado)",
        "codigo": """INICIO_RUTA "Ruta Lago" :>
    ORIGEN "Puno" :
    DESTINO "Uros" :>
FIN_RUTA :>"""
    },
    "4.3 [Demo Error Sintáctico PDA] Falta terminador :> (Informe)": {
        "nivel": "Casos de Error (Demo Jurado)",
        "codigo": """INICIO_RUTA "Circuito Sur Mistico" :>
    ORIGEN "Puno" :>
    DESTINO "Chucuito" :>
    COSTO = 55
    MOSTRAR_RUTA :>
FIN_RUTA :>"""
    },
    "4.4 [Demo Error Sintáctico/Pila] Parada sin FIN_PARADA": {
        "nivel": "Casos de Error (Demo Jurado)",
        "codigo": """INICIO_RUTA "Ruta Desbalanceada" :>
    ORIGEN "Puno" :>
    INICIO_PARADA "Sillustani" :>
        TIPO = "ARQUEOLOGICO" :>
    DESTINO "Lampa" :>
FIN_RUTA :>"""
    },
    "4.5 [Demo Error Semántico] PROBABILIDAD_LLUVIA = 150 y COSTO negativo": {
        "nivel": "Casos de Error (Demo Jurado)",
        "codigo": """INICIO_RUTA "Prueba Reglas Semanticas" :>
    ORIGEN "Puno" :>
    INICIO_PARADA "Sillustani" :>
        TIPO = "ARQUEOLOGICO" :>
        DESCRIPCION = "Prueba sintacticamente valida pero semanticamente erronea" :>
        PROBABILIDAD_LLUVIA = 150 :>
        COSTO = -20 :>
    FIN_PARADA :>
    DESTINO "Lampa" :>
    MOSTRAR_RUTA :>
FIN_RUTA :>"""
    },
}
