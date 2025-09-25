import sys

# import pyparsing - available if you need it!
# import lark - available if you need it!

def starting_class(pattern):
    if pattern.startswith("\\"):
        return pattern[:2]
    elif pattern.startswith("["):
        if "]" not in pattern:
            raise RuntimeError("Unclosed character class")
        return pattern[:pattern.index("]")+1]
    else:
        return pattern[0]
    
def match(input_line, pattern):
    x = starting_class(pattern)
    for char in input_line:
        if match_pattern(char, x):
            if match_pattern(input_line[input_line.index(char):], pattern):
                return True

def match_pattern(input_line, pattern):
    if pattern == "":
        return True
    if input_line == "":
        return False
    

    if pattern.startswith(r"\d"):
        if input_line[0].isdigit():
            if match_pattern(input_line[1:], pattern[2:]):
                return True
        return False
    elif pattern.startswith(r"\w"):
        if input_line[0].isalnum() or input_line[0] == "_":
            if match_pattern(input_line[1:], pattern[2:]):
                return True
        return False
    elif pattern.startswith("["):
        if "]" not in pattern:
            raise RuntimeError("Unclosed character class")
        if pattern[1] == "^":
            chars = pattern[2:pattern.index("]")]
            if input_line[0] not in chars:
                if match_pattern(input_line[1:], pattern[pattern.index("]")+1:]):
                    return True
            return False
        else:
            chars = pattern[1:pattern.index("]")]
            if input_line[0] in chars:
                if match_pattern(input_line[1:], pattern[pattern.index("]")+1:]):
                    return True
            return False
    elif pattern[0] == input_line[0]:
        if match_pattern(input_line[1:], pattern[1:]):
            return True
    else:
        return False
  
  
  #  else:
   #     raise RuntimeError(f"Unhandled pattern: {pattern}")
    

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
