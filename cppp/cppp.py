"""
Main CPPP class source: cppp.py

Author:     Gil Treibush
Version:    1.0.0-alpha.1
License:    MIT License
"""

import asyncio
from collections import defaultdict, OrderedDict
# Local imports
from .ltoken import LexerToken
from .cmacro import CMacro
from .directives import *
from .cparser import *


class Cppp:
    """
    This class represents a single translation unit, derived from a C/C++ source file.

    Methods:
        TBD
    """

    _lexer_lst = []
    _macros_dict = {}

    _sys_path = []
    _file_errs = {}

    def __init__(self, main_file_name, predefined_values=None, trigraphs_enabled=False,
                 follow_included=False, sys_path=None):
        """
        Class constructor.

        Parameters:
            file_name: main source file.
            predefined_values: a dictionary of predefined macros.
            trigraphs_enabled: flag - enable trigraph expansion.
            follow_included: flag - include and process included files.
            sys_path: path list to included files directories.
        """

        self._main_file_name = main_file_name
        self._trigraphs_enabled = trigraphs_enabled
        self._follow_included = follow_included

        if sys_path:
            if not isinstance(sys_path, list):
                raise TypeError("System path list is not in the form of a list.")
            else:
                self._sys_path = sys_path.copy()

        # Handle macros passed from the command line
        if predefined_values:
            if not isinstance(predefined_values, dict):
                raise TypeError("Predefined-Macros dictionary is not in the form of a dictionary.")

            else:
                for key, val in predefined_values.items():
                    macro_lst = asyncio.run(do_tokenize_from_string(str(val)))
                    if key in self._macros_dict.keys():
                        # TODO: handle redefinition error
                        pass
                    self._macros_dict[key] = CMacro(key, macro_lst, (-1, -1))

    def pretty_print(self):
        for token in self._lexer_lst:
            if token.val == '\n':
                print()
            elif token.val == ' ':
                print(" ._.", end = "")
            else:
                print(f" ${token.val}", end = "")

    def do_tokenize(self):
        self._lexer_lst = asyncio.run(do_tokenize_from_file(self._main_file_name))
        directives_do_process(self._lexer_lst, self._macros_dict)
        self.pretty_print()
