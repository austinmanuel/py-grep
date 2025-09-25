import sys

# import pyparsing - available if you need it!
# import lark - available if you need it!

def match_pattern(input_line, pattern):
    if pattern == None:
        return True
    if input_line == None:
        return False
    

    if pattern.startwith(r"\d"):
        if input_line[0].isdigit():
            match_pattern(input_line[1:], pattern[2:])
        return False
    elif pattern.startswith(r"\w"):
        if input_line[0].isalnum() or input_line[0] == "_":
            match_pattern(input_line[1:], pattern[2:])
        return False
    elif pattern.startswith("["):
        if "]" not in pattern:
            raise RuntimeError("Unclosed character class")
        if pattern[1] == "^":
            chars = pattern[2:pattern.index("]")]
            if input_line[0] not in chars:
                match_pattern(input_line[1:], pattern[pattern.index("]"):])
            return False
        else:
            chars = pattern[1:pattern.index("]")]
            if input_line[0] in chars:
                match_pattern(input_line[1:], pattern[pattern.index("]"):])
            return False
    elif pattern[0] == input_line[0]:
        return match_pattern(input_line[1:], pattern[1:])
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

    if match_pattern(input_line, pattern, 1):
        exit(0)
    else:
        exit(1)


if __name__ == "__main__":
    main()
