<?php

/* ============================================================
 * TOKENS DEL LENGUAJE
 * ============================================================
 */



const INICIO_RUTA         = 0;
const FIN_RUTA            = 1;
const ORIGEN              = 2;
const DESTINO             = 3;
const INICIO_PARADA       = 4;
const FIN_PARADA          = 5;
const TIPO                = 6;
const DESCRIPCION         = 7;
const UBICACION           = 8;
const VISTA               = 9;
const COSTO               = 10;
const TRANSPORTE          = 11;
const DISTANCIA           = 12;
const DURACION            = 13;
const PRONOSTICO          = 14;
const TEMPERATURA         = 15;
const PROBABILIDAD_LLUVIA = 16;
const SI                  = 17;
const SINO                = 18;
const FIN                 = 19;
const RECOMENDAR          = 20;
const MOSTRAR             = 21;
const MOSTRAR_RUTA        = 22;


/* ============================================================
 * SIMBOLOS, SEPARADORES Y OPERADORES
 * ============================================================
 */

const IGUAL           = 23;   // =
const COMA            = 24;   // ,
const ALLAVE_CUAD     = 25;   // [
const CLLAVE_CUAD     = 26;   // ]

const MENOR           = 27;   // <
const MAYOR           = 28;   // >
const MENOR_IGUAL     = 29;   // <=
const MAYOR_IGUAL     = 30;   // >=
const IGUALDAD        = 31;   // ==
const DISTINTO        = 32;   // !=

const TERMINADOR      = 33;   // :>


/* ============================================================
 * TOKENS PRODUCIDOS POR EL ANALISIS LEXICO
 * ============================================================
 */

const ID              = 34;
const NUM             = 35;
const CADENA          = 36;


/* ============================================================
 * TOKENS DE CONTROL
 *
 * FIN_CODIGO es el fin del archivo (EOF).
 *
 * No debe confundirse con la palabra reservada FIN,
 * que cierra el condicional SI / SINO.
 * ============================================================
 */

const FIN_CODIGO      = 666;
const ERROR           = 999;


/* ============================================================
 * CLASE TABLA LÉXICA
 *
 * Contiene los lexemas que forman parte de la definición
 * fija del lenguaje.
 * ============================================================
 */

class TablaLexica
{
    private array $porToken = [];
    private array $porLexema = [];

    /*
     * Nombres legibles de los tokens que el analizador
     * léxico produce y que NO viven en la tabla de lexemas
     * (no se pueden buscar como lexema).
     */
    private array $nombres = [
        ID          => 'IDENTIFICADOR',
        NUM         => 'NUMERO',
        CADENA      => 'CADENA',
        FIN_CODIGO  => 'FIN_CODIGO',
        ERROR       => 'ERROR'
    ];


    public function __construct()
    {
        /* ====================================================
         * PALABRAS RESERVADAS
         *
         * Solo se reconocen en mayúsculas, tal como
         * aparecen en el diseño del lenguaje.
         * ====================================================
         */

        $this->Agregar(INICIO_RUTA,         'INICIO_RUTA',         'palabra_reservada');
        $this->Agregar(FIN_RUTA,            'FIN_RUTA',            'palabra_reservada');
        $this->Agregar(ORIGEN,              'ORIGEN',              'palabra_reservada');
        $this->Agregar(DESTINO,             'DESTINO',             'palabra_reservada');
        $this->Agregar(INICIO_PARADA,       'INICIO_PARADA',       'palabra_reservada');
        $this->Agregar(FIN_PARADA,          'FIN_PARADA',          'palabra_reservada');
        $this->Agregar(TIPO,                'TIPO',                'palabra_reservada');
        $this->Agregar(DESCRIPCION,         'DESCRIPCION',         'palabra_reservada');
        $this->Agregar(UBICACION,           'UBICACION',           'palabra_reservada');
        $this->Agregar(VISTA,               'VISTA',               'palabra_reservada');
        $this->Agregar(COSTO,               'COSTO',               'palabra_reservada');
        $this->Agregar(TRANSPORTE,          'TRANSPORTE',          'palabra_reservada');
        $this->Agregar(DISTANCIA,           'DISTANCIA',           'palabra_reservada');
        $this->Agregar(DURACION,            'DURACION',            'palabra_reservada');
        $this->Agregar(PRONOSTICO,          'PRONOSTICO',          'palabra_reservada');
        $this->Agregar(TEMPERATURA,         'TEMPERATURA',         'palabra_reservada');
        $this->Agregar(PROBABILIDAD_LLUVIA, 'PROBABILIDAD_LLUVIA', 'palabra_reservada');
        $this->Agregar(SI,                  'SI',                  'palabra_reservada');
        $this->Agregar(SINO,                'SINO',                'palabra_reservada');
        $this->Agregar(FIN,                 'FIN',                 'palabra_reservada');
        $this->Agregar(RECOMENDAR,          'RECOMENDAR',          'palabra_reservada');
        $this->Agregar(MOSTRAR,             'MOSTRAR',             'palabra_reservada');
        $this->Agregar(MOSTRAR_RUTA,        'MOSTRAR_RUTA',        'palabra_reservada');

        /* ====================================================
         * SIMBOLOS, SEPARADORES Y OPERADORES
         *
         * Los de dos caracteres (<=, >=, ==, !=, :>)
         * son reconocidos por BuscarLexemaMasLargo(),
         * que siempre escoge el lexema más largo.
         * ====================================================
         */

        $this->Agregar(IGUAL,       '=',   'operador', 'IGUAL');
        $this->Agregar(COMA,        ',',   'separador', 'COMA');
        $this->Agregar(ALLAVE_CUAD, '[',   'simbolo',  'ALLAVE_CUADRADA');
        $this->Agregar(CLLAVE_CUAD, ']',   'simbolo',  'CLLAVE_CUADRADA');

        $this->Agregar(MENOR,       '<',   'operador', 'MENOR');
        $this->Agregar(MAYOR,       '>',   'operador', 'MAYOR');
        $this->Agregar(MENOR_IGUAL, '<=',  'operador', 'MENOR_IGUAL');
        $this->Agregar(MAYOR_IGUAL, '>=',  'operador', 'MAYOR_IGUAL');
        $this->Agregar(IGUALDAD,    '==',  'operador', 'IGUALDAD');
        $this->Agregar(DISTINTO,    '!=',  'operador', 'DISTINTO');

        $this->Agregar(TERMINADOR,  ':>',  'terminador', 'TERMINADOR');
    }


