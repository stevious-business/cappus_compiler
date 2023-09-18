from . import source
from . import tokens
from cfclogger import log
from locals import *

class LexerError(TypeError): pass

class LexemeStream:
    def __init__(self, src: source.Source):
        self.lexemes = []
        self.source = src
        self.pointer = 0
        self.lexeme = tokens.Lexeme(tokens.TokenType.EOF, "", self.source)
    
    def consume_lexeme(self) -> tokens.Lexeme:
        try:
            self.lexeme = self.lexemes[self.pointer]
            self.pointer += 1
            return self.lexeme
        except IndexError:
            self.lexeme = tokens.Lexeme(tokens.TokenType.EOF, "", self.source)
            return self.lexeme
    
    def get_lexemes(self):
        """Returns current list of lexemes"""
        return self.lexemes
    
    def findall(self) -> list[tokens.Lexeme]:
        """Finds all lexemes in source"""
        while not self.source.peek() == "EOF":
            if self.find_next().tokenType == tokens.TokenType.INVALID:
                raise LexerError("Error while lexing (See above for details)!")
        return self.lexemes
    
    def find_next(self) -> tokens.Lexeme:
        char = self.source.get()
        value = char
        if char in " \n\r\t\b":
            value = ""
            while self.source.peek() in " \n\r\t\b":
                self.source.get()
            char = self.source.get()
            value = char
        # check for identifiers / keywords
        if char.isalpha() or char == "_":
            tokenType = tokens.TokenType.KEYWORD
            while self.source.peek().isalnum() or self.source.peek() == "_":
                if self.source.peek().isnumeric():
                    tokenType = tokens.TokenType.IDENTIFIER
                value += self.source.get()
            if tokenType == tokens.TokenType.KEYWORD:
                if value not in tokens.TokenList.KEYWORDS:
                    tokenType = tokens.TokenType.IDENTIFIER
                if value in tokens.TokenList.BOOLEANS:
                    tokenType = tokens.TokenType.BOOL
            lexeme = tokens.Lexeme(tokenType, value, self.source)
            self.lexemes.append(lexeme)
            return lexeme
        # literals
        elif char.isnumeric():
            tokenType = tokens.TokenType.INTEGER
            while self.source.peek().isnumeric() or self.source.peek() == ".":
                if self.source.peek() == ".":
                    if tokenType == tokens.TokenType.FLOAT:
                        # error, two dots in a number
                        self.lexemes.append(tokens.Lexeme(
                            tokens.TokenType.INVALID, value+self.source.get(),
                            self.source))
                        return tokens.Lexeme(tokens.TokenType.INVALID,
                                             value+self.source.get(),
                                             self.source)
                    tokenType = tokens.TokenType.FLOAT
                value += self.source.get()
            lexeme = tokens.Lexeme(tokenType, value, self.source)
            self.lexemes.append(lexeme)
            return lexeme
        elif char == '"':
            while True:
                if char != "\\" and self.source.peek() == '"':
                    value += self.source.get()
                    break
                char = self.source.get()
                if char != tokens.TokenType.EOF:
                    value += char
                else:
                    break
            lexeme = tokens.Lexeme(tokens.TokenType.STRING, value,
                                   self.source)
            self.lexemes.append(lexeme)
            return lexeme
        # operators and arithmetics
        elif char in tokens.TokenList.SINGLES:
            if char + self.source.peek() in tokens.TokenList.DOUBLES:
                if char + self.source.peek() + self.source.peek(2) \
                        in tokens.TokenList.TRIPLES:
                    lexeme = tokens.Lexeme(tokens.TokenType.OPERATOR,
                                           char+self.source.peek()
                                           +self.source.peek(2),
                                           self.source)
                    self.source.get()
                else:
                    lexeme = tokens.Lexeme(tokens.TokenType.OPERATOR,
                                           char+self.source.peek(),
                                           self.source)
                self.source.get()
            else:
                lexeme = tokens.Lexeme(tokens.TokenType.OPERATOR, char,
                                       self.source)
            self.lexemes.append(lexeme)
            return lexeme
        
        else:
            tokenType = tokens.from_string(char)
            if tokenType is tokens.TokenType.INVALID:
                log(LOG_FAIL,
                    "Failed to identify token: %s at %s" %
                    (char, self.source.get_pos()))
                self.lexemes.append(
                    tokens.Lexeme(tokenType, char, self.source))
                return tokens.Lexeme(tokenType, char, self.source)
            else:
                lexeme = tokens.Lexeme(tokenType, char, self.source)
                self.lexemes.append(lexeme)
                return lexeme