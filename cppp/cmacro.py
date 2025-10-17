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

    def __init__(self, value: list = None, params: list = None, source: tuple = None,
                 function_like: bool = False, variadic: bool = False):
        self._val = value if value else [] # By default, the value is missing
        self._params = params if params else [] # By default, there are no parameters
        self._source = source if source else (-1, -1) # Default source is the CLI
        self._function_like = function_like
        self._variadic = variadic

        # TODO: assert params and function_like/variadic come together

    def __add__(self, other):
        if isinstance(other, CMacro):
            self._val = other._val
        elif isinstance(other, LexerToken):
            self._val.append(other)
        else:
            # Raise error
            pass

    def __repr__(self):
        return f"CMacro({self._val}, {self._source})"

    def __str__(self):
        str_out = f"["

        if self._source == (-1, -1):
            str_out = str_out + f"CLI]"
        else:
            str_out = str_out + f"Line: {self._source[0]}]"

        if self._val:
            str_out = str_out + f"{self._val}"

        if self._params:
            str_out = str_out + f"{self._params}"

        if self._variadic:
            str_out = str_out + f" variadic,"

        if self._function_like:
            str_out = str_out + f" function like,"

        if self._source:
            str_out = str_out + f" {self._source}"

        return str_out

    @property
    def val(self):
        return self._val

    @property
    def params(self):
        return self._params

    @property
    def function_like(self):
        return self._function_like

    @property
    def variadic(self):
        return self._variadic

    def append(self, other):
        if isinstance(other, LexerToken):
            self._val.append(other)
        else:
            pass