    private function Agregar(
        int $token,
        string $lexema,
        string $tipo,
        string $nombre = ''
    ): void {

        $dato = [
            'token'  => $token,
            'lexema' => $lexema,
            'tipo'   => $tipo,

            /*
             * Si no se indica un nombre legible,
             * se usa el propio lexema en mayúsculas.
             */
            'nombre' => $nombre !== ''
                        ? $nombre
                        : strtoupper($lexema)
        ];

        /*
         * Índice por TOKEN
         *
         * Ejemplo:
         *
         * $porToken[INICIO_RUTA]
         */
        $this->porToken[$token] = $dato;


        /*
         * Índice por LEXEMA
         *
         * Ejemplo:
         *
         * $porLexema['INICIO_RUTA']
         */
        $this->porLexema[$lexema] = $dato;
    }


    public function BuscarPorToken(int $token): ?array
    {
        return $this->porToken[$token] ?? null;
    }


    public function BuscarPorLexema(string $lexema): ?array
    {
        return $this->porLexema[$lexema] ?? null;
    }


    public function ExisteLexema(string $lexema): bool
    {
        return isset($this->porLexema[$lexema]);
    }


    /*
     * Devuelve el nombre legible de un token.
     *
     * Ejemplo:
     *
     * $tablaLexica->NombreDe(INICIO_RUTA)
     * devuelve 'INICIO_RUTA'
     */
    public function NombreDe(int $token): ?string
    {
        if (isset($this->nombres[$token])) {
            return $this->nombres[$token];
        }

        return $this->porToken[$token]['nombre'] ?? null;
    }


    /*
     * Busca el lexema válido MÁS LARGO que exista
     * en la TablaLexica desde una posición determinada.
     *
     * Esto permite reconocer:
     *
     * =      (y no tomarlo como parte de ==)
     * ==     (y no tomarlo como = + =)
     * <
     * <=     (y no tomarlo como < + =)
     * >
     * >=
     * !=
     * :>
     *
     * sin escribir reglas adicionales en el Tokenizador.
     */
    public function BuscarLexemaMasLargo(
        string $codigo,
        int $posicion
    ): ?array {

        $encontrado = null;

        foreach ($this->porLexema as $lexema => $datos) {

            /*
             * Las palabras reservadas formadas por letras
             * se reconocen previamente en el Tokenizador.
             *
             * Aquí nos interesan principalmente los
             * lexemas fijos:
             *
             * =
             * <
             * <=
             * [
             * ,
             * :>
             * etc.
             */
            if (ctype_alpha($lexema[0])) {
                continue;
            }

            $longitud = strlen($lexema);

            $fragmento = substr(
                $codigo,
                $posicion,
                $longitud
            );

            if ($fragmento === $lexema) {

                if (
                    $encontrado === null ||
                    $longitud > $encontrado['longitud']
                ) {

                    $encontrado = [
                        'token'    => $datos['token'],
                        'lexema'   => $lexema,
                        'tipo'     => $datos['tipo'],
                        'longitud' => $longitud
                    ];
                }
            }
        }

        return $encontrado;
    }


    public function getTabla(): array
    {
        return $this->porToken;
    }
}


/* ============================================================
 * CLASE TOKEN
 *
 * Cada llamada a getToken() devuelve un objeto Token.
 * ============================================================
 */

class Token
{
    public int $token;
    public ?string $lexema;
    public int $linea;
    public int $columna;

    /*
     * Nombre legible del token.
     *
     * Ejemplo:
     *
     * INICIO_RUTA
     * MENOR_IGUAL
     * IDENTIFICADOR
     */
    public ?string $nombre;


    public function __construct(
        int $token,
        ?string $lexema,
        int $linea,
        int $columna,
        ?string $nombre = null
    ) {
        $this->token = $token;
        $this->lexema = $lexema;
        $this->linea = $linea;
        $this->columna = $columna;
        $this->nombre = $nombre;
    }


    public function Mostrar(): void
    {
        echo "Token(" . $this->token . ") \t";

        echo "Nombre(" .
            ($this->nombre ?? 'null')
            . ") \t";

        echo "Lexema(" .
            ($this->lexema ?? 'null')
            . ") \t";

        echo "Linea(" . $this->linea . ") \t";

        echo "Columna(" . $this->columna . ")";

        echo PHP_EOL;
    }
}


/* ============================================================
 * CLASE TOKENIZADOR
 *
 * Lee el código fuente.
 *
 * Cada llamada a:
 *
 * getToken()
 *
 * devuelve UN objeto Token.
 * ============================================================
 */

class Tokenizador
{
    private string $codigo;

    private int $indice = 0;

    private int $linea = 1;

    private int $columna = 1;

    private TablaLexica $tablaLexica;


