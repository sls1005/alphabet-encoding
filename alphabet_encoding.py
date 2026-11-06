# The encoding of this source code file is ASCII.
# Python 3 is recommended for interpreting this; older interpreters are not supported as they use different syntax for unicode strings.
from enum import IntEnum, unique

@unique
class EncoderMode(IntEnum):
    EVERYTHING =               0
    ALPHANUMERIC =             1
    ASCII =                    2
    ASCII_PRINTABLE =          3
    ASCII_UPPER_ALPHABETIC =   4
    ASCII_LOWER_ALPHABETIC =   5
    ASCII_UPPER_ALPHANUMERIC = 6
    ASCII_LOWER_ALPHANUMERIC = 7

def xv(c, prefix='XV', suffix='X'): # str[1], str, str -> str; input length must be one.
    #assert len(c) == 1
    result = ''
    A = ord('A')
    k = ord(c)
    while True:
        offset = k % 24
        code = 'Z' if offset == 0 else chr(A + offset - 1)
        result = code + result
        k //= 24
        if k == 0:
            break
    return prefix + result + suffix

def encode(s, mode=EncoderMode.ALPHANUMERIC, newline=''): # str, EncoderMode, str -> str; if you don't want to encode newline characters using the special code XL, pass empty string or False as 3rd arg (now default); if you want to encode newline characters with XL, pass None as 3rd arg.
    result = ''
    alphabetic_mode = (
        mode in (EncoderMode.ASCII_UPPER_ALPHABETIC, EncoderMode.ASCII_LOWER_ALPHABETIC)
    )
    upper_mode = (
        mode in (EncoderMode.ASCII_UPPER_ALPHABETIC, EncoderMode.ASCII_UPPER_ALPHANUMERIC)
    )
    lower_mode = (
        mode in (EncoderMode.ASCII_LOWER_ALPHABETIC, EncoderMode.ASCII_LOWER_ALPHANUMERIC)
    )
    not_first_line = False
    in_xv_block = False
    lines = []
    if newline is None:
        lines = s.splitlines()
    elif (newline == '') or (not newline):
        lines = [s]
    else:
        lines = s.split(newline)
    for line in lines:
        if not_first_line:
            result += 'xl' if lower_mode else 'XL'
        for c in line:
            encoded = None
            no_change = False
            xv_used = False
            if c == 'X':
                encoded = 'XX'
            elif c == 'x':
                encoded = 'xy'
            elif c.isascii():
                if mode == EncoderMode.ASCII:
                    encoded = c
                    no_change = True
                elif c.isprintable():
                    if mode == EncoderMode.ASCII_PRINTABLE:
                        encoded = c
                        no_change = True
                    elif c.isalpha():
                        if mode == EncoderMode.ALPHANUMERIC:
                            encoded = c
                            no_change = True
                        elif c.isupper():
                            if mode in (EncoderMode.ASCII_UPPER_ALPHABETIC, EncoderMode.ASCII_UPPER_ALPHANUMERIC):
                                encoded = c
                                no_change = True
                            else: # c is upper but mode is not upper, alpha, alphanumeric, ascii, ascii_printable
                                pass # should encode. See below.
                        elif c.islower():
                            if mode in (EncoderMode.ASCII_LOWER_ALPHABETIC, EncoderMode.ASCII_LOWER_ALPHANUMERIC):
                                encoded = c
                                no_change = True
                            else:
                                pass # should encode. See below.
                        # else: impossible
                    elif c.isdecimal():
                        if mode in (EncoderMode.ALPHANUMERIC, EncoderMode.ASCII_UPPER_ALPHANUMERIC, EncoderMode.ASCII_LOWER_ALPHANUMERIC):
                            encoded = c
                            no_change = True
                    else: # c printable but not alphanumeric, and mode isn't ascii or ascii_printable
                        pass # should encode. See below.
                else: # c is in ascii but not printable, and mode isn't ascii
                    pass # should encode. See below.
                # c is in ascii, mode is not ascii
                # encode here
                if no_change:
                    pass
                elif alphabetic_mode or in_xv_block:
                    encoded = xv(c, prefix = 'Y' if in_xv_block else 'XV', suffix = '')
                    xv_used = True
                else:
                    encoded = 'X%02X' % ord(c)
            #elif alphabetic_mode: # c not ascii
            else:
                encoded = xv(c, prefix = 'Y' if in_xv_block else 'XV', suffix = '')
                xv_used = True
            if xv_used:
                if not in_xv_block:
                    in_xv_block = True
            elif in_xv_block:
                result += 'X'
                in_xv_block = False
            if no_change:
                result += encoded
            elif lower_mode:
                result += encoded.lower()
            elif c == 'x':
                if upper_mode or (mode < 1) or (mode > 7):
                    result += encoded.upper() 
                else:
                    result += encoded
            else:
                result += encoded.upper()
        # end for (inner)
        not_first_line = True
    # end for
    if in_xv_block:
        result += 'x' if lower_mode else 'X'
    return result

