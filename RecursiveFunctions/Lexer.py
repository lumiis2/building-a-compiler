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
    NLN = 0  # New line
    WSP = 1  # White Space
    COM = 2  # Comment
    NUM = 3  # Number (integers)
    STR = 4  # Strings
    TRU = 5  # The constant true
    FLS = 6  # The constant false
    VAR = 7  # An identifier
    LET = 8  # The 'let' of the let expression
    INX = 9  # The 'in' of the let expression
    END = 10  # The 'end' of the let expression
    EQL = 201  # x = y
    ADD = 202  # x + y
    SUB = 203  # x - y
    MUL = 204  # x * y
    DIV = 205  # x div y
    LEQ = 206  # x <= y
    LTH = 207  # x < y
    NEG = 208  # ~x
    NOT = 209  # not x
    LPR = 210  # (
    RPR = 211  # )
    VAL = 212  # The 'val' declaration
    ORX = 213  # x or y
    AND = 214  # x and y
    IFX = 215  # The 'if' of a conditional expression
    THN = 216  # The 'then' of a conditional expression
    ELS = 217  # The 'else' of a conditional expression
    FNX = 218  # The 'fn' that declares an anonymous function
    ARW = 219  # The '=>' that separates the parameter from the body of function
    FUN = 220  # The 'fun' declaration
    MOD = 221  # The 'mod' operator


class Lexer:
    
    def __init__(self, source):
        """
        The constructor of the lexer. It receives the string that shall be
        scanned.
        """
        self.input_str = source
        self.pos = 0
        self.length = len(source)

    def next_valid_token(self):
        token = self.getToken()
        if token.kind == TokenType.WSP or token.kind == TokenType.NLN:
            token = self.next_valid_token()
        return token


    def tokens(self):
        """
        This method is a token generator: it converts the string encapsulated
        into this object into a sequence of Tokens. Notice that this method
        filters out three kinds of tokens: white-spaces, comments and new lines.

        Examples:

        >>> l = Lexer("1 + 3")
        >>> [tk.kind for tk in l.tokens()]
        [<TokenType.NUM: 3>, <TokenType.ADD: 202>, <TokenType.NUM: 3>]

        >>> l = Lexer('1 * 2\\n')
        >>> [tk.kind for tk in l.tokens()]
        [<TokenType.NUM: 3>, <TokenType.MUL: 204>, <TokenType.NUM: 3>]

        >>> l = Lexer('1 * 2 -- 3\\n')
        >>> [tk.kind for tk in l.tokens()]
        [<TokenType.NUM: 3>, <TokenType.MUL: 204>, <TokenType.NUM: 3>]

        >>> l = Lexer("1 + var")
        >>> [tk.kind for tk in l.tokens()]
        [<TokenType.NUM: 3>, <TokenType.ADD: 202>, <TokenType.VAR: 7>]

        >>> l = Lexer("let val v = 2 in v end")
        >>> [tk.kind.name for tk in l.tokens()]
        ['LET', 'VAL', 'VAR', 'EQL', 'NUM', 'INX', 'VAR', 'END']

        >>> l = Lexer("fn x => x + 1")
        >>> [tk.kind.name for tk in l.tokens()]
        ['FNX', 'VAR', 'ARW', 'VAR', 'ADD', 'NUM']

        >>> l = Lexer("fun inc a = a + 1")
        >>> [tk.kind.name for tk in l.tokens()]
        ['FUN', 'VAR', 'VAR', 'EQL', 'VAR', 'ADD', 'NUM']
        """
        token = self.getToken()
        while token.kind != TokenType.EOF:
            if token.kind != TokenType.WSP and token.kind != TokenType.COM \
                    and token.kind != TokenType.NLN:
                yield token
            token = self.getToken()

    def getToken(self):
        """
        Return the next token.
        """
        if self.pos >= self.length:
            return Token("", TokenType.EOF)

        curr_char = self.input_str[self.pos]

        # Numbers 
        if curr_char.isdigit():
            number_text = curr_char
            self.pos += 1
            while self.pos < self.length and self.input_str[self.pos].isdigit():
                number_text += self.input_str[self.pos]
                self.pos += 1
            return Token(number_text, TokenType.NUM)

        # Comments: -- ... \n
        if curr_char == "-" and self.pos + 1 < self.length and self.input_str[self.pos + 1] == "-":
            comment_text = ""
            self.pos += 2
            while self.pos < self.length and self.input_str[self.pos] != "\n":
                comment_text += self.input_str[self.pos]
                self.pos += 1
            return Token(comment_text, TokenType.COM)

        # Comments: (* ... *)
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

        # Identifiers and keywords
        if curr_char.isalpha():
            start = self.pos
            while self.pos < self.length and (self.input_str[self.pos].isalnum() or self.input_str[self.pos] == '_'):
                self.pos += 1
            word = self.input_str[start:self.pos]
            if word == "let":
                return Token(word, TokenType.LET)
            elif word == "fn":
                return Token(word, TokenType.FNX)
            elif word == "in":
                return Token(word, TokenType.INX)
            elif word == "end":
                return Token(word, TokenType.END)
            elif word == "true":
                return Token(word, TokenType.TRU)
            elif word == "false":
                return Token(word, TokenType.FLS)
            elif word == "not":
                return Token(word, TokenType.NOT)
            elif word == "or":
                return Token(word, TokenType.ORX)
            elif word == "and":
                return Token(word, TokenType.AND)
            elif word == "if":
                return Token(word, TokenType.IFX)
            elif word == "then":
                return Token(word, TokenType.THN)
            elif word == "else":
                return Token(word, TokenType.ELS)
            elif word == "div":
                return Token(word, TokenType.DIV)
            elif word == "mod":
                return Token(word, TokenType.MOD)
            elif word == "val":
                return Token(word, TokenType.VAL)
            elif word == "fun":
                return Token(word, TokenType.FUN)
            else:
                return Token(word, TokenType.VAR)

        # Assignment <-
        if self.input_str[self.pos:self.pos+2] == "<-":
            self.pos += 2
            return Token("<-", TokenType.ASN)

        # Less than or equal <=
        if self.input_str[self.pos:self.pos+2] == "<=":
            self.pos += 2
            return Token("<=", TokenType.LEQ)

        # =>
        if self.input_str[self.pos:self.pos+2] == "=>":
            self.pos += 2
            return Token("=>", TokenType.ARW)

        # Less than <
        if curr_char == "<":
            self.pos += 1
            return Token(curr_char, TokenType.LTH)

        # Operators and punctuation
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
        if curr_char == "~":
            self.pos += 1
            return Token(curr_char, TokenType.NEG)
        if curr_char == "(":
            self.pos += 1
            return Token(curr_char, TokenType.LPR)
        if curr_char == ")":
            self.pos += 1
            return Token(curr_char, TokenType.RPR)

        # Whitespace and newlines
        if curr_char.isspace():
            self.pos += 1
            if curr_char == "\n":
                return Token(curr_char, TokenType.NLN)
            else:
                return Token(curr_char, TokenType.WSP)

        # If nothing matches, return EOF
        return Token("", TokenType.EOF)