    public function __construct(
        string $codigo,
        TablaLexica $tablaLexica
    ) {
        /*
         * Normalizamos los saltos de línea de Windows
         * (\r\n) a un solo carácter, de modo que el
         * conteo de línea y columna sea exacto.
         */
        $this->codigo = str_replace("\r\n", "\n", $codigo);

        $this->tablaLexica = $tablaLexica;
    }


    /* ========================================================
     * CREAR TOKEN
     *
     * Punto único de creación de tokens.
     *
     * Aquí se resuelve el nombre legible del token
     * a partir de la TablaLexica, para que las clases
     * Token no tengan que conocer la tabla.
     * ========================================================
     */

    private function NuevoToken(
        int $token,
        ?string $lexema,
        int $linea,
        int $columna
    ): Token {

        return new Token(
            $token,
            $lexema,
            $linea,
            $columna,
            $this->tablaLexica->NombreDe($token)
        );
    }


    /* ========================================================
     * GET TOKEN
     * ========================================================
     */

    public function getToken(): Token
    {
        /*
         * Ignorar:
         *
         * espacios
         * tabulaciones
         * saltos de línea
         * retornos de carro
         */
        $this->OmitirEspacios();


        /*
         * FIN DEL CÓDIGO
         *
         * OJO: este es el fin del archivo.
         * La palabra reservada FIN es otro token.
         */
        if ($this->FinCodigo()) {

            return $this->NuevoToken(
                FIN_CODIGO,
                null,
                $this->linea,
                $this->columna
            );
        }


        /*
         * Guardamos dónde comienza el token.
         */
        $lineaInicial = $this->linea;

        $columnaInicial = $this->columna;


        $caracter = $this->codigo[$this->indice];


        /* ====================================================
         * IDENTIFICADOR O PALABRA RESERVADA
         * ====================================================
         */

        if (ctype_alpha($caracter)) {

            $lexema = $this->LeerIdentificador();


            /*
             * Primero buscamos si el lexema está definido
             * dentro de TablaLexica.
             */
            $elemento =
                $this->tablaLexica
                     ->BuscarPorLexema($lexema);


            /*
             * Si existe, es una palabra reservada.
             */
            if ($elemento !== null) {

                return $this->NuevoToken(
                    $elemento['token'],
                    $lexema,
                    $lineaInicial,
                    $columnaInicial
                );
            }


            /*
             * Si no es palabra reservada,
             * entonces es un identificador.
             */
            return $this->NuevoToken(
                ID,
                $lexema,
                $lineaInicial,
                $columnaInicial
            );
        }


        /* ====================================================
         * NÚMERO CON SIGNO NEGATIVO
         *
         * Ejemplo:
         *
         * -16.115
         * -69.425
         *
         * Solo se trata como número si el signo va
         * seguido de un dígito. Un "-" suelto cae
         * después en el caso CARÁCTER DESCONOCIDO.
         * ====================================================
         */

        if ($this->EsNumeroNegativo()) {

            $lexema = $this->LeerNumero();


            /*
             * Si LeerNumero devuelve null,
             * el número tiene un formato incorrecto.
             */
            if ($lexema === null) {

                return $this->NuevoToken(
                    ERROR,
                    null,
                    $lineaInicial,
                    $columnaInicial
                );
            }


            return $this->NuevoToken(
                NUM,
                $lexema,
                $lineaInicial,
                $columnaInicial
            );
        }


        /* ====================================================
         * NÚMERO
         * ====================================================
         */

        if (ctype_digit($caracter)) {

            $lexema = $this->LeerNumero();


            /*
             * Si LeerNumero devuelve null,
             * el número tiene un formato incorrecto.
             */
            if ($lexema === null) {

                return $this->NuevoToken(
                    ERROR,
                    null,
                    $lineaInicial,
                    $columnaInicial
                );
            }


            return $this->NuevoToken(
                NUM,
                $lexema,
                $lineaInicial,
                $columnaInicial
            );
        }


        /* ====================================================
         * CADENA
         *
         * Ejemplo:
         *
         * "Circuito Sur Mistico"
         * ====================================================
         */

        if ($caracter === '"') {

            $lexema = $this->LeerCadena();


            /*
             * Si no se encontró la comilla final.
             */
            if ($lexema === null) {

                return $this->NuevoToken(
                    ERROR,
                    null,
                    $lineaInicial,
                    $columnaInicial
                );
            }


            return $this->NuevoToken(
                CADENA,
                $lexema,
                $lineaInicial,
                $columnaInicial
            );
        }


        /* ====================================================
         * LEXEMA FIJO
         *
         * =
         * ,
         * [
         * ]
         *
         * <   >   <=   >=   ==   !=
         * :>
         * ====================================================
         */

        $elemento = $this->LeerLexemaFijo();


        if ($elemento !== null) {

            return $this->NuevoToken(
                $elemento['token'],
                $elemento['lexema'],
                $lineaInicial,
                $columnaInicial
            );
        }


        /* ====================================================
         * CARÁCTER DESCONOCIDO
         * ====================================================
         */

        $lexema = $caracter;

        $this->Avanzar();


        return $this->NuevoToken(
            ERROR,
            $lexema,
            $lineaInicial,
            $columnaInicial
        );
    }


    /* ========================================================
     * ES NÚMERO NEGATIVO
     *
     * True si el carácter actual es "-"
     * y el siguiente es un dígito.
     * ========================================================
     */

    private function EsNumeroNegativo(): bool
    {
        if ($this->codigo[$this->indice] !== '-') {
            return false;
        }

        $siguiente = $this->indice + 1;

        if ($siguiente >= strlen($this->codigo)) {
            return false;
        }

        return ctype_digit($this->codigo[$siguiente]);
    }


    /* ========================================================
     * OMITIR ESPACIOS EN BLANCO
     * ========================================================
     */

