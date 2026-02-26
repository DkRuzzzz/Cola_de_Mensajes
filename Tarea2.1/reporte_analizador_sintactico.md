# Reporte del Analizador Sintáctico (Parser) del Compilador PHP

## 1. Contexto: Propósito del Analizador Sintáctico

El **Analizador Sintáctico** (o *Parser*) es la segunda fase del proceso de compilación, ubicada inmediatamente después del Análisis Léxico. Su objetivo primordial es recibir el flujo de tokens generado por el *Lexer* y determinar si dichos tokens forman estructuras de código válidas según las reglas gramaticales del lenguaje (en este caso, un subconjunto de PHP).

Mientras que el Lexer responde a la pregunta *"¿Es esta palabra válida?"*, el Parser responde a *"¿Tienen sentido estas palabras juntas en este orden?"*. Adicionalmente, nuestro parser genera una representación intermedia y valida errores semánticos básicos (como el uso de variables no definidas).

---

## 2. Interacción con el Analizador Léxico

> **Nota sobre la Arquitectura**: El compilador contiene un parser heredado (`analizadorSintactico/parser.py`), sin embargo, el parser **activo y operativo** que se utiliza en el flujo real del compilador es `php_parser.py` (ubicado en la carpeta `codigoIntermedio (Optimización)`). Este archivo condensa el Análisis Sintáctico, el Análisis Semántico y la Generación de Código Intermedio en una sola pasada.

El analizador sintáctico tiene una dependencia estricta del analizador léxico. 

1. **Definición Compartida de Tokens**: El parser (`php_parser.py`) importa la misma lista de tokens generada en `analizadorLexico/lexer_php.py`. Herramientas como PLY (Python Lex-Yacc) exigen que el Parser conozca por nombre todos los tokens (`VARIABLE`, `LNUMBER`, `IF`, `WHILE`, etc.) que el Lexer es capaz de producir.
2. **Consumo de Flujo**: Al iniciar el análisis (`parser.parse(code, lexer=lexer_php.lexer)`), el parser le solicita subyacentemente tokens uno por uno al lexer. 
3. **Manejo de Errores Escalonado**: Si el lexer encuentra un carácter ilegal, lo reporta y el análisis puede detenerse. Si todos los caracteres son válidos léxicamente, pero están en un orden incorrecto (ej. `$var = + * 5;`), el parser toma el control y emite un **Error Sintáctico**.

---

## 3. Codificación, Lógica y Parseo

El parser fue diseñado usando PLY (`ply.yacc`), una implementación en Python de la herramienta estándar Yacc (Yet Another Compiler-Compiler).

### Construcción del Árbol y AST
Las herramientas como Yacc funcionan de *"Abajo hacia Arriba"* (Bottom-Up), específicamente usando un enfoque de análisis **LALR(1)**. Esto significa que lee tokens de izquierda a derecha con 1 token de anticipación para decidir si agrupar (*reducir*) una serie de tokens en una estructura lógica superior.

En nuestro código (`php_parser.py`), las reglas gramaticales se declaran en los *docstrings* de las funciones de Python, por ejemplo:
```python
def p_statement_assignment(p):
    '''statement : VARIABLE EQUAL expression SEMICOLON'''
    define_variable(p[1])         # Acción Semántica
    p[0] = ('assign', p[1], p[3]) # Generación del Nodo AST
```
Aquí la función se ejecuta sólo cuando el parser encuentra una coincidencia exacta con `[VARIABLE] [=] [expresion] [;]`. En ese momento, guarda en `p[0]` la representación lógica de esa asignación para que funciones de nivel superior la usen.

### Control de Tabla de Símbolos (Semántica Básica)
El parser incluye reglas semánticas ligeras acopladas:
- Cada vez que se declara una asignación o parámetro, se guarda la variable en un `symbol_table`.
- Cuando una regla gramatical consume una variable como parte de una expresión `p_expression_variable(...)`, invoca a `check_variable_defined(...)`. Si la variable no existe en la tabla de símbolos, se genera un **Error Semántico**.

---

## 4. Gramáticas Implementadas

Las reglas gramaticales se codificaron en notación **BNF (Backus-Naur Form)**. A continuación, las más relevantes:

