import ply.lex as lex

# Palabras reservadas con su tipo de token específico
keywords = {
    "abstract": "ABSTRACT", "array": "ARRAY", "as": "AS", "break": "BREAK", 
    "callable": "CALLABLE", "case": "CASE", "catch": "CATCH", "class": "CLASS", 
    "clone": "CLONE", "const": "CONST", "continue": "CONTINUE", "declare": "DECLARE", 
    "default": "DEFAULT", "do": "DO", "echo": "ECHO", "else": "ELSE", 
    "elseif": "ELSEIF", "empty": "EMPTY", "enddeclare": "ENDDECLARE", 
    "endfor": "ENDFOR", "endforeach": "ENDFOREACH", "endif": "ENDIF", 
    "endswitch": "ENDSWITCH", "endwhile": "ENDWHILE", "enum": "ENUM", 
    "eval": "EVAL", "exit": "EXIT", "extends": "EXTENDS", "final": "FINAL", 
    "finally": "FINALLY", "fn": "FN", "for": "FOR", "foreach": "FOREACH", 
    "function": "FUNCTION", "global": "GLOBAL", "goto": "GOTO", "if": "IF", 
    "implements": "IMPLEMENTS", "include": "INCLUDE", "include_once": "INCLUDE_ONCE", 
    "instanceof": "INSTANCEOF", "insteadof": "INSTEADOF", "interface": "INTERFACE", 
    "isset": "ISSET", "list": "LIST", "match": "MATCH", "namespace": "NAMESPACE", 
    "new": "NEW", "print": "PRINT", "private": "PRIVATE", "protected": "PROTECTED", 
    "public": "PUBLIC", "readonly": "READONLY", "require": "REQUIRE", 
    "require_once": "REQUIRE_ONCE", "return": "RETURN", "static": "STATIC", 
    "switch": "SWITCH", "throw": "THROW", "trait": "TRAIT", "try": "TRY", 
    "unset": "UNSET", "use": "USE", "var": "VAR", "while": "WHILE", 
    "yield": "YIELD", "yield from": "YIELD_FROM"
}

# Lista de tokens
tokens = (
    # Literales
    "VARIABLE", "LNUMBER", "DNUMBER", "CONSTANT_ENCAPSED_STRING", "STRING",
    
    # Tags
    "OPEN_TAG", "OPEN_TAG_WITH_ECHO", "CLOSE_TAG",
    
    # Operadores de Asignación Combinados
    "PLUS_EQUAL", "MINUS_EQUAL", "MUL_EQUAL", "DIV_EQUAL", "MOD_EQUAL",
    "AND_EQUAL", "OR_EQUAL", "XOR_EQUAL", "SL_EQUAL", "SR_EQUAL",
    "CONCAT_EQUAL", "POW_EQUAL",
    
    # Operadores Lógicos
    "BOOLEAN_AND", "BOOLEAN_OR", "LOGICAL_AND", "LOGICAL_OR", "LOGICAL_XOR",
    
    # Operadores de Comparación
    "IS_EQUAL", "IS_IDENTICAL", "IS_NOT_EQUAL", "IS_NOT_IDENTICAL",
    "IS_GREATER_OR_EQUAL", "IS_SMALLER_OR_EQUAL", "SPACESHIP",

    # Operadores Básicos y Puntuación
    "PLUS", "MINUS", "TIMES", "DIVIDE", "MODULO", "EQUAL",
    "LPAREN", "RPAREN", "LBRACE", "RBRACE", "LBRACKET", "RBRACKET",
    "SEMICOLON", "COMMA", "DOT", "GT", "LT", "NOT", "BIT_OR", "BIT_AND", "BIT_XOR", "TERNARY", "COLON",
    
    # Otros
    "INC", "DEC", "OBJECT_OPERATOR", "NULLSAFE_OBJECT_OPERATOR",
    "DOUBLE_ARROW", "NS_SEPARATOR", "ELLIPSIS",
) + tuple(keywords.values())