    private function OmitirEspacios(): void
    {
        while (!$this->FinCodigo()) {

            $caracter =
                $this->codigo[$this->indice];


            if (!ctype_space($caracter)) {
                break;
            }


            $this->Avanzar();
        }
    }


    /* ========================================================
     * LEER IDENTIFICADOR
     *
     * Regla:
     *
     * comienza con letra
     * después puede contener letras, números o "_"
     *
     * El "_" es indispensable porque varias palabras
     * reservadas están formadas por dos términos:
     *
     * INICIO_RUTA
     * INICIO_PARADA
     * FIN_RUTA
     * FIN_PARADA
     * PROBABILIDAD_LLUVIA
     * ========================================================
     */

    private function LeerIdentificador(): string
    {
        $lexema = '';


        while (!$this->FinCodigo()) {

            $caracter =
                $this->codigo[$this->indice];


            if (
                !ctype_alpha($caracter) &&
                !ctype_digit($caracter) &&
                $caracter !== '_'
            ) {
                break;
            }


            $lexema .= $caracter;


            $this->Avanzar();
        }


        return $lexema;
    }


    /* ========================================================
     * LEER NÚMERO
     *
     * Permite:
     *
     * 10
     * 120
     * 3.14
     * 0.5
     * -5
     * -16.115
     *
     * No permite:
     *
     * 12.4.5
     * 34-
     * ========================================================
     */

    private function LeerNumero(): ?string
    {
        $lexema = '';

        $cantidadPuntos = 0;


        /*
         * Signo negativo.
         *
         * Solo llega aquí si EsNumeroNegativo() confirmó
         * que el signo va seguido de un dígito.
         */
        if (
            !$this->FinCodigo() &&
            $this->codigo[$this->indice] === '-'
        ) {
            $lexema .= '-';

            $this->Avanzar();
        }


        while (!$this->FinCodigo()) {

            $caracter =
                $this->codigo[$this->indice];


            /*
             * Dígito
             */
            if (ctype_digit($caracter)) {

                $lexema .= $caracter;

                $this->Avanzar();

                continue;
            }


            /*
             * Punto decimal
             */
            if ($caracter === '.') {

                $cantidadPuntos++;


                /*
                 * Solo permitimos un punto decimal.
                 */
                if ($cantidadPuntos > 1) {

                    /*
                     * Consumimos el carácter que provocó
                     * el error para evitar quedar detenidos
                     * en la misma posición.
                     */
                    $this->Avanzar();

                    return null;
                }


                $lexema .= $caracter;

                $this->Avanzar();

                continue;
            }


            break;
        }


        return $lexema;
    }


    /* ========================================================
     * LEER CADENA
     *
     * Ejemplo:
     *
     * "Circuito Sur Mistico"
     *
     * En TOUR-LANG la cadena se escribe entre comillas
     * dobles y puede contener espacios.
     *
     * No puede contener un salto de línea: si aparece,
     * la cadena está mal cerrada y se devuelve null.
     * ========================================================
     */

    private function LeerCadena(): ?string
    {
        /*
         * Consumir comilla inicial.
         */
        $this->Avanzar();


        $lexema = '';


        while (!$this->FinCodigo()) {

            $caracter =
                $this->codigo[$this->indice];


            /*
             * Comilla de cierre.
             */
            if ($caracter === '"') {

                $this->Avanzar();

                return $lexema;
            }


            /*
             * Un salto de línea dentro de la cadena
             * significa que faltó la comilla de cierre.
             *
             * Nos detenemos aquí para no leer el resto
             * del archivo como si fuera una sola cadena.
             */
            if ($caracter === "\n") {
                return null;
            }


            $lexema .= $caracter;


            $this->Avanzar();
        }


        /*
         * Se llegó al final del código
         * sin encontrar la comilla final.
         */
        return null;
    }


    /* ========================================================
     * LEER LEXEMA FIJO
     *
     * Busca siempre el lexema válido más largo.
     * ========================================================
     */

    private function LeerLexemaFijo(): ?array
    {
        $elemento =
            $this->tablaLexica
                 ->BuscarLexemaMasLargo(
                     $this->codigo,
                     $this->indice
                 );


        if ($elemento === null) {
            return null;
        }


        /*
         * Avanzar tantos caracteres como
         * tenga el lexema encontrado.
         */
        for (
            $i = 0;
            $i < $elemento['longitud'];
            $i++
        ) {
            $this->Avanzar();
        }


        return $elemento;
    }


    /* ========================================================
     * AVANZAR UNA POSICIÓN
     * ========================================================
     */

    private function Avanzar(): void
    {
        if ($this->FinCodigo()) {
            return;
        }


        /*
         * Si encontramos salto de línea,
         * incrementamos línea y reiniciamos columna.
         */
        if (
            $this->codigo[$this->indice] === "\n"
        ) {

            $this->linea++;

            $this->columna = 1;

        } else {

            $this->columna++;
        }


        $this->indice++;
    }


    /* ========================================================
     * VERIFICAR FIN DEL CÓDIGO
     * ========================================================
     */

    private function FinCodigo(): bool
    {
        return
            $this->indice >= strlen($this->codigo);
    }
}


/* ============================================================
 * ANALIZADOR SINTACTICO (AUTOMATA DE PILA)
 *
 * Implementa el PDA diseñado en JFLAP para TOUR-LANG.
 *
 * - Los estados usan los MISMOS NOMBRES que el diagrama
 *   (q0, q1, ..., qArr, qF, q25_2, q26_2).
 * - Pila inicial: Z (fondo de pila).
 *
 *   P  se apila en INICIO_PARADA y se desapila en FIN_PARADA
 *   A  se apila en [               y se desapila en ]
 *   S  se apila en SI              y se desapila en FIN :>
 *   Z  se desapila en FIN_RUTA :>  (cierre del programa)
 *
 * - Aceptación: estado final qF, fin del archivo y pila vacía.
 * ============================================================
 */

