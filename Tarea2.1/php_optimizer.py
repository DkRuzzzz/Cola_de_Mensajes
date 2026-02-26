def eliminar_codigo_muerto(code_lines):
    used_vars = set()
    optimized = []

    for line in reversed(code_lines):
        tokens = line.split()
        if len(tokens) >= 3 and tokens[1] == '=':
            var = tokens[0]
            if var in used_vars or var.startswith('$') or 'print' in line or 'return' in line:
                optimized.insert(0, line)
                used_vars.update(tokens[2:])
        else:
            optimized.insert(0, line)
            used_vars.update(tokens)

    return optimized

def eliminar_subexpresiones_comunes(code_lines):
    expr_map = {}
    temp_map = {}
    optimized = []

    for line in code_lines:
        tokens = line.strip().split()
        if len(tokens) == 5 and tokens[1] == '=' and tokens[3] in ['+', '-', '*', '/']:
            expr = (tokens[3], tokens[2], tokens[4])
            if expr in expr_map:
                prev_temp = expr_map[expr]
                temp_map[tokens[0]] = prev_temp
            else:
                expr_map[expr] = tokens[0]
                optimized.append(line)
        else:
            for old, new in temp_map.items():
                if old in line:
                    line = line.replace(old, new)
            optimized.append(line)

    return optimized

def sustituir_operaciones_costosas(code_lines):
    optimized = []
    for line in code_lines:
        tokens = line.strip().split()
        if len(tokens) == 5 and tokens[1] == '=':
            dest, eq, left, op, right = tokens
            if op == '*' and right == '2':
                optimized.append(f"{dest} = {left} + {left}")
                continue
            elif op == '*' and right == '0':
                optimized.append(f"{dest} = 0")
                continue
            elif op == '+' and right == '0':
                optimized.append(f"{dest} = {left}")
                continue
            elif op == '+' and left == '0':
                optimized.append(f"{dest} = {right}")
                continue
        optimized.append(line)
    return optimized

def optimizar_codigo(code_lines):
    code = eliminar_codigo_muerto(code_lines)
    code = eliminar_subexpresiones_comunes(code)
    code = sustituir_operaciones_costosas(code)
    return code

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Uso: python php_optimizer.py <archivo_3ac.txt>")
        sys.exit(1)

    file_path = sys.argv[1]
    with open(file_path, 'r') as f:
        code_lines = [line.strip() for line in f if line.strip()]
    
    print("=== Código original ===")
    for l in code_lines:
        print(l)
    print("=======================")

    optimized = optimizar_codigo(code_lines)

    print("=== Código optimizado ===")
    for l in optimized:
        print(l)
    print("=========================")
