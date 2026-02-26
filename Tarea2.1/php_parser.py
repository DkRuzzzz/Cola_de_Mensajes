import ply.yacc as yacc
import sys
import os

# Asegurar que podemos importar desde el directorio hermano analizadorLexico
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from analizadorLexico.lexer_php import tokens

# Contadores globales para temporales y etiquetas
temp_count = 0
label_count = 0

# Listas de errores
syntax_errors = []
semantic_errors = []

# Tabla de Símbolos simple (Set de variables definidas)
symbol_table = set()

def new_temp():
    global temp_count
    temp_count += 1
    return f"t{temp_count}"

def new_label():
    global label_count
    label_count += 1
    return f"L{label_count}"

# --- Reglas Semánticas ---
def check_variable_defined(var_name, lineno):
    """Verifica si la variable está definida, si no, registra error semántico."""
    if var_name not in symbol_table:
        msg = f"Error Semántico en línea {lineno}: Variable '{var_name}' no definida."
        semantic_errors.append(msg)

def define_variable(var_name):
    """Registra una variable en la tabla de símbolos."""
    symbol_table.add(var_name)

# --- Gramáticas y construcción del AST ---

def p_program(p):
    '''program : OPEN_TAG statements CLOSE_TAG
               | OPEN_TAG statements'''
    p[0] = p[2]

def p_statements(p):
    '''statements : statement statements
                  | statement
                  | empty'''
    if len(p) == 3:
        p[0] = [p[1]] + p[2]
    elif len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = []

def p_statement_assignment(p):
    '''statement : VARIABLE EQUAL expression SEMICOLON'''
    # Semántica: Se define la variable
    define_variable(p[1])
    p[0] = ('assign', p[1], p[3])

def p_statement_echo(p):
    '''statement : ECHO expression SEMICOLON'''
    p[0] = ('echo', p[2])

def p_statement_if(p):
    '''statement : IF LPAREN expression RPAREN block
                 | IF LPAREN expression RPAREN block ELSE block'''
    if len(p) == 6:
        p[0] = ('if', p[3], p[5], None)
    else:
        p[0] = ('if', p[3], p[5], p[7])

def p_statement_while(p):
    '''statement : WHILE LPAREN expression RPAREN block'''
    p[0] = ('while', p[3], p[5])

def p_statement_function(p):
    '''statement : FUNCTION STRING LPAREN params RPAREN block'''
    # Todo: Agregar params a tabla de símbolos local (scope)
    # Por simplificación actual, las agregamos a la global para evitar falsos positivos
    # en este proof-of-concept
    p[0] = ('function', p[2], p[4], p[6])

def p_params(p):
    '''params : VARIABLE
              | VARIABLE COMMA params
              | empty'''
    if len(p) >= 2 and p[1]:
        define_variable(p[1]) # Definir parametro como variable existente
        
    if len(p) == 2:
        p[0] = [p[1]] if p[1] else []
    elif len(p) == 4:
        # p[3] ya viene procesado recursivamente? No, p[3] es params
        # Si params_opt recursivo define vars, ok.
        p[0] = [p[1]] + p[3]
    else:
        p[0] = []

def p_statement_return(p):
    '''statement : RETURN expression SEMICOLON'''
    p[0] = ('return', p[2])

def p_expression_comparison(p):
    '''expression : expression GT expression
                  | expression LT expression
                  | expression IS_GREATER_OR_EQUAL expression
                  | expression IS_SMALLER_OR_EQUAL expression
                  | expression IS_EQUAL expression
                  | expression IS_NOT_EQUAL expression'''
    p[0] = (p[2], p[1], p[3])

def p_expression_binop(p):
    '''expression : expression PLUS expression
                  | expression MINUS expression
                  | expression TIMES expression
                  | expression DIVIDE expression
                  | expression MODULO expression'''
    p[0] = (p[2], p[1], p[3])

def p_expression_group(p):
    '''expression : LPAREN expression RPAREN'''
    p[0] = p[2]

def p_expression_number(p):
    '''expression : LNUMBER
                  | DNUMBER'''
    p[0] = p[1]

def p_expression_variable(p):
    '''expression : VARIABLE'''
    # Semántica: Verificar uso
    check_variable_defined(p[1], p.lineno(1))
    p[0] = ('var', p[1])

def p_expression_string(p):
    '''expression : CONSTANT_ENCAPSED_STRING'''
    p[0] = p[1]

def p_expression_function_call(p):
    '''expression : STRING LPAREN args RPAREN'''
    p[0] = ('call', p[1], p[3])

def p_args(p):
    '''args : expression
            | expression COMMA args
            | empty'''
    if len(p) == 2:
        p[0] = [p[1]] if p[1] else []
    elif len(p) == 4:
        p[0] = [p[1]] + p[3]
    else:
        p[0] = []    

def p_block(p):
    '''block : LBRACE statements RBRACE
             | LBRACE RBRACE'''
    if len(p) == 4:
        p[0] = p[2]
    else:
        p[0] = []

def p_empty(p):
    'empty :'
    p[0] = []

def p_error(p):
    if p:
        msg = f"Error de Sintaxis: Token inesperado '{p.value}' en línea {p.lineno}"
        syntax_errors.append(msg)
        # Intentar recuperación simple: descartar tokens hasta punto y coma
        # parser.errok() 
    else:
        syntax_errors.append("Error de Sintaxis: Fin de archivo inesperado")

