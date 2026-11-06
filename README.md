This project defines and implements a new encoding that could use only 26 alphabetic letters or 36 alphanumeric letters to encode all Unicode characters, using `X` to start an escaping sequence, as defined below.

```txt
In this encoding,

X shall mean the start of an escape sequence or the end of a unicode block or that of an alphabet-encoded unicode block as defined below; such a sequence shall be interpreted as Englishly case-insensitive.

XL marks the end of a line and shall start a new line whenever present;

XU shall mean the start of a unicode block, which shall be a character sequence having the form XUHHHHX, where "HHHH" shall be replaced by one or more hexadecimal digits (represented by hexadecimal numerals from 0 to F), representing a character in Unicode;

XV shall mean the start of an alphabet-encoded unicode block, which shall be something similar to a unicode block as defined above, but instead use alphabetic letters to represent the Unicode code points, following the rules below: Z shall represent zero, and letters from A to W shall represent numbers from one to twenty-three, following the alphabetical order, meaning A shall be used to encode the number one, B for two, C for three, and so on, and W shall be used to encode twenty-three, thus forming a 24-based numeral system, where the smallest digit is Z (zero), and the largest digit is W (twenty-three), and twenty-four shall be represented as AZ (one-zero), while X and Y are reserved for other purposes and shall not be used to represent numbers; X marks the end of the entire block, while Y marks the end of the current character and the start of the next character; therefore the sequence shall be in the form XVCCCCX or XVCCCCYDDDD...X, where "CCCC" shall be one or more 24-based digits mentioned above, forming a number to represent a Unicode code point, and "DDDD" shall be another 24-based number to represent another character, and "..." shall mean zero or more sequences following the form of a letter Y followed by a 24-based number to represent a Unicode point (where "Y" used in this way is invented as a shorthand for XXV to save storage), and thus, "XU41X" can also be represented as "XVBQX";

XX shall mean the capital Latin letter X;

XY shall mean the lowercase Latin letter x;

X followed by two hexadecimal digits (represented by hexadecimal numerals from 0 to F), in the form XHH, where "HH" shall be replaced by two hexadecimal digits, shall represent a character in Unicode; for example, X41 represents the Unicode character A (U+0041); 'tis Unicode, not ASCII nor extended ASCII (but if, and only if, an implementation extends this encoding for the purpose of representing a character that isn't included in Unicode, then this rule may be ignored.)

An empty unicode block or alphabet-encoded unicode block, i.e., "XUX" or "XVX", is invalid, and it is recommended that a decoder ignore it, and if an invalid character is encountered in a unicode block or alphabet-encoded unicode block or X-followed-by-two-digits format sequence, or if the value represented by a unicode block or alphabet-encoded unicode block would exceed the maximum possible Unicode code point U+10FFFF, or if the input ends before the end of a block is reached, it is recommended to interpret as if the block ended before that character or end of the input, and if doing so would result in an empty block, it is recommend that the block be ignored.

Any character sequence starting with an unescaped X (or x) but not mentioned above is reserved and shall not be used, and if encountered, the decoder encountering it shall interpret it as if it started with an escaped literal X (or x).

A part that does not contain any escape sequence, is not considered encoded, and shall be represented as-is.

Therefore, "oxygen" could be encoded as "oxyygen", "oXYygen", "ox78ygen", "oX78ygen", "oxu78xygen", "oXU78Xygen",
"oxvezxygen" or "oXVEZXygen", while "OXYGEN" could be encoded as "OXXYGEN", "OxxYGEN", "OX58YGEN", "Ox58YGEN", "OXU58XYGEN", "Oxu58xYGEN", "OXVCPXYGEN" or "OxvcpxYGEN".

Thus, anything and everything can be encoded using only 26 letters, or with only 26 letters and 10 digits.
```

The encoding is less efficient than UTF-7 or Base64, but can be used where they cannot be used, such as in a case-insensitive environment or one that doesn't allow special characters, or identifiers that must start with alphabetic characters.

Note that the source code file only contains functions, so nothing will happen if you run it. You have to add code to call these functions.