class AnalizadorSintactico
{
    private const ESTADO_INICIAL = 'q0';
    private const ESTADO_FINAL   = 'qF';
    private const FONDO_PILA     = 'Z';

    private Tokenizador $tokenizador;

    private TablaLexica $tablaLexica;

    private string $estadoActual = self::ESTADO_INICIAL;

    private array $pila = [];

    private bool $seguimientoActivo;

    private array $seguimiento = [];

    private ?array $error = null;

    /*
     * $transiciones[estado][token] = [
     *     'sig'  => estado siguiente,
     *     'pop'  => símbolo a desapilar (o null),
     *     'push' => símbolo a apilar (o null)
     * ]
     *
     * Una combinación ausente representa un error sintáctico.
     */
    private array $transiciones = [];


    public function __construct(
        Tokenizador $tokenizador,
        TablaLexica $tablaLexica,
        bool $seguimientoActivo = true
    ) {
        $this->tokenizador = $tokenizador;
        $this->tablaLexica = $tablaLexica;
        $this->seguimientoActivo = $seguimientoActivo;

        $this->ConstruirTransiciones();
    }


    /*
     * Registra una regla individual de transición en el Autómata de Pila (PDA):
     * δ(estadoOrigen, tokenEntrada, simboloDesapilar) -> (estadoDestino, simboloApilar)
     */
    private function registrarReglaTransicion(
        string $estadoOrigen,
        int $tokenEntrada,
        string $estadoDestino,
        ?string $simboloDesapilar = null,
        ?string $simboloApilar = null
    ): void {
        $this->transiciones[$estadoOrigen][$tokenEntrada] = [
            'sig'  => $estadoDestino,
            'pop'  => $simboloDesapilar,
            'push' => $simboloApilar
        ];
    }


    /*
     * Registra un conjunto de tokens que comparten el mismo estado origen,
     * estado destino y operación sobre la pila del PDA.
     */
    private function registrarGrupoTransiciones(
        string $estadoOrigen,
        array $conjuntoTokens,
        string $estadoDestino,
        ?string $simboloDesapilar = null,
        ?string $simboloApilar = null
    ): void {
        foreach ($conjuntoTokens as $tokenEntrada) {
            $this->registrarReglaTransicion(
                $estadoOrigen,
                $tokenEntrada,
                $estadoDestino,
                $simboloDesapilar,
                $simboloApilar
            );
        }
    }


    private function ConstruirTransiciones(): void
    {
        /* ---------- Cabecera de la ruta ---------- */
        $this->registrarReglaTransicion('q0', INICIO_RUTA, 'q1');
        $this->registrarReglaTransicion('q1', CADENA,      'q2');
        $this->registrarReglaTransicion('q2', TERMINADOR,  'q3');
        $this->registrarReglaTransicion('q3', ORIGEN,      'q4');
        $this->registrarReglaTransicion('q4', CADENA,      'q5');
        $this->registrarReglaTransicion('q5', TERMINADOR,  'q6');

        /* ---------- Bloque de paradas (push P) ---------- */
        $this->registrarReglaTransicion('q6', INICIO_PARADA, 'q7', null, 'P');
        $this->registrarReglaTransicion('q7', CADENA,        'q8');
        $this->registrarReglaTransicion('q8', TERMINADOR,    'q9');

        /* ---------- Atributos locales de parada ---------- */
        $this->registrarGrupoTransiciones(
            'q9',
            [
                TIPO, DESCRIPCION, UBICACION, VISTA, COSTO,
                TRANSPORTE, DISTANCIA, DURACION,
                PRONOSTICO, TEMPERATURA, PROBABILIDAD_LLUVIA
            ],
            'q10'
        );

        $this->registrarReglaTransicion('q10', IGUAL, 'q11');

        /* ---------- Valor simple de atributo ---------- */
        $this->registrarGrupoTransiciones('q11', [CADENA, NUM, ID], 'q12');

        /* ---------- Arreglo de coordenadas [lat, lon] (push/pop A) ---------- */
        $this->registrarReglaTransicion('q11',  ALLAVE_CUAD, 'qArr', null, 'A');
        $this->registrarGrupoTransiciones('qArr', [NUM, COMA, ID], 'qArr');
        $this->registrarReglaTransicion('qArr', CLLAVE_CUAD, 'q12', 'A', null);

        $this->registrarReglaTransicion('q12', TERMINADOR, 'q9');

        /* ---------- Cierre de parada (pop P) ---------- */
        $this->registrarReglaTransicion('q9',  FIN_PARADA, 'q13', 'P', null);
        $this->registrarReglaTransicion('q13', TERMINADOR, 'q6');

        /* ---------- Destino de la ruta ---------- */
        $this->registrarReglaTransicion('q6',  DESTINO,    'q14');
        $this->registrarReglaTransicion('q14', CADENA,     'q15');
        $this->registrarReglaTransicion('q15', TERMINADOR, 'q16');

        /* ---------- Atributos globales de la ruta ---------- */
        $this->registrarGrupoTransiciones(
            'q16',
            [COSTO, TRANSPORTE, DISTANCIA, DURACION],
            'q17'
        );
        $this->registrarReglaTransicion('q17', IGUAL, 'q18');
        $this->registrarGrupoTransiciones('q18', [NUM, ID, CADENA], 'q19');
        $this->registrarReglaTransicion('q19', TERMINADOR, 'q16');

        /* ---------- Instrucción de visualización ---------- */
        $this->registrarReglaTransicion('q16', MOSTRAR_RUTA, 'q30');
        $this->registrarReglaTransicion('q30', TERMINADOR,   'q16');

        /* ---------- Bloque condicional SI (push S) ---------- */
        $this->registrarReglaTransicion('q16', SI, 'q20', null, 'S');
        $this->registrarGrupoTransiciones(
            'q20',
            [COSTO, DISTANCIA, DURACION, TEMPERATURA, PROBABILIDAD_LLUVIA],
            'q21'
        );
        $this->registrarGrupoTransiciones(
            'q21',
            [MENOR, MENOR_IGUAL, MAYOR, MAYOR_IGUAL, IGUALDAD, DISTINTO],
            'q22'
        );
        $this->registrarGrupoTransiciones('q22', [NUM, ID, CADENA], 'q23');
        $this->registrarReglaTransicion('q23', TERMINADOR, 'q24');

        /* ---------- Sentencias dentro de la rama SI ---------- */
        $this->registrarGrupoTransiciones('q24', [RECOMENDAR, MOSTRAR], 'q25');
        $this->registrarReglaTransicion('q25', CADENA,     'q26');
        $this->registrarReglaTransicion('q26', TERMINADOR, 'q24');

        /* ---------- Rama alternativa SINO ---------- */
        $this->registrarReglaTransicion('q24',   SINO,       'q27');
        $this->registrarReglaTransicion('q27',   TERMINADOR, 'q28');
        $this->registrarGrupoTransiciones('q28', [RECOMENDAR, MOSTRAR], 'q25_2');
        $this->registrarReglaTransicion('q25_2', CADENA,     'q26_2');
        $this->registrarReglaTransicion('q26_2', TERMINADOR, 'q28');

        /* ---------- Fin del condicional (pop S) ---------- */
        $this->registrarGrupoTransiciones('q24', [FIN], 'q29');
        $this->registrarGrupoTransiciones('q28', [FIN], 'q29');
        $this->registrarReglaTransicion('q29', TERMINADOR, 'q16', 'S', null);

        /* ---------- Cierre de la ruta (pop Z -> estado final qF) ---------- */
        $this->registrarReglaTransicion('q16', FIN_RUTA,   'q31');
        $this->registrarReglaTransicion('q31', TERMINADOR, 'qF', self::FONDO_PILA, null);
    }


