import sys, argparse

# TODO Handle newlines in powershell

def parse_args():
    parser = argparse.ArgumentParser(
        prog='pygrep',
        description='A simplified Python implementation of grep'
    )

    parser.add_argument(
        '-E', '--Expression',
        required=True,
        type=str,
        help="The expression string to evaluate"
    )
    
    parser.add_argument(
        "src_file", 
        nargs="?",
        type=str,
        help="File to perform the search on (optional)"
    )

    return parser.parse_args()


def search_file(filename, pattern):
    try:
        with open(filename, 'r') as file:
            found = False
            for line in file:
                line = line.strip()
                if match(line, pattern):
                    print(line)
                    found = True
    except FileNotFoundError:
            print(f"Error: The file '{file}' was not found.")
            return False
    
    if found:
        return True
    else:
        return False
        

def search_stdin(input_line, pattern):
    if match(input_line, pattern):
        print(input_line)
        return True
    else:
        return False

def match(input_line: str, pattern: list) -> bool:
    anchor_start, anchor_end = False, False

    if pattern[0][1] == "^":
        anchor_start = True
        pattern = pattern[1:]
    if pattern[-1][1] == "$":
        anchor_end = True
        pattern = pattern[:-1]

    if anchor_start:
        success, complete = match_pattern(input_line, pattern)
        if success:
            if anchor_end:
                return success and complete
            else:
                return success
    else: 
        for index in range(len(input_line)):
            substring = input_line[index:]
            success, complete = match_pattern(substring, pattern)
            if success:
                if anchor_end:
                    return success and complete
                else:
                    return success
        return False

def compile_pattern(pattern: str) -> list:
    compiled_pattern = []
    while pattern:
        match pattern[0]:
            case "^":
                compiled_pattern.append(("ANCHOR", "^", None))
                pattern = pattern[1:]
            case "$":
                compiled_pattern.append(("ANCHOR", "$", None))
                pattern = pattern[1:]
            case "[":
                if "]" not in pattern:
                    raise RuntimeError("Unclosed character group")
                compiled_pattern.append(("GROUP", pattern[:pattern.index("]")+1], None))
                pattern = pattern[pattern.index("]")+1:]
            case "(":
                if ")" not in pattern:
                    raise RuntimeError("Unclosed alternation")
                compiled_pattern.append(("ALT", pattern[1:pattern.index(")")], None))
                pattern = pattern[pattern.index(")")+1:]
            case "\\":
                compiled_pattern.append(("CLASS", "\\" + pattern[1], None))
                pattern = pattern[2:]
            case ".":
                compiled_pattern.append(("CLASS", ".", None))
                pattern = pattern[1:]
            case "+":
                if not compiled_pattern:
                    raise RuntimeError("Nothing to repeat for '+'")
                if compiled_pattern[0][2]:
                    raise RuntimeError("Double quantifier in pattern")
                # Expand "+" quantifier into a literal token with no quantifier + a literal token with a "*" quantifier for the same symbol
                old = compiled_pattern.pop()
                compiled_pattern.append((old[0], old[1], None))
                compiled_pattern.append((old[0], old[1], "*"))
                pattern = pattern[1:]
            case "*":
                if not compiled_pattern:
                    raise RuntimeError("Nothing to optionally repeat for '*'")
                if compiled_pattern[0][2]:
                    raise RuntimeError("Double quantifier in pattern")
                old = compiled_pattern.pop()
                compiled_pattern.append((old[0], old[1], "*"))
                pattern = pattern[1:]
            case "?":
                if not compiled_pattern:
                    raise RuntimeError("Nothing to optionally match for '?'")
                if compiled_pattern[0][2]:
                    raise RuntimeError("Double quantifier in pattern")
                old = compiled_pattern.pop()
                compiled_pattern.append((old[0], old[1], "?"))
                pattern = pattern[1:]
            case _:
                compiled_pattern.append(("LITERAL", pattern[0], None))
                pattern = pattern[1:]
    return compiled_pattern

def alternation_match(input_line: str, patterns: list):
    for pattern in patterns:
        if match(input_line, pattern):
            return True, len(pattern)
    return False, 0

def single_match(input_line: str, token) -> tuple[bool, int]:
    if not input_line:
        return False, 0
    kind, value, _ = token

    if kind == "LITERAL" and input_line[0] == value:
        return True, 1
    if kind == "CLASS" and value == "\\d" and input_line[0].isdigit():
        return True, 1
    if kind == "CLASS" and value == "\\w" and input_line[0].isalnum() or input_line[0] == "_":
        return True, 1
    if kind == "CLASS" and value == "." and input_line[0]:
        return True, 1
    if kind == "GROUP":
        chars = value[1:-1]
        if chars[0] == "^":
            if input_line[0] not in chars[1:]:
                return True, 1
        else:
            if input_line[0] in chars:
                return True, 1
    return False, 0         

def match_pattern(input_line: str, pattern: list) -> tuple[bool, bool]:
    if not pattern:
        return True, input_line == ""
    
    kind, value, quant = pattern[0]

    if kind == "ALT":
        compiled_patterns = [compile_pattern(x) for x in value.split("|")]
        ok, consumed = alternation_match(input_line, compiled_patterns)
        if ok:
            return match_pattern(input_line[consumed:], pattern[1:])
        else:
            return False, False

    if quant == "?":
        ok, consumed = single_match(input_line, (kind, value, None))
        if ok: 
            return match_pattern(input_line[consumed:], pattern[1:])
        else:
            return match_pattern(input_line, pattern[1:])
        
    if quant == "*":
        ok, consumed = single_match(input_line, (kind, value, None))
        if not ok: 
            return match_pattern(input_line, pattern[1:])
        else:

            idx = consumed

            while True:
                success, complete = match_pattern(input_line[idx:], pattern[1:])
                if success:
                    return success, complete
                ok, c = single_match(input_line[idx:], (kind, value, None))
                if not ok:
                    break
                idx += c
        return False, False
    
    ok, consumed = single_match(input_line, (kind, value, None))
    if ok:
        return match_pattern(input_line[consumed:], pattern[1:])
    return False, False

def main():
    args = parse_args()

    compiled_pattern = compile_pattern(args.Expression) 
    
    if args.src_file:
        if search_file(args.src_file, compiled_pattern):
            exit(0)
        else:
            exit(1)
    else:
        if search_stdin(sys.stdin.read(), compiled_pattern):
            exit(0)
        else:
            exit(1)


if __name__ == "__main__":
    main()