# Construimos el parser
parser = yacc.yacc()


# GENERACIÓN DE CÓDIGO 3 DIRECCIONES (Igual que antes)
def gen_code_statement(stmt):
    if not stmt: return []
    stype = stmt[0]

    if stype == 'assign':
        var_name = stmt[1]
        expr = stmt[2]
        code_expr, place_expr = gen_code_expression(expr)
        code_expr.append(f"{var_name} = {place_expr}")
        return code_expr

    elif stype == 'echo':
        expr = stmt[1]
        code_expr, place_expr = gen_code_expression(expr)
        code_expr.append(f"print {place_expr}")
        return code_expr

    elif stype == 'if':
        # ('if', cond_expr, block_if, block_else)
        cond_expr = stmt[1]
        block_if = stmt[2] # Lista de sentencias
        block_else = stmt[3]

        label_true = new_label()
        label_false = new_label()
        label_end = new_label()

        code_cond = gen_code_conditional(cond_expr, label_true, label_false)

        code_if = []
        if block_if:
            for s in block_if:
                code_if += gen_code_statement(s)

        code_else = []
        if block_else:
            for s in block_else:
                code_else += gen_code_statement(s)

        if block_else:
            return (
                code_cond +
                [f"{label_true}:"] +
                code_if +
                [f"goto {label_end}"] +
                [f"{label_false}:"] +
                code_else +
                [f"{label_end}:"]
            )
        else:
            return (
                code_cond +
                [f"{label_true}:"] +
                code_if +
                [f"{label_false}:"]
            )

    elif stype == 'while':
        cond_expr = stmt[1]
        block_while = stmt[2]

        label_start = new_label()
        label_true = new_label()
        label_false = new_label()

        code_loop = []
        for s in block_while:
            code_loop += gen_code_statement(s)

        code_cond = gen_code_conditional(cond_expr, label_true, label_false)

        return [
            f"{label_start}:"
        ] + code_cond + [
            f"{label_true}:"
        ] + code_loop + [
            f"goto {label_start}",
            f"{label_false}:"
        ]

    elif stype == 'function':
        fn_name = stmt[1]
        # logic for params?
        fn_block = stmt[3]

        code_fn = [f"func {fn_name}"]
        for s in fn_block:
            code_fn += gen_code_statement(s)
        code_fn.append(f"endfunc")
        return code_fn

    elif stype == 'return':
        expr = stmt[1]
        code_expr, place_expr = gen_code_expression(expr)
        code_expr.append(f"return {place_expr}")
        return code_expr
    
    elif isinstance(stmt, tuple) and stmt[0] == 'call':
        code_expr, place_expr = gen_code_expression(stmt)
        return code_expr

    else:
        return [f"# Sentencia no reconocida: {stmt}"]


def gen_code_expression(expr):
    if isinstance(expr, (int, float)):
        return ([], str(expr))

    if isinstance(expr, str) and (expr.startswith('"') or expr.startswith("'")):
        return ([], expr)

    if isinstance(expr, tuple):
        op = expr[0]
        if op == 'var':
            return ([], expr[1])
        
        elif op == 'call':
            fn_name = expr[1]
            args = expr[2]
            code = []
            param_places = []
            for arg in args:
                c, p = gen_code_expression(arg)
                code += c
                param_places.append(p)
            for p in param_places:
                code.append(f"param {p}")
            tmp = new_temp()
            code.append(f"{tmp} = call {fn_name}, {len(args)}")
            return (code, tmp)

        elif len(expr) == 3: # binary op
            left_expr = expr[1]
            right_expr = expr[2]
            code_left, place_left = gen_code_expression(left_expr)
            code_right, place_right = gen_code_expression(right_expr)
            tmp = new_temp()
            code = code_left + code_right
            code.append(f"{tmp} = {place_left} {op} {place_right}")
            return (code, tmp)

    return ([], "0")


def gen_code_conditional(expr, label_true, label_false):
    if isinstance(expr, tuple):
        op = expr[0]
        # Si es un operador de comparación
        if op in ['>', '<', '>=', '<=', '==', '!=']:
            left_expr = expr[1]
            right_expr = expr[2]
            code_left, place_left = gen_code_expression(left_expr)
            code_right, place_right = gen_code_expression(right_expr)
            code = code_left + code_right
            code.append(f"if {place_left} {op} {place_right} goto {label_true}")
            code.append(f"goto {label_false}")
            return code

    code_expr, place_expr = gen_code_expression(expr)
    code_expr.append(f"if {place_expr} != 0 goto {label_true}")
    code_expr.append(f"goto {label_false}")
    return code_expr

def parse_and_validate(code):
    """
    Función principal para parsear. 
    Retorna:
    - code_3ac (lista o None)
    - syntax_errors (lista)
    - semantic_errors (lista)
    """
    from analizadorLexico import lexer_php
    
    # Reiniciar estado global
    global syntax_errors, semantic_errors, symbol_table, temp_count, label_count
    syntax_errors = []
    semantic_errors = []
    symbol_table = set()
    temp_count = 0
    label_count = 0
    
    ast = parser.parse(code, lexer=lexer_php.lexer)
    
    if syntax_errors or semantic_errors:
        return None, syntax_errors, semantic_errors
        
    code_3ac = []
    if ast:
        for stmt in ast:
            code_3ac += gen_code_statement(stmt)
            
    return code_3ac, [], []