    /* ========================================================
     * ANALIZAR
     *
     * Devuelve true si el programa es aceptado.
     * ========================================================
     */

    public function Analizar(): bool
    {
        $this->estadoActual = self::ESTADO_INICIAL;
        $this->pila = [self::FONDO_PILA];
        $this->seguimiento = [];
        $this->error = null;

        $paso = 1;

        while (true) {

            $token = $this->tokenizador->getToken();
            $estadoAnterior = $this->estadoActual;

            /*
             * Error léxico producido por el Tokenizador.
             */
            if ($token->token === ERROR) {
                $this->RegistrarPaso($paso, $estadoAnterior, $token, null, null, null);

                $this->error = $this->CrearError(
                    'lexico',
                    $token,
                    'El analizador lexico encontro un lexema no valido.'
                );

                return false;
            }


            /*
             * Estado final: solo se acepta el fin del archivo.
             */
            if ($estadoAnterior === self::ESTADO_FINAL) {

                if ($token->token === FIN_CODIGO) {
                    $this->RegistrarPaso($paso, $estadoAnterior, $token, $estadoAnterior, null, null);

                    if (!empty($this->pila)) {
                        $this->error = $this->CrearError(
                            'sintactico',
                            $token,
                            'La pila no quedo vacia al terminar el programa.'
                        );

                        return false;
                    }

                    return true;
                }

                $this->RegistrarPaso($paso, $estadoAnterior, $token, null, null, null);

                $this->error = $this->CrearError(
                    'sintactico',
                    $token,
                    $this->DescribirError($estadoAnterior, $token)
                );

                return false;
            }


            $transicion =
                $this->transiciones[$estadoAnterior][$token->token]
                ?? null;

            /*
             * No existe transición para (estado, token).
             */
            if ($transicion === null) {
                $this->RegistrarPaso($paso, $estadoAnterior, $token, null, null, null);

                $this->error = $this->CrearError(
                    'sintactico',
                    $token,
                    $this->DescribirError($estadoAnterior, $token)
                );

                return false;
            }


            /*
             * Operación sobre la pila (primero pop, luego push,
             * igual que en JFLAP).
             */
            if ($transicion['pop'] !== null) {

                $tope = empty($this->pila) ? null : end($this->pila);

                if ($tope !== $transicion['pop']) {
                    $this->RegistrarPaso($paso, $estadoAnterior, $token, null, null, null);

                    $this->error = $this->CrearError(
                        'pila',
                        $token,
                        sprintf(
                            'Se esperaba %s en el tope de la pila pero habia %s.',
                            $transicion['pop'],
                            $tope ?? 'pila vacia'
                        )
                    );

                    return false;
                }

                array_pop($this->pila);
            }

            if ($transicion['push'] !== null) {
                $this->pila[] = $transicion['push'];
            }

            $this->estadoActual = $transicion['sig'];

            $this->RegistrarPaso(
                $paso,
                $estadoAnterior,
                $token,
                $transicion['sig'],
                $transicion['pop'],
                $transicion['push']
            );

            $paso++;
        }
    }


    public function getEstadoActual(): string
    {
        return $this->estadoActual;
    }


    public function getPila(): array
    {
        return $this->pila;
    }


    public function getSeguimiento(): array
    {
        return $this->seguimiento;
    }