# Reglas de tokens simples (Expresiones regulares)
t_ignore_WHITESPACE = r'\s+'
t_OPEN_TAG = r'<\?php|<\?'
t_OPEN_TAG_WITH_ECHO = r'<\?='
t_CLOSE_TAG = r'\?>'

# Comentarios
def t_COMMENT(t):
    r'//.*|/\*[\s\S]*?\*/|\#.*'
    pass

# Operadores de Asignación
t_PLUS_EQUAL = r'\+='
t_MINUS_EQUAL = r'-='
t_MUL_EQUAL = r'\*='
t_DIV_EQUAL = r'/='
t_MOD_EQUAL = r'%='
t_AND_EQUAL = r'&='
t_OR_EQUAL = r'\|='
t_XOR_EQUAL = r'\^='
t_SL_EQUAL = r'<<='
t_SR_EQUAL = r'>>='
t_CONCAT_EQUAL = r'\.='
t_POW_EQUAL = r'\*\*='

# Lógicos
t_BOOLEAN_AND = r'&&'
t_BOOLEAN_OR = r'\|\|'
t_LOGICAL_AND = r'and'
t_LOGICAL_OR = r'or'
t_LOGICAL_XOR = r'xor'

# Comparación
t_IS_IDENTICAL = r'==='
t_IS_NOT_IDENTICAL = r'!=='
t_IS_EQUAL = r'=='
t_IS_NOT_EQUAL = r'!=|<>'
t_IS_GREATER_OR_EQUAL = r'>='
t_IS_SMALLER_OR_EQUAL = r'<='
t_SPACESHIP = r'<=>'

# Incremento/Decremento/Otros objetos
t_INC = r'\+\+'
t_DEC = r'--'
t_OBJECT_OPERATOR = r'->'
t_NULLSAFE_OBJECT_OPERATOR = r'\?->'
t_DOUBLE_ARROW = r'=>'
t_NS_SEPARATOR = r'\\'
t_ELLIPSIS = r'\.\.\.'

# Operadores Básicos (Un solo caracter)
t_PLUS = r'\+'
t_MINUS = r'-'
t_TIMES = r'\*'
t_DIVIDE = r'/'
t_MODULO = r'%'
t_EQUAL = r'='
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LBRACE = r'\{'
t_RBRACE = r'\}'
t_LBRACKET = r'\['
t_RBRACKET = r'\]'
t_SEMICOLON = r';'
t_COMMA = r','
t_DOT = r'\.'
t_GT = r'>'
t_LT = r'<'
t_NOT = r'!'
t_BIT_OR = r'\|'
t_BIT_AND = r'&'
t_BIT_XOR = r'\^'
t_TERNARY = r'\?'
t_COLON = r':'

def t_VARIABLE(t):
    r'\$[a-zA-Z_][a-zA-Z0-9_]*'
    return t

def t_LNUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_DNUMBER(t):
    r'\d+\.\d+'
    t.value = float(t.value)
    return t

def t_CONSTANT_ENCAPSED_STRING(t):
    r'\"(\\.|[^\\"])*\"|\'(\\.|[^\\\'])*\''
    return t

def t_STRING(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = keywords.get(t.value.lower(), "STRING") # Case insensitive keywords usually? PHP keywords are case insensitive.
    return t

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# Lista de errores léxicos
error_list = []

def t_error(t):
    """Manejo de errores léxicos"""
    error_message = f"Error Léxico: Carácter inesperado '{t.value[0]}' en la línea {t.lineno}."
    error_list.append(error_message)
    t.lexer.skip(1)

# Inicializar lexer
lexer = lex.lex()

def analyze_code(code):
    """
    Analiza el código y devuelve los tokens hallados y la lista de errores.
    Reinicia la lista de errores en cada llamada.
    """
    global error_list
    error_list = []
    
    lexer.input(code)
    tokens_list = []
    
    # Iterar para forzar el procesamiento y captura de errores
    for tok in lexer:
        tokens_list.append(tok)
    
    return tokens_list, error_list
