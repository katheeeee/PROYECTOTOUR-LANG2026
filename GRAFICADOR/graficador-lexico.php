<?php

/* ============================================================
 * TOKENS DEL LENGUAJE
 * ============================================================
 */

/* ============================================================
 * PALABRAS RESERVADAS
 *
 * Estructura de una ruta:
 *
 * INICIO_RUTA  ...  FIN_RUTA
 *
 * Estructura de una parada:
 *
 * INICIO_PARADA  ...  FIN_PARADA
 *
 * Condicional:
 *
 * SI ... SINO ... FIN
 * ============================================================
 */

const INICIO_TOUR         = 0;
const FIN_TOUR            = 1;
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
const MOSTRAR_TOUR        = 22;


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

        $this->Agregar(INICIO_TOUR,         'INICIO_TOUR',         'palabra_reservada');
        $this->Agregar(FIN_TOUR,            'FIN_TOUR',            'palabra_reservada');
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
        $this->Agregar(MOSTRAR_TOUR,        'MOSTRAR_TOUR',        'palabra_reservada');

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
         * $porToken[INICIO_TOUR]
         */
        $this->porToken[$token] = $dato;


        /*
         * Índice por LEXEMA
         *
         * Ejemplo:
         *
         * $porLexema['INICIO_TOUR']
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
     * $tablaLexica->NombreDe(INICIO_TOUR)
     * devuelve 'INICIO_TOUR'
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
     * INICIO_TOUR
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
 * PRUEBA DEL TOKENIZADOR
 * ============================================================
 */


/*
 * Código fuente de prueba.
 *
 * Mismo fragmento de TOUR-LANG, solo que repartido
 * en varias líneas para poder observar el conteo
 * de línea y columna del reporte.
 */

$codigo = <<<'TOURLANG'
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


/*
 * Crear TablaLexica.
 */

$tablaLexica =
    new TablaLexica();


/*
 * Crear Tokenizador.
 */

$tokenizador =
    new Tokenizador(
        $codigo,
        $tablaLexica
    );


/* ============================================================
 * MOSTRAR FLUJO DE TOKENS
 * ============================================================
 */

echo "<pre>";

echo "FLUJO DE TOKENS\n";

echo "============================================================\n\n";


while (true) {

    /*
     * Cada llamada devuelve UN Token.
     */

    $token =
        $tokenizador->getToken();


    /*
     * Mostrar token.
     */

    $token->Mostrar();


    /*
     * Terminar cuando encontramos FIN_CODIGO,
     * es decir, cuando el archivo se terminó de leer.
     */

    if ($token->token === FIN_CODIGO) {
        break;
    }
}


echo "</pre>";