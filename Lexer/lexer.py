import sys
import enum


class Token:
    """
    This class contains the definition of Tokens. A token has two fields: its
    text and its kind. The "kind" of a token is a constant that identifies it
    uniquely. See the TokenType to know the possible identifiers (if you want).
    You don't need to change this class.
    """
    def __init__(self, tokenText, tokenKind):
        # The token's actual text. Used for identifiers, strings, and numbers.
        self.text = tokenText
        # The TokenType that this token is classified as.
        self.kind = tokenKind


class TokenType(enum.Enum):
    """
    These are the possible tokens. You don't need to change this class at all.
    """
    EOF = -1  # End of file
    NLN = 0   # New line
    WSP = 1   # White Space
    COM = 2   # Comment
    STR = 3   # Strings
    TRU = 4   # The constant true
    FLS = 5   # The constant false
    INT = 6   # Number (integers)
    BIN = 7   # Number (binary)
    OCT = 8   # Number (octal)
    HEX = 9   # Number (hexadecimal)
    EQL = 201
    ADD = 202
    SUB = 203
    MUL = 204
    DIV = 205
    LEQ = 206
    LTH = 207
    NEG = 208
    NOT = 209
    LPR = 210
    RPR = 211


class Lexer:
    
    def __init__(self, source):
        """
        The constructor of the lexer. It receives the string that shall be
        scanned.
        """
        self.input_str = source
        self.pos = 0
        self.length = len(source)
        pass
    
    def next_valid_token(self):
        token = self.getToken()
        if token.kind == TokenType.WSP or token.kind == TokenType.NLN:
            token = self.next_valid_token()
        return token

    def tokens(self):
        """
        This method is a token generator: it converts the string encapsulated
        into this object into a sequence of Tokens. Examples:

        >>> l = Lexer("10")
        >>> [tk.kind.name for tk in l.tokens()]
        ['INT']

        >>> l = Lexer("01")
        >>> [tk.kind.name for tk in l.tokens()]
        ['OCT']

        >>> l = Lexer("0b1")
        >>> [tk.kind.name for tk in l.tokens()]
        ['BIN']

        >>> l = Lexer("0B1")
        >>> [tk.kind.name for tk in l.tokens()]
        ['BIN']

        >>> l = Lexer("0x1")
        >>> [tk.kind.name for tk in l.tokens()]
        ['HEX']

        >>> l = Lexer("0X1")
        >>> [tk.kind.name for tk in l.tokens()]
        ['HEX']

        >>> l = Lexer("0X1 + 0xA + 0XABCDEF + 0xA0B1C2D3E4F5")
        >>> [tk.kind.name for tk in l.tokens()]
        ['HEX', 'ADD', 'HEX', 'ADD', 'HEX', 'ADD', 'HEX']

        >>> l = Lexer("0b1 + 0xA + 0B01010101 + 0xA0B1C2D3E4F5")
        >>> [tk.kind.name for tk in l.tokens()]
        ['BIN', 'ADD', 'HEX', 'ADD', 'BIN', 'ADD', 'HEX']

        >>> l = Lexer('1 * 2 - 3')
        >>> [tk.kind.name for tk in l.tokens()]
        ['INT', 'MUL', 'INT', 'SUB', 'INT']

        >>> l = Lexer('1 * 2 - 3 -- alkdjf adkjf dlkjf \\n')
        >>> [tk.kind.name for tk in l.tokens()]
        ['INT', 'MUL', 'INT', 'SUB', 'INT', 'COM']

        >>> l = Lexer('1 * 2 - 3 -- alkdjf adkjf dlkjf \\n0x23 + 012')
        >>> [tk.kind.name for tk in l.tokens()]
        ['INT', 'MUL', 'INT', 'SUB', 'INT', 'COM', 'HEX', 'ADD', 'OCT']
        """
        token = self.getToken()
        while token.kind != TokenType.EOF:
            if token.kind != TokenType.WSP and token.kind != TokenType.NLN:
                yield token
            token = self.getToken()

    def getToken(self):
        """
        Return the next token.
        """
        if self.pos >= self.length:
            return Token("", TokenType.EOF)
            
        curr_char = self.input_str[self.pos]

        if curr_char.isdigit():
            number_text = curr_char
            self.pos += 1
            if number_text == "0" and self.pos < self.length:
                next_char = self.input_str[self.pos]
                if next_char in "bB":  # BIN
                    number_text += next_char
                    self.pos += 1
                    while self.pos < self.length and self.input_str[self.pos] in "01":
                        number_text += self.input_str[self.pos]
                        self.pos += 1
                    return Token(number_text, TokenType.BIN)
                elif next_char in "xX":  # HEX
                    number_text += next_char
                    self.pos += 1
                    while self.pos < self.length and self.input_str[self.pos].lower() in "0123456789abcdef":
                        number_text += self.input_str[self.pos]
                        self.pos += 1
                    return Token(number_text, TokenType.HEX)
            while self.pos < self.length and self.input_str[self.pos].isdigit():
                number_text += self.input_str[self.pos]
                self.pos += 1
            if number_text.startswith("0") and len(number_text) > 1:
                return Token(number_text, TokenType.OCT)
            else:
                return Token(number_text, TokenType.INT)
            
        if curr_char == "-" and self.pos + 1 < self.length and self.input_str[self.pos + 1] == "-":
            comment_text = ""
            self.pos += 2  
            while self.pos < self.length and self.input_str[self.pos] != "\n":
                comment_text += self.input_str[self.pos]
                self.pos += 1
            return Token(comment_text, TokenType.COM)
        
        if curr_char == "(" and self.pos + 1 < self.length and self.input_str[self.pos + 1] == "*":
            comment_text = ""
            self.pos += 2 
            while self.pos < self.length:
                if self.input_str[self.pos] == "*" and self.pos + 1 < self.length and self.input_str[self.pos + 1] == ")":
                    self.pos += 2  
                    break
                comment_text += self.input_str[self.pos]
                self.pos += 1
            return Token(comment_text, TokenType.COM)
            
        if self.input_str[self.pos:self.pos+3] == "not" and \
             (self.pos+3 == self.length or not self.input_str[self.pos+3].isalnum()):
            self.pos += 3
            return Token("not", TokenType.NOT)
            
        if self.input_str[self.pos:self.pos+4] == "true" and \
             (self.pos+4 == self.length or not self.input_str[self.pos+4].isalnum()):
            self.pos += 4
            return Token("not", TokenType.TRU)
            
        if self.input_str[self.pos:self.pos+5] == "false" and \
             (self.pos+5 == self.length or not self.input_str[self.pos+5].isalnum()):
            self.pos += 5
            return Token("not", TokenType.FLS)
                    
                    
        if curr_char.isspace():
            self.pos += 1
            if curr_char == "\n":
                return Token(curr_char, TokenType.NLN)
            else:
                return Token(curr_char, TokenType.WSP)
        
        if curr_char == "<" and self.pos + 1 < self.length and self.input_str[self.pos + 1] == "=":
            token_text = self.input_str[self.pos:self.pos+2]
            self.pos += 2
            return Token(token_text, TokenType.LEQ)
        
        if curr_char == "=":
            self.pos += 1
            return Token(curr_char, TokenType.EQL)
        if curr_char == "+":
            self.pos += 1
            return Token(curr_char, TokenType.ADD)
        if curr_char == "-":
            self.pos += 1
            return Token(curr_char, TokenType.SUB)
        if curr_char == "*":
            self.pos += 1
            return Token(curr_char, TokenType.MUL)
        if curr_char == "/":
            self.pos += 1
            return Token(curr_char, TokenType.DIV)
        if curr_char == "<=":
            self.pos += 1
            return Token(curr_char, TokenType.LEQ)
        if curr_char == "<":
            self.pos += 1
            return Token(curr_char, TokenType.LTH)
        if curr_char == "~":
            self.pos += 1
            return Token(curr_char, TokenType.NEG)
        if curr_char == "(":
            self.pos += 1
            return Token(curr_char, TokenType.LPR)
        if curr_char == ")":
            self.pos += 1
            return Token(curr_char, TokenType.RPR)
            
            
        token = None
        return token