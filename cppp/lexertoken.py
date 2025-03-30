"""
A Lexer Token class source: lexertoken.py

Author:     Gil Treibush
Version:    1.0.0-alpha.1
License:    MIT License
"""


class LexerToken:
    """
    This class represents a single Lexer Token.
    """

    _val = ""

    def __init__(self, start, val = None, identifier_compatible = None):
        self._start = start

        if val:
            self._val = self._val + val

        self._identifier_compatible = identifier_compatible

    def __repr__(self):
        return f"LexerToken({self._start}, {self._val}, {self._identifier_compatible})"

    def __str__(self):
        return f"{self._start[0]},{self._start[1]}:{self._val}[{self._identifier_compatible}]"

    def __add__(self, other):
        if isinstance(other, LexerToken):
            self._val = self._val + other._val
        elif isinstance(other, str):
            self._val = self._val + other
        else:
            raise TypeError("Token added to non-supported type")

    def __len__(self):
        return len(self._val)

    def __eq__(self, other):
        if isinstance(other, LexerToken):
            return self._val == other._val
        elif isinstance(other, str):
            return self._val == other
        else:
            raise TypeError("Token compared to non-supported type")

    @property
    def val(self):
        return self._val

    @property
    def identifier_compatible(self):
        return self._identifier_compatible

    @identifier_compatible.setter
    def identifier_compatible(self, value):
        self._identifier_compatible = bool(value)