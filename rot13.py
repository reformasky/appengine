import cgi

def rot13(s):
    a = ord('a')
    A = ord('A')
    result = ''
    for ss in s:
        if (ss >='a' and ss<='z'):
            result += chr( (ord(ss)+ 13 - a )%26 + a)
        elif (ss>='A' and ss<='Z'):
            result += chr( (ord(ss)+ 13 - A )%26 + A)
        else:
            result += ss
    return cgi.escape(result, quote = True) 