    public function getError(): ?array
    {
        return $this->error;
    }


    public function getTransiciones(): array
    {
        return $this->transiciones;
    }


    /* ========================================================
     * SEGUIMIENTO
     * ========================================================
     */

    private function PilaComoTexto(): string
    {
        /*
         * Se muestra de fondo a tope: Z P A
         */
        return empty($this->pila)
            ? '(vacia)'
            : implode(' ', $this->pila);
    }


    private function RegistrarPaso(
        int $paso,
        string $estadoActual,
        Token $token,
        ?string $estadoSiguiente,
        ?string $pop,
        ?string $push
    ): void {
        if (!$this->seguimientoActivo) {
            return;
        }

        $operacion = [];

        if ($pop !== null) {
            $operacion[] = "pop $pop";
        }

        if ($push !== null) {
            $operacion[] = "push $push";
        }

        $this->seguimiento[] = [
            'paso'            => $paso,
            'estadoActual'    => $estadoActual,
            'token'           => $token->token,
            'nombreToken'     => $token->nombre ?? 'TOKEN_' . $token->token,
            'lexema'          => $token->lexema,
            'linea'           => $token->linea,
            'columna'         => $token->columna,
            'estadoSiguiente' => $estadoSiguiente,
            'operacion'       => implode(', ', $operacion),
            'pila'            => $this->PilaComoTexto()
        ];
    }


    /* ========================================================
     * ERRORES
     * ========================================================
     */

    private function DescribirToken(int $token): string
    {
        $nombre = $this->tablaLexica->NombreDe($token)
            ?? 'TOKEN_' . $token;

        $dato = $this->tablaLexica->BuscarPorToken($token);

        /*
         * Para símbolos (:> = , [ ] < > ...) mostramos
         * también el lexema, para que el mensaje sea claro.
         */
        if ($dato !== null && !ctype_alpha($dato['lexema'][0])) {
            return $nombre . " ('" . $dato['lexema'] . "')";
        }

        return $nombre;
    }


    private function TokensEsperados(string $estado): array
    {
        if ($estado === self::ESTADO_FINAL) {
            return ['FIN_CODIGO'];
        }

        $tokens = array_keys($this->transiciones[$estado] ?? []);

        return array_map(
            fn (int $token): string => $this->DescribirToken($token),
            $tokens
        );
    }


    private function CrearError(
        string $tipo,
        Token $token,
        string $descripcion
    ): array {
        $esperados = $this->TokensEsperados($this->estadoActual);

        $nombre = $token->nombre ?? 'TOKEN_' . $token->token;

        $lexema = $token->lexema === null
            ? 'null'
            : "'{$token->lexema}'";

        $listaEsperados = empty($esperados)
            ? 'ninguno'
            : implode(', ', $esperados);

        return [
            'tipo'        => $tipo,
            'linea'       => $token->linea,
            'columna'     => $token->columna,
            'estado'      => $this->estadoActual,
            'token'       => $token->token,
            'nombreToken' => $nombre,
            'lexema'      => $token->lexema,
            'esperados'   => $esperados,
            'pila'        => $this->PilaComoTexto(),
            'descripcion' => $descripcion,
            'mensaje'     => sprintf(
                'Error %s en linea %d, columna %d: recibido %s (%s) '
                . 'en el estado %s; se esperaba: %s. %s',
                $tipo,
                $token->linea,
                $token->columna,
                $nombre,
                $lexema,
                $this->estadoActual,
                $listaEsperados,
                $descripcion
            )
        ];
    }


    private function DescribirError(string $estado, Token $token): string
    {
        /*
         * El archivo terminó antes de completar la estructura.
         */
        if ($token->token === FIN_CODIGO && $estado !== self::ESTADO_FINAL) {
            return 'El programa termino antes de completar la estructura '
                 . 'esperada; ' . $this->MensajePorEstado($estado);
        }

        return $this->MensajePorEstado($estado);
    }


