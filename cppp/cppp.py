"""
Main CPPP class source: cppp.py

Author:     Gil Treibush
Version:    1.0.0-alpha.1
License:    MIT License
"""


def read_input_file(file_name):
    """
    Read a C/C++ source file character by character.

        Parameters:
            file_name: main source file.

        Return values:
            Tuple: Next character, Line number, Character position
    """

    try:
        with open(file_name, 'r', encoding='utf-8', errors='replace') as file:
            line_num = 0
            for line in file:
                line_num += 1
                for char_position, char in enumerate(line, start=1):
                    if char == '\uFFFD':  # Skip non-utf-8 characters
                        continue
                    if char == '\r' or char == '\f':
                        char = '\n'
                    yield char, line_num, char_position

    except Exception as e:
        # TODO: handle error
        raise


class Cppp:
    """
    This class represents a single translation unit, derived from a C/C++ source file.

    Methods:
        TBD
    """

    _predefined_values = {}
    _sys_path = []

    def __init__(self, file_name, predefined_values=None, trigraphs_enabled=False,
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

        self.file_name = file_name
        self.trigraphs_enabled = trigraphs_enabled
        self.follow_included = follow_included

        if predefined_values:
            if not isinstance(predefined_values, dict):
                raise TypeError("Predefined-Macros dictionary is not in the form of a dictionary.")
            else:
                self._predefined_values = predefined_values.copy()

        if sys_path:
            if not isinstance(sys_path, list):
                raise TypeError("System path list is not in the form of a list.")
            else:
                self._sys_path = sys_path.copy()

    def do_translation_phase_1(self):
        """
        Perform the first translation phase:
            Physical source file characters are mapped to the source character set.
            New-line characters are replaced with end-of-line indicators.
            Trigraph sequences, if enabled, are replaced by corresponding single-character internal representations.
            - From the ISO standard document.
            Also, truncate white-space characters, since handling white-spaces is implementation-dependent.
        """

        trigraph_subs = {'=': '#', '/': '\\', '\'': '^',
                         '(': '[', ')': ']', '!': '|',
                         '<': '{', '>': '}', '-': '~'}

        qbuf = []
        in_string = False
        escape_char = False

        # Add character to temp buffer
        for char, line_num, char_num in read_input_file(self.file_name):
            if in_string:
                if char == '\\' and not escape_char:
                    escape_char = True
                if char == '\"' and not escape_char:
                    in_string = False

                escape_char = False

            elif char == '\"':
                in_string = True

            else:
                # Process buffer - last character
                if char == '\n':
                    if len(qbuf) > 0 and qbuf[-1][0] == '\n':
                        continue
                elif char.isspace():
                    if len(qbuf) > 0 and qbuf[-1][0].isspace():
                        continue
                    else:
                        char = ' '

            if self.trigraphs_enabled and len(qbuf) > 1:
                if qbuf[-2][0] == '?' and qbuf[-1][0] == '?' and char in trigraph_subs.keys():
                    qbuf.pop()
                    qbuf[-1][0] = trigraph_subs[char]

                    if in_string and not escape_char:
                        if char == '/':
                            escape_char = True

                    continue

            qbuf.append([char, (line_num, char_num)])

            ### Debug Prints ###
            while len(qbuf) > 3:
                pchar = qbuf.pop(0)
                print(f"{pchar[0]}", end='')

        ### Debug Prints ###
        while len(qbuf) > 0:
            pchar = qbuf.pop(0)
            print(f"{pchar[0]}", end='')
