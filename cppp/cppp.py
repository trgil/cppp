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

    predefined_values = {}
    sys_path = []

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
                self.predefined_values = predefined_values.copy()

        if sys_path:
            if not isinstance(sys_path, list):
                raise TypeError("System path list is not in the form of a list.")
            else:
                self.sys_path = sys_path.copy()

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
        in_str = False

        # Add character to temp buffer
        for char, line_num, char_num in read_input_file(self.file_name):
            qbuf.append([char, (line_num, char_num)])

            # TODO: add handling of strings and quotes

            # Process buffer - last character
            if qbuf[-1][0] == '\r' or qbuf[-1][0] == '\f':
                qbuf[-1][0] = '\n'

            # Process buffer - last two characters
            if len(qbuf) > 1:
                if qbuf[-1][0] == '\n' and qbuf[-2][0] == '\n':
                    qbuf.pop()
                elif qbuf[-1][0].isspace() and qbuf[-2][0].isspace():
                    if qbuf[-1][0] == '\n':
                        qbuf.pop(-2)
                    else:
                        qbuf.pop()

                # Process buffer - last tree characters
                elif len(qbuf) > 2 and self.trigraphs_enabled:
                    if qbuf[-3][0] == '?' and qbuf[-2][0] == '?' and qbuf[-1][0] in trigraph_subs.keys():
                        qbuf[-3][0] = trigraph_subs[qbuf[-1][0]]
                        qbuf.pop()
                        qbuf.pop()

            ### Debug Prints ###
            while len(qbuf) > 3:
                pchar = qbuf.pop(0)
                print(f"{pchar[0]}", end='')

        ### Debug Prints ###
        while len(qbuf) > 0:
            pchar = qbuf.pop(0)
            print(f"{pchar[0]}", end='')
