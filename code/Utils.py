import re


def fix(l):
    if l == '🛑':
        return '^'
    if l == '🚧':
        return '^l'
    if l == '💾':
        return '^s'
    if l == 'Ă':
        return '^v'
    if l == '!':
        return '{!}'
    if l == '―':
        return '{Tab}'
    if l == '⇒':
        return '+{End}'
    if l == '⇐':
        return '+{Home}'
    if l == '⇑':
        return '+{Up}'
    if l == 'Ä':
        return '^s'
    if l == 'Ö':
        return '!{Tab}'
    if l == 'ö':
        return '^{f5}'
    if l == 'Ș':
        return '^{Tab}'
    if l == 'Ț':
        return '^{Tab}^{Tab}'
    if l == 'Î':
        return '^{Tab}^{Tab}^{Tab}^{Tab}'
    if l == '↢':
        return '{Backspace}'
    if l == '▲':
        return '{PgUp}'
    if l == '▼':
        return '{PgDn}'
    if l == '◄':
        return '{Home}'
    if l == '►':
        return '{End}'
    if l == '↑':
        return '{Up}'
    if l == '↓':
        return '{Down}'
    if l == '←':
        return '{Left}'
    if l == '→':
        return '{Right}'
    if l == ' ':
        return '{Space}'
    if l == ';':
        return ';'
    if l == '%':
        return '%'
    if l == '#':
        return '{Raw}#'
    if l == '{':
        return '{{}'
    if l == '}':
        return '{}}'
    if l == '+':
        return '{+}'
    if l == '\n':
        return '{Enter}'
    if l == '⇩':
        return '+{Enter}'
    if l == '`':
        return '``'
    if l == '"':
        return '"'
    return l


def prefilter(code):
    p1 = re.sub(' +', ' ', code)
    p1 = re.sub('\n ', '\n', p1)
    return p1


def specialCountUntil(text,_end_line,_end_char):
    cnt = 0
    end_line = 1
    end_char = 0
    for c in text:
        if c == "\n":
            end_line += 1
            end_char = 0
            newLineStarted = False
        else:
            end_char += 1
            if c != " ":
                newLineStarted = True
        if newLineStarted == True or end_char == 0:
            cnt += 1
        if _end_char==end_char and _end_line == end_line:
            break;

    return cnt

def specialCount(text):
    cnt = 0
    end_line = 1
    end_char = 0
    for c in text:
        if c == "\n":
            end_line += 1
            end_char = 0
            newLineStarted = False
        else:
            end_char += 1
            if c != " ":
                newLineStarted = True
        if newLineStarted == True or end_char == 0:
            cnt += 1

    return cnt


def decreaseCount(text, cnt):
    end_line = 1
    end_char = 0
    for c in text:
        if c == "\n":
            end_line += 1
            end_char = 0
            newLineStarted = False
        else:
            end_char += 1
            if c != " ":
                newLineStarted = True
        if newLineStarted == True or end_char == 0:
            cnt -= 1
        if cnt == 0:
            break
    cur_line = end_line
    cur_char = end_char
    if end_char > 0:
        end_char -= 1
    return cnt, end_line, end_char, cur_char
