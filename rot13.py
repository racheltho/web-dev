def rot13_char(char):
    num = ord(char)
    # identify chars A-M and a-m
    if num in range(65, 78) or num in range(97, 110):
        return chr(num+13)
    # identify chars N-Z and n-z
    elif num in range(78, 91) or num in range(110, 122):
        return chr(num-13)
    # otherwise, return chars as is
    else:
        return char


def rot13_text(text):
    return "".join(map(rot13_char, text))