def decode(es): # str -> str
    from os import linesep
    from string import hexdigits
    result = ''
    A = ord('A')
    hex_digit_set = set(hexdigits)
    buf = ''
    rg = 0
    index_in_block = 0
    state = 0
    # Possible states:
    # 0: default
    # 1: X encountered; in escape sequence
    # 2: In XU block
    # 3: In XV block
    # 4: In X-followed-by-two-hexadecimal-digits block
    for c in es:
        char_is_ascii_alphabetic = c.isascii() and c.isalpha()
        char_upper = c.upper() if char_is_ascii_alphabetic else c
        char_is_x = (char_upper == 'X')
        if state > 1 and state < 5: # i.e., state in 2, 3, 4
            state_is_2 = (state == 2)
            state_is_3 = (state == 3)
            state_is_4 = (state == 4)
            state_is_2_or_3_and_char_is_x = (state_is_2 or state_is_3) and char_is_x # block ends normally
            state_is_3_and_char_is_y = state_is_3 and (char_upper == 'Y')
            if state_is_2_or_3_and_char_is_x or (
                (state_is_2 or (state_is_4 and index_in_block <= 2)) and (char_upper not in hex_digit_set)
            ) or state_is_3_and_char_is_y or (
                state_is_3 and (not char_is_ascii_alphabetic)
            ) or (
                state_is_2 and ((0x10FFFF - int(char_upper, 16)) >> 4) < rg
            ) or (
                state_is_3 and ((0x10FFFF - (0 if char_upper == 'Z' else ord(char_upper) - A)) / 24 < rg)
            ) or (
                state_is_4 and (index_in_block == 2)
            ): # if there is a block before invalid char, it should end first
                if index_in_block > 0:
                    result += chr(rg)
                rg = 0
                index_in_block = 0
                state = 3 if state_is_3_and_char_is_y else 0
                if state_is_2_or_3_and_char_is_x or state_is_3_and_char_is_y:
                    continue
        if state == 0:
            if char_is_x:
                buf = c
                state = 1
            else:
                result += c
        elif state == 1:
            if char_is_x:
                result += 'X'
                state = 0
            elif char_upper == 'Y':
                result += 'x'
                state = 0
            elif char_upper == 'L':
                result += linesep
                state = 0
            elif char_upper == 'U':
                state = 2
            elif char_upper == 'V':
                state = 3
            elif char_upper in hex_digit_set:
                state = 4
                rg = int(char_upper, 16)
                index_in_block = 1
            else:
                result += buf + c
                buf = ''
                state = 0
        elif state == 2 or state == 4:
            rg = (rg << 4) + int(char_upper, 16) # () enclosing << are needed or you will encounter strange bugs; 'tis a bug fix
            index_in_block += 1
        elif state == 3:
            #assert char_upper != 'X' and char_upper != 'Y'
            rg *= 24
            if char_upper != 'Z':
                rg += ord(char_upper) - A + 1
            index_in_block += 1
        #else: impossible; state 4 already handled; see above.
    if state == 1 and buf != '':
        result += buf 
    elif (state > 1 and state < 5) and (index_in_block > 0):
        result += chr(rg)
    return result