| Estructura | Gramática implementada (Simplificada) | Explicación |
|------------|---------------------------------------|-------------|
| **Bloque Principal** | `program : OPEN_TAG statements CLOSE_TAG` | Exige que el código inicie y (opcionalmente) acabe con tags PHP. |
| **Sentencias (Múltiples)** | `statements : statement statements \| empty` | Regla recursiva para admitir una lista infinita de líneas de código. |
| **Asignaciones** | `statement : VARIABLE EQUAL expression SEMICOLON` | Exige nombre, `=`, un cálculo/valor y finalizar con `;`. |
| **Bucle While** | `statement : WHILE LPAREN expression RPAREN block` | Estructura rígida de palabra reservada, paréntesis de condición y cuerpo de bloque `{}`. |
| **Condicional If** | `statement : IF LPAREN exp RPAREN block [ELSE block]` | Condicional estándar con soporte opcional para clausula subordinada *else*. |
| **Impresión** | `statement : ECHO expression SEMICOLON` | Comando echo básico (no soporta interpolación múltiple con comas). |
| **Expresiones Arit.** | `expression : expression PLUS expression` | Resolución recursiva de cálculos matemáticos. |
| **Llamadas a Func.** | `expression : STRING LPAREN args RPAREN` | Identificación de ejecución de funciones integradas o de usuario. |

> **Limitación conocida**: Debido a la naturaleza prototípica, las asociaciones de prioridad matemática no están declaradas estrictamente (`%prec`) en todas las expresiones bidimensionales complejas, operando bajo asociatividad por defecto al consumir la gramática de izquierda a derecha.

---

## 5. Ejemplos de Ejecución

Para validar la correcta funcionalidad, construimos un script de ejecución aislada `test_syntax_only.py`. A continuación, se presentan dos casos de uso, evidenciando comportamiento ante código correcto e incorrecto.

### Caso 1: Corrida Exitosa

Este caso muestra un código PHP funcional con operaciones, condicionales y ciclos, con sintaxis estrictamente válida.

**Archivo `ejemplos/syntax_exito.php`:**
```php
<?php
// Ejemplo de prueba exitosa para analisis sintáctico
$num1 = 15;
$num2 = 25;
$suma = $num1 + $num2;

if ($suma > 30) {
    echo "La suma es mayor";
} else {
    echo "La suma es menor";
}

while ($num1 < 20) {
    $num1 = $num1 + 1;
}
?>
```

**Salida en Terminal (Éxito):**
```text
=== ANÁLISIS SINTÁCTICO DE: ejemplos/syntax_exito.php ===

-> Ejecutando Análisis Sintáctico y Semántico...
 Resultado: ÉXITO - No se encontraron errores sintácticos ni semánticos

AST parseado temporalmente generado a Código Intermedio:
  $num1 = 15
  $num2 = 25
  t1 = $num1 + $num2
  $suma = t1
  if $suma > 30 goto L1
  goto L2
  L1:
  print "La suma es mayor"
  goto L3
  L2:
  print "La suma es menor"
  L3:
  L4:
  if $num1 < 20 goto L5
  goto L6
  L5:
  t2 = $num1 + 1
  $num1 = t2
  goto L4
  L6:
```
*Interpretación: El Analizador Sintáctico comprendió al 100% la estructura jerárquica, logrando convertirla con éxito al código 3AC (Código de Tres Direcciones).*

---

### Caso 2: Corrida No Exitosa (Con Errores)

Este caso inserta deliberadamente fallos en las reglas de gramática de asignación y condicionales. 

**Archivo `ejemplos/syntax_error.php`:**
```php
<?php
// Ejemplo de prueba con error de sintaxis y falta de variables
$precio = 100;
// Error Sintáctico: Falta punto y coma en la siguiente línea
$descuento = 20

// Error Semántico: Variable '$impuesto' no definida
$total = $precio - $impuesto;

// Error Sintáctico: Estructura mal formada (falta paréntesis de cierre)
if ($total > 80 {
    echo "Caro";
}
?>
```

**Salida en Terminal (Fallo Logrado):**
```text
=== ANÁLISIS SINTÁCTICO DE: ejemplos/syntax_error.php ===

-> Ejecutando Análisis Sintáctico y Semántico...
 Resultado: FALLÓ

--- ERRORES SINTÁCTICOS ---
 - Error de Sintaxis: Token inesperado '$total' en línea 8

Compilación abortada.
```
*Interpretación: En la línea 6 se declara `$descuento = 20` sin punto y coma. El parser (LALR) mira el siguiente token en la línea 8 que resulta ser la variable `$total`. Porque la gramática de asignación exige rígidamente un `SEMICOLON` al final, cuando encuentra a `$total` se rompe la regla y eleva una excepción sintáctica precisa con el token no coincidente, abortando adecuadamente antes de traducir código.*
