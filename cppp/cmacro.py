"""
A C macro class source: cmacro.py

Author:     Gil Treibush
Version:    1.0.0-alpha.1
License:    MIT License
"""

from .ltoken import LexerToken


class CMacro:
    """
    This class represents a single defined macro.
    """

    _params = []

    def __init__(self, name, value = None, source = None):
        self._name = name
        self._val = value if value else []
        self._source = source

    def __add__(self, other):
        if isinstance(other, CMacro):
            self._val = other._val
        elif isinstance(other, LexerToken):
            self._val.append(other)
        else:
            # Raise error
            pass

    def __eq__(self, other):
        if isinstance(other, LexerToken):
            return self._name == other.val
        elif isinstance(other, str):
            return self._name == other
        else:
            # Raise error
            pass

    def __repr__(self):
        return f"CMacro({self._name}, {self._val}, {self._source})"

    def __str__(self):
        str = f"["

        if self._source == (-1, -1):
            str = str + f"CLI]"
        else:
            str = str + f"Line: {self._source[0]}]"

        str = str + f"{self._name}"

        if self._val:
            str = str + f"->{self._val}"

        return str

    @property
    def name(self):
        return self._name

    @property
    def val(self):
        return self._val

    @property
    def params(self):
        return self._params

    def append(self, other):
        if isinstance(other, LexerToken):
            self._val.append(other)
        else:
            pass

    def substitute(self, token):
        # Do simple substitution
        pass