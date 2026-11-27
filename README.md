# 🗺️ PROYECTO TOUR-LANG 2026

**Compilador y Lenguaje de Dominio Específico (DSL) para el Modelado, Validación Formal y Visualización Cartográfica de Rutas Turísticas en la Región Puno**

---

## 🏛️ Información Académica
- **Universidad:** Universidad Nacional del Altiplano (UNA Puno)
- **Facultad:** Facultad de Ingeniería Mecánica Eléctrica, Electrónica y Sistemas
- **Escuela Profesional:** Ingeniería de Sistemas (EPIS)
- **Curso:** Compiladores — V Semestre — Grupo A
- **Área de Concurso:** Ciencias de la Computación (Ciencias de la Computación y Ciberseguridad)
- **Docente Asesor:** Ing. Victor Hugo Bejar Gonzales

### 👥 Equipo Desarrollador
| Integrante | Correo Institucional | Rol Principal |
| :--- | :--- | :--- |
| **Kriss Katherine Aico Ramos** | `60850734@est.unap.edu.pe` | Líder de Proyecto, Analizador Léxico (AFD) e Integración Web |
| **Julissa Esther Mestas Huanca** | `julissamestas@est.unap.edu.pe` | Analizador Sintáctico y Modelado de Autómata de Pila (PDA en JFLAP) |
| **Anthony Junior Quispe Cruz** | `60908700@est.unap.edu.pe` | Analizador Semántico, Casos de Prueba y Visualización Cartográfica |

---

## ⚙️ Arquitectura del Compilador `TOUR-LANG`

El proyecto implementa un pipeline completo de compilación e interpretación:

1. **Analizador Léxico (`tour_lang/lexico.py` y `GRAFICADOR/graficador-lexico.php`):**
   - Basado en un **Autómata Finito Determinista (AFD)** de **140 estados** (`q0`–`q140`) distribuidos en 4 ramas y **5 estados de detección de errores léxicos** (`E1` a `E5`).
   - Reconoce **23 palabras reservadas** en mayúsculas (`INICIO_RUTA`, `FIN_RUTA`, `ORIGEN`, `DESTINO`, `INICIO_PARADA`, `FIN_PARADA`, `TIPO`, `DESCRIPCION`, `UBICACION`, `VISTA`, `COSTO`, `TRANSPORTE`, `DISTANCIA`, `DURACION`, `PRONOSTICO`, `TEMPERATURA`, `PROBABILIDAD_LLUVIA`, `SI`, `SINO`, `FIN`, `RECOMENDAR`, `MOSTRAR`, `MOSTRAR_RUTA`), 11 símbolos/operadores (incluyendo `:>`), literales de cadena y números decimales con signo negativo para coordenadas geográficas del altiplano.
2. **Analizador Sintáctico (`tour_lang/sintactico.py`, `GRAFICADOR/graficador-sintactico.php` y `automata-v2.jff`):**
   - Basado en un **Autómata de Pila Determinista (PDA)** de **36 estados** modelado y verificado en **JFLAP 7.1**.
   - Emplea el alfabeto de pila $\Gamma = \{Z, R, P, A, S\}$ (`Z` se reemplaza por `R` al iniciar la ruta, y `R` se desapila al cerrar `FIN_RUTA :>`) para validar el balanceo de bloques de ruta (`R`), paradas intermedias (`P`), arreglos de coordenadas `[lat, lon]` (`A`) y estructuras condicionales `SI / SINO / FIN` (`S`).
3. **Analizador Semántico (`tour_lang/semantico.py`):**
   - Construye la **Tabla de Símbolos por ámbitos** (Global vs. Local por parada).
   - Valida unicidad de paradas y atributos, compatibilidad de tipos, rangos estrictos (`PROBABILIDAD_LLUVIA` en `[0, 100]`, costos/distancias no negativos) y coherencia espacial entre `ORIGEN`, paradas y `DESTINO`.
4. **Plataforma Web Interactiva (`app.py` con Streamlit + Leaflet + MapLibre GL 3D + OSRM/Valhalla):**
   - Editor interactivo con los **30 ejercicios oficiales** de rutas turísticas de Puno (Básico, Intermedio y Avanzado) más 5 casos de prueba de errores.
   - Pantalla dividida estilo IDE con **enrutamiento real por carreteras (OSRM + Valhalla)**, **Mapa 2D / Satelital (Leaflet)**, **Relieve 3D real del Altiplano + Vuelo 3D (MapLibre GL)** y exportación a `.tl`, `.json` y `.geojson`.

---

## 🚀 Ejemplo de Código en `TOUR-LANG`

```tourlang
INICIO_RUTA "Gran Ruta Cultural Puno" :>
    ORIGEN "Puno" :>

    INICIO_PARADA "Sillustani" :>
        UBICACION = [-15.723, -70.147] :>
        TIPO = "ARQUEOLOGICO" :>
        DESCRIPCION = "Chullpas de las culturas Kolla e Inca" :>
        VISTA = "3D" :>
        TEMPERATURA = 15 :>
        PROBABILIDAD_LLUVIA = 10 :>
    FIN_PARADA :>

    INICIO_PARADA "Pucara" :>
        UBICACION = [-15.041, -70.370] :>
        TIPO = "CULTURAL" :>
        DESCRIPCION = "Museo Litico y talleres de ceramica" :>
        VISTA = "3D" :>
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
FIN_RUTA :>
```

---

## 💻 Ejecución Rápida

### 1. Plataforma Web en Python
```bash
pip install -r requirements.txt
streamlit run app.py
```
*(En Windows también puedes hacer doble clic en `iniciar_web.bat`).*

### 2. Ejecutar Suite de Pruebas (30 Ejercicios + Validación de Errores)
```bash
python tests/test_tour_lang.py
```

### 3. Ejecutar Prototipos PHP y Modelos JFLAP
```bash
php GRAFICADOR/graficador-sintactico.php
```
Los archivos `automata-v2.jff` y `GRAFICADOR/lexema_automata.jff` pueden abrirse directamente en **JFLAP 7.1**.

### 4. Presentación Interactiva HTML (16:9 con Simulador del PDA)
Abre directamente `presentacion_tour_lang.html` en cualquier navegador (navegación con flechas `←` / `→` o `Espacio`).
