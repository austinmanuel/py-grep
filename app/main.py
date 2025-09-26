import sys

# import pyparsing - available if you need it!
# import lark - available if you need it!

# TODO Handle newlines in powershell

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
        if pattern[0] == "^":
            compiled_pattern.append(("ANCHOR", "^", None))
            pattern = pattern[1:]
        elif pattern[0] == "\\":
            compiled_pattern.append(("CLASS", "\\" + pattern[1], None))
            pattern = pattern[2:]
        elif pattern[0] == "[":
            if "]" not in pattern:
                raise RuntimeError("Unclosed character group")
            compiled_pattern.append(("GROUP", pattern[:pattern.index("]")+1], None))
            pattern = pattern[pattern.index("]")+1:]
        elif pattern[0] == "+":
            if not compiled_pattern:
                raise RuntimeError("Nothing to repeat for '+'")
            old = compiled_pattern.pop()
            compiled_pattern.append((old[0], old[1], "+"))
            pattern = pattern[1:]
        elif pattern[0] == "?":
            if not compiled_pattern:
                raise RuntimeError("Nothing to optionally match for '?'")
            old = compiled_pattern.pop()
            compiled_pattern.append((old[0], old[1], "?"))
            pattern = pattern[1:]
        elif pattern[0] == "$":
            compiled_pattern.append(("ANCHOR", "$", None))
            pattern = pattern[1:]
        else:
            compiled_pattern.append(("LITERAL", pattern[0], None))
            pattern = pattern[1:]
    return compiled_pattern

def single_match(input_line: str, token) -> tuple[bool, int]:
    if not input_line:
        return False, 0
    kind, value, _ = token

    if kind == "LITERAL" and input_line[0] == value:
        print("Found literal: ", value)
        return True, 1
    if kind == "CLASS" and value == "\\d" and input_line[0].isdigit():
        print("Found class match: ", value)
        return True, 1
    if kind == "CLASS" and value == "\\w" and input_line[0].isalnum() or input_line[0] == "_":
        print("Found class match: ", value)
        return True, 1
    if kind == "GROUP":
        chars = value[1:-1]
        if chars[0] == "^":
            if input_line[0] not in chars[1:]:
                print("Found neg group match: ", value)
                return True, 1
        else:
            if input_line[0] in chars:
                print("Found group match: ", value)
                return True, 1
    return False, 0         

def match_pattern(input_line: str, pattern: list) -> tuple[bool, bool]:
    if not pattern:
        return True, input_line == ""
    if input_line == "":
        return False, True
    
    kind, value, quant = pattern[0]

    if quant == "?":
        ok, consumed = single_match(input_line, (kind, value, None))
        if ok: 
            return match_pattern(input_line[consumed:], pattern[1:])
        else:
            return match_pattern(input_line, pattern[1:])
   
    if quant == "+":
        ok, consumed = single_match(input_line, (kind, value, None))
        if not ok:
            return False, False    

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
    pattern = sys.argv[2]
    input_line = sys.stdin.read()

    if sys.argv[1] != "-E":
        print("Expected first argument to be '-E'")
        exit(1)

    compiled_pattern = compile_pattern(pattern) 
    print(compiled_pattern)

    if match(input_line, compiled_pattern):
        print("True")
        exit(0)
    else:
        print("False")
        exit(1)


if __name__ == "__main__":
    main()
