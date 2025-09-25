import sys

# import pyparsing - available if you need it!
# import lark - available if you need it!

def starting_class(pattern):
    if pattern.startswith("\\"):
        print("Character class found:", pattern[:2])
        return pattern[:2]
    elif pattern.startswith("["):
        print("Character class found:", pattern[:pattern.index("]")+1])
        if "]" not in pattern:
            raise RuntimeError("Unclosed character class")
        return pattern[:pattern.index("]")+1] 
    else:
        print("Literal character found:", pattern[0])
        return pattern[0]
    

def match(input_line, pattern):
    anchor_start, anchor_end = False, False

    if pattern.startswith("^"):
        anchor_start = True
        pattern = pattern[1:]
    if pattern.endswith("$"):
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


def match_pattern(input_line, pattern):
    if pattern == "":
        if input_line == "":
            return True, True
        else:
            return True, False
    if input_line == "":
        return False, True
    
    if pattern.startswith(r"\d"):
        if input_line[0].isdigit():
            success, complete = match_pattern(input_line[1:], pattern[2:])
            return success, complete
        return False, False
    
    elif pattern.startswith(r"\w"):
        if input_line[0].isalnum() or input_line[0] == "_":
            success, complete = match_pattern(input_line[1:], pattern[2:])
            return success, complete
        return False, False
    
    elif pattern.startswith("["):
        if "]" not in pattern:
            raise RuntimeError("Unclosed character class")
        if pattern[1] == "^":
            chars = pattern[2:pattern.index("]")]
            if input_line[0] not in chars:
                success, complete = match_pattern(input_line[1:], pattern[pattern.index("]")+1:])
                return success, complete
            return False, False
        else:
            chars = pattern[1:pattern.index("]")]
            if input_line[0] in chars:
                success, complete = match_pattern(input_line[1:], pattern[pattern.index("]")+1:])
                return success, complete
            return False, False
        
    elif pattern[0] == input_line[0]:
        success, complete = match_pattern(input_line[1:], pattern[1:])
        return success, complete
    else:
        return False, False


def main():
    pattern = sys.argv[2]
    input_line = sys.stdin.read()

    if sys.argv[1] != "-E":
        print("Expected first argument to be '-E'")
        exit(1)

    if match(input_line, pattern):
        print("True")
        exit(0)
    else:
        print("False")
        exit(1)


if __name__ == "__main__":
    main()
