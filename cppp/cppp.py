"""
Main CPPP class source: cppp.py

Author:     Gil Treibush
Version:    1.0.0-alpha.1
License:    MIT License
"""

import asyncio
from collections import defaultdict


class Cppp:
    """
    This class represents a single translation unit, derived from a C/C++ source file.

    Methods:
        TBD
    """

    _predefined_values = defaultdict(lambda: "")
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

        self.main_file_name = main_file_name
        self.trigraphs_enabled = trigraphs_enabled
        self.follow_included = follow_included

        if predefined_values:
            if not isinstance(predefined_values, dict):
                raise TypeError("Predefined-Macros dictionary is not in the form of a dictionary.")
            else:
                self._predefined_values.update(predefined_values)

        if sys_path:
            if not isinstance(sys_path, list):
                raise TypeError("System path list is not in the form of a list.")
            else:
                self._sys_path = sys_path.copy()

    def read_input_file(self, file_name):
        """
        Read a C/C++ source file character by character.

            Parameters:
                file_name: main source file.

            Return values:
                Tuple: Next character, Line number, Character position
        """

        self._file_errs[file_name] = 0

        try:
            with open(file_name, 'r', encoding='utf-8', errors='replace') as file:
                line_num = 0

                for line in file:
                    line_num += 1

                    for char_position, char in enumerate(line, start=1):
                        if char == '\uFFFD':  # Skip non-utf-8 characters
                            self._file_errs[file_name] += 1
                            continue

                        if char == '\r' or char == '\f':
                            char = '\n'

                        yield char, line_num, char_position

        except Exception as e:
            # TODO: handle error
            raise

    async def do_translation_phase_1(self, file_name, out_queue):
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
        for char, line_num, char_num in self.read_input_file(file_name):
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
                    if len(qbuf) > 0 and qbuf[-1][0].isspace() and qbuf[-1][0] != '\n':
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

            while len(qbuf) > 3:
                await out_queue.put(qbuf.pop(0))

        while len(qbuf) > 0:
            await out_queue.put(qbuf.pop(0))

        await out_queue.put(None)

    async def do_translation_phase_2(self, in_queue, out_queue):
        """
        Perform the second translation phase:
            Each instance of a new-line character and an immediately preceding backslash character
            is deleted. splicing physical source lines to form logical source lines.
            - From the ISO standard document.
            File also supposed to end with a new-line character, but this is not checked.
        """

        escape_char = False

        while True:
            char = await in_queue.get()
            if not char:
                break

            if char[0] == '\n' and escape_char:
                escape_char = False
                continue

            elif char[0]  == '\\' and not escape_char:
                escape_char = True
                continue

            else:
                escape_char = False

            await out_queue.put(char)

        await out_queue.put(None)

    async def do_translation_phase_3_remove_comments(self, in_queue, out_queue):
        """
        Perform the third translation phase - remove comments:
            The source tile is decomposed into preprocessing tokens and sequences of
            white-space characters (including comments). Each comment is replaced by one space character.
            - From the ISO standard document.
        """

        in_comment_c_style = False
        in_comment_cpp_style = False
        char_asterisk = False
        char_slash = None

        while True:
            char = await in_queue.get()
            if not char:
                break

            if in_comment_c_style:
                if char[0] == '\n':
                    in_comment_c_style = False
                    continue
                else:
                    continue

            if in_comment_cpp_style:
                if char_asterisk and char[0] == '/':
                    in_comment_cpp_style = False
                    continue
                elif char[0] == '*':
                    char_asterisk = True
                else:
                    char_asterisk = False

            if char[0] == '/':
                if char_slash:
                    in_comment_c_style = True
                    char_slash = None
                    continue
                else:
                    char_slash = char
                    continue

            if char[0] == '*' and char_slash:
                in_comment_cpp_style = True
                char_slash = None

            if char_slash:
                await out_queue.put(char_slash)
                char_slash = None

            await out_queue.put(char)

        await out_queue.put(None)

    async def do_translation_phase_3(self, in_queue, out_queue):
        """
        Perform the third translation phase:
            The source tile is decomposed into preprocessing tokens and sequences of white-space characters.
            - From the ISO standard document.
        """

        symbols = ('+', '-', '*', '/', '%', '=', '<', '>', '!',
                   '=', '&', '|', '^', '~', '.', ':', ';', ',',
                   '[', ']', '(', ')', '{', '}', '?', '#', '\n')

        token_buf = []
        token_cur = None
        push_to_queue = False

        while True:
            char = await in_queue.get()
            if not char:
                break

            if char[0] == ' ':
                push_to_queue = True
                token_cur = None
            elif char[0] in symbols:
                push_to_queue = True
                token_cur = char
            else:
                push_to_queue = False
                if len(token_buf) == 0:
                    token_buf.append(char[1])
                    token_buf.append(char[0])
                else:
                    token_buf[1] = token_buf[1] + char[0]

            if push_to_queue and len(token_buf) > 0:
                await out_queue.put(token_buf.copy())
                token_buf.clear()
            if token_cur:
                await out_queue.put([token_cur[1], token_cur[0]])
                token_cur = None

        if len(token_buf) > 0:
            await out_queue.put(token_buf.copy())
        if token_cur:
            await out_queue.put([token_cur[1], token_cur[0]])

        await out_queue.put(None)

    async def do_translation_phase_4(self, in_queue, out_queue = None):
        while True:
            char = await in_queue.get()
            if not char:
                break

            ### Debug Prints ###
            print(f"{char[0]} - {char[1:]} ", end=' , ')

    async def do_parse_tu(self):
        queue_phase_1 = asyncio.Queue(5)
        queue_phase_2 = asyncio.Queue(5)
        queue_phase_3 = asyncio.Queue(5)
        queue_phase_4 = asyncio.Queue(5)

        phase_1_task = asyncio.create_task(self.do_translation_phase_1(self.main_file_name, queue_phase_1))
        phase_2_task = asyncio.create_task(self.do_translation_phase_2(queue_phase_1, queue_phase_2))
        phase_3_task_cr = asyncio.create_task(self.do_translation_phase_3_remove_comments(queue_phase_2, queue_phase_3))
        phase_3_task = asyncio.create_task(self.do_translation_phase_3(queue_phase_3, queue_phase_4))
        phase_4_task = asyncio.create_task(self.do_translation_phase_4(queue_phase_4))

        await asyncio.gather(phase_1_task, phase_2_task, phase_3_task_cr, phase_3_task, phase_4_task)

    def parse_tu(self):
        asyncio.run(self.do_parse_tu())