    private function MensajePorEstado(string $estado): string
    {
        return match ($estado) {
            'q0'    => 'El programa debe comenzar con INICIO_RUTA.',
            'q1'    => 'Despues de INICIO_RUTA debe ir el nombre de la ruta entre comillas.',
            'q2'    => 'Falta el terminador :> despues del nombre de la ruta.',
            'q3'    => 'Despues de la cabecera debe ir ORIGEN.',
            'q4'    => 'Despues de ORIGEN debe ir el nombre del origen entre comillas.',
            'q5'    => 'Falta el terminador :> despues del origen.',
            'q6'    => 'Se esperaba INICIO_PARADA (otra parada) o DESTINO.',
            'q7'    => 'Despues de INICIO_PARADA debe ir el nombre de la parada entre comillas.',
            'q8'    => 'Falta el terminador :> despues del nombre de la parada.',
            'q9'    => 'Dentro de una parada se esperaba un atributo '
                     . '(TIPO, DESCRIPCION, UBICACION, VISTA, COSTO, TRANSPORTE, '
                     . 'DISTANCIA, DURACION, PRONOSTICO, TEMPERATURA, '
                     . 'PROBABILIDAD_LLUVIA) o FIN_PARADA.',
            'q10'   => 'Despues del atributo debe ir el signo =.',
            'q11'   => 'Despues de = debe ir un valor (CADENA, NUM, ID) o una lista [ ... ].',
            'qArr'  => 'Dentro de la lista solo se admiten NUM, ID, comas y el cierre ].',
            'q12'   => 'Falta el terminador :> al final de la asignacion.',
            'q13'   => 'Falta el terminador :> despues de FIN_PARADA.',
            'q14'   => 'Despues de DESTINO debe ir el nombre del destino entre comillas.',
            'q15'   => 'Falta el terminador :> despues del destino.',
            'q16'   => 'Despues del destino se esperaba un atributo global '
                     . '(COSTO, TRANSPORTE, DISTANCIA, DURACION), MOSTRAR_RUTA, '
                     . 'SI o FIN_RUTA.',
            'q17'   => 'Despues del atributo global debe ir el signo =.',
            'q18'   => 'Despues de = debe ir un valor (NUM, ID o CADENA).',
            'q19'   => 'Falta el terminador :> al final de la asignacion.',
            'q30'   => 'Falta el terminador :> despues de MOSTRAR_RUTA.',
            'q20'   => 'Despues de SI debe ir COSTO, DISTANCIA, DURACION, '
                     . 'TEMPERATURA o PROBABILIDAD_LLUVIA.',
            'q21'   => 'Se esperaba un operador relacional (<, <=, >, >=, ==, !=).',
            'q22'   => 'Despues del operador debe ir el valor a comparar (NUM, ID o CADENA).',
            'q23'   => 'Falta el terminador :> despues de la condicion del SI.',
            'q24'   => 'Dentro del SI se esperaba RECOMENDAR, MOSTRAR, SINO o FIN.',
            'q25'   => 'Despues de RECOMENDAR o MOSTRAR debe ir un texto entre comillas.',
            'q26'   => 'Falta el terminador :> despues de la sentencia.',
            'q27'   => 'Falta el terminador :> despues de SINO.',
            'q28'   => 'Dentro del SINO se esperaba RECOMENDAR, MOSTRAR o FIN.',
            'q25_2' => 'Despues de RECOMENDAR o MOSTRAR debe ir un texto entre comillas.',
            'q26_2' => 'Falta el terminador :> despues de la sentencia.',
            'q29'   => 'Falta el terminador :> despues de FIN.',
            'q31'   => 'Falta el terminador :> despues de FIN_RUTA.',
            'qF'    => 'No se permite codigo adicional despues de FIN_RUTA :>.',
            default => 'El token recibido no tiene una transicion valida.'
        };
    }
}


/* ============================================================
 * DEMOSTRACION EJECUTABLE
 * ============================================================
 */

function AnalizarYMostrar(string $titulo, string $codigo): void
{
    $tablaLexica = new TablaLexica();

    $parser = new AnalizadorSintactico(
        new Tokenizador($codigo, $tablaLexica),
        $tablaLexica,
        true
    );

    $valido = $parser->Analizar();

    echo "$titulo\n";
    echo "============================================================\n\n";

    printf(
        "%-5s %-8s %-22s %-34s %-9s %-14s %-12s\n",
        'Paso',
        'Estado',
        'Token',
        'Lexema',
        'Siguiente',
        'Operacion',
        'Pila'
    );

    foreach ($parser->getSeguimiento() as $paso) {
        printf(
            "%-5d %-8s %-22s %-34s %-9s %-14s %-12s\n",
            $paso['paso'],
            $paso['estadoActual'],
            $paso['nombreToken'],
            substr($paso['lexema'] ?? 'null', 0, 33),
            $paso['estadoSiguiente'] ?? 'ERROR',
            $paso['operacion'],
            $paso['pila']
        );
    }

    echo "\nResultado: ", $valido ? 'ACEPTADO' : 'RECHAZADO', "\n";

    if (!$valido) {
        echo $parser->getError()['mensaje'], "\n";
    }

    echo "\n\n";
}


function EjecutarDemostracion(): void
{
    $programaValido = <<<'TOURLANG'
INICIO_RUTA "Circuito Sur Mistico" :>
ORIGEN "Puno" :>
INICIO_PARADA "Chucuito" :>
TIPO = "HISTORICO" :>
DESCRIPCION = "Parada fotografica y cultural" :>
FIN_PARADA :>
INICIO_PARADA "Aramu Muru" :>
UBICACION = [-16.115,-69.425] :>
TIPO = "MISTICO" :>
DESCRIPCION = "Puerta interdimensional" :>
VISTA = "SATELITE" :>
FIN_PARADA :>
DESTINO "Puno" :>
COSTO = 55 :>
SI COSTO <= 50 :>
RECOMENDAR "Ruta economica" :>
SINO :>
MOSTRAR "Ruta fuera del presupuesto estandar" :>
FIN :>
MOSTRAR_RUTA :>
FIN_RUTA :>
TOURLANG;

    /* Falta el terminador :> después del COSTO. */
    $programaInvalido = <<<'TOURLANG'
INICIO_RUTA "Circuito Sur Mistico" :>
ORIGEN "Puno" :>
DESTINO "Puno" :>
COSTO = 55
MOSTRAR_RUTA :>
FIN_RUTA :>
TOURLANG;

    echo "<pre>";

    echo "FLUJO DE TOKENS\n";
    echo "============================================================\n\n";

    $tablaLexica = new TablaLexica();
    $tokenizador = new Tokenizador($programaValido, $tablaLexica);

    while (true) {
        $token = $tokenizador->getToken();
        $token->Mostrar();

        if ($token->token === FIN_CODIGO) {
            break;
        }
    }

    echo "\n\n";

    AnalizarYMostrar('ANALISIS SINTACTICO - PROGRAMA VALIDO', $programaValido);
    AnalizarYMostrar('ANALISIS SINTACTICO - PROGRAMA CON ERROR', $programaInvalido);

    echo "</pre>";
}


if (
    PHP_SAPI === 'cli' ||
    (isset($_SERVER['SCRIPT_FILENAME']) && realpath($_SERVER['SCRIPT_FILENAME']) === __FILE__)
) {
    EjecutarDemostracion();
}