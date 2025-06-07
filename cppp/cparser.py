"""
A source parser source: cparser.py

Author:     Gil Treibush
Version:    1.0.0-alpha.1
License:    MIT License
"""

import asyncio
from typing import Callable

from .ltoken import LexerToken
from .directives import is_identifier_compatible


def input_txt_from_file(file_name: str):
    """
    Read a C/C++ source file character by character, and perform some of the first translation phase steps.
        Physical source file characters are mapped to the source character set.
        New-line characters are replaced with end-of-line indicators.
        - From the ISO standard document.
    :param file_name: input source file.
    :return: number of encoding errors found in the file.
    """

    _file_errs = 0

    try:
        with open(file_name, 'r', encoding='utf-8', errors='replace') as file:
            line_num = 1
            line_add = 0
            char_position = 1

            for text_line in file:
                for char in text_line:
                    if char == '\uFFFD':  # Skip non-utf-8 characters
                        _file_errs += 1
                        continue

                    char_position += 1

                    if line_add:
                        line_num += 1
                        char_position = 1

                    if char == '\r' or char == '\f':
                        char = '\n'

                    line_add = True if char == '\n' else False

                    yield char, line_num, char_position

        return _file_errs
        # TODO: read and propagate _file_errs in __main__

    except Exception as e:
        # TODO: handle error
        raise


def input_txt_from_string(text: str):
    """
    Read some C/C++ code from string character by character, and perform some of the first translation
    phase steps.
        Physical source file characters are mapped to the source character set.
        New-line characters are replaced with end-of-line indicators.
        - From the ISO standard document.
    :param text: input source string.
    :return: number of encoding errors found in the file.
    """

    _file_errs = 0
    line_num = 1
    char_position = 1
    line_add = False

    corrected_text = (
        text.replace('\r\n', '\n').replace('\r', '\n').replace('\f', '\n'))

    for char in corrected_text:
        if char == '\uFFFD':  # Skip non-utf-8 characters
            _file_errs += 1
            continue

        char_position += 1

        if line_add:
            line_num += 1
            char_position = 1

        line_add = True if char == '\n' else False

        yield char, line_num, char_position

    return _file_errs


async def cat_output_text(in_queue, out_text: list):
    while True:
        out_m = await in_queue.get()
        if not out_m:
            break

        if isinstance(out_m, LexerToken):
            txt = out_m.val
        else:
            txt, (_, _) = out_m

        out_text.append(txt)


async def do_translation_phase_1(input_func: Callable, input_src: str, out_queue, trigraphs_enabled: bool = False):
    """
    Perform the first translation phase:
        Physical source file characters are mapped to the source character set.
        Trigraph sequences, if enabled, are replaced by corresponding single-character internal representations.
        - From the ISO standard document.
        Also, truncate white-space characters, since handling white-spaces is implementation-dependent.
    """

    trigraph_subs = {'=': '#', '/': '\\', '\'': '^',
                        '(': '[', ')': ']', '!': '|',
                        '<': '{', '>': '}', '-': '~'}

    char_buf = []
    escape_char = False
    in_string = False
    in_comment_c_style = False
    in_comment_cpp_style = False

    for char, line_num, char_num in input_func(input_src):

        # Push new chars into the buffer
        if in_string:
            # In a string - white spaces are preserved.
            if not escape_char and char == '\"':
                in_string = False
            elif not escape_char and char == '\\':
                escape_char = True
            else:
                escape_char = False

        elif in_comment_cpp_style:
            # In a comment - white spaces are preserved.
            if not escape_char and char == '\n':
                in_comment_cpp_style = False
            elif not escape_char and char == '\\':
                escape_char = True
            else:
                escape_char = False

        elif in_comment_c_style:
            # In a comment - white spaces are preserved.
            if char == '/' and len(char_buf) > 0 and char_buf[-1][0] == '*':
                in_comment_c_style = False

        elif char == '\"':
            # Start a string
            in_string = True

        elif char == '/':
            if len(char_buf) > 0 and char_buf[-1][0] == '/':
                in_comment_cpp_style = True

        elif char == '*':
            if len(char_buf) > 0 and char_buf[-1][0] == '/':
                in_comment_c_style = True

        # Not inside a string - do white-space truncation
        elif char == '\n':
            # Multiple new-line sequence - char can be discarded
            if len(char_buf) > 0 and char_buf[-1][0] == '\n':
                continue

        elif char.isspace():
            if len(char_buf) > 0 and char_buf[-1][0] == ' ':
                # Multiple white spaces sequence - char can be discarded
                continue
            else:
                # Standardize white space to ' '
                char = ' '

        # Handle trigraphs - also expanded inside strings
        if trigraphs_enabled and len(char_buf) > 1:
            if char_buf[-2][0] == '?' and char_buf[-1][0] == '?' and char in trigraph_subs.keys():
                char_buf.pop()
                char_buf[-1][0] = trigraph_subs[char]
                if char == '/':
                    # Trigraph sequence: '??/' translates to the escape char '\\'
                    escape_char = True
                continue

        char_buf.append([char, (line_num, char_num)])

        # Push new chars into the buffer
        while len(char_buf) > 3:
            await out_queue.put(char_buf.pop(0))

    while len(char_buf) > 0:
        await out_queue.put(char_buf.pop(0))

    await out_queue.put(None)


async def do_translation_phase_2(in_queue, out_queue):
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

        elif char[0] == '\\' and not escape_char:
            escape_char = True
            continue

        else:
            escape_char = False

        await out_queue.put(char)

    await out_queue.put(None)


async def do_translation_phase_3_remove_comments(in_queue, out_queue):
    """
    Perform the third translation phase - remove comments:
        The source file is decomposed into preprocessing tokens and sequences of
        white-space characters (including comments). Each comment is replaced by one space character.
        - From the ISO standard document.
    """

    char_buf = []

    escape_char = False
    asterisk_char = False

    in_string = False
    in_comment_c_style = False
    in_comment_cpp_style = False

    while True:
        char = await in_queue.get()
        if not char:
            break

        # Push new chars into the buffer
        if in_string:
            # In a string - white spaces are preserved.
            if not escape_char and char[0] == '\"':
                in_string = False
            elif not escape_char and char[0] == '\\':
                escape_char = True
            else:
                escape_char = False

        elif in_comment_cpp_style:
            # In a comment - white spaces are preserved.
            if char[0] == '\n':
                in_comment_cpp_style = False
            else:
                escape_char = False
                continue

        elif in_comment_c_style:
            # In a comment - white spaces are preserved.
            if char[0] == '/' and asterisk_char:
                in_comment_c_style = False
            elif char[0] == '*':
                asterisk_char = True
            else:
                asterisk_char = False

            continue

        elif char[0] == '\"':
            # Start a string
            in_string = True

        elif char[0] == '/':
            if len(char_buf) > 0 and char_buf[-1][0] == '/':
                in_comment_cpp_style = True
                prev_char = char_buf.pop()
                char = [' ', prev_char[1]]

        elif char[0] == '*':
            if len(char_buf) > 0 and char_buf[-1][0] == '/':
                in_comment_c_style = True
                prev_char = char_buf.pop()
                char = [' ', prev_char[1]]

        if not in_string and char[0] == '\n':
            # Do more white-space truncation - new lines
            if len(char_buf) > 0:
                if char_buf[-1][0] == '\n':
                    continue
                if char_buf[-1][0] == ' ':
                    char_buf.pop()
            else:
                continue

        elif not in_string and char[0] == ' ':
            # Do more white-space truncation
            if len(char_buf) > 0:
                if char_buf[-1][0] == ' ' or char_buf[-1][0] == '\n':
                    continue
            else:
                continue

        # Configure char buffer
        char_buf.append(char)

        # Push new chars into the buffer
        while len(char_buf) > 3:
            await out_queue.put(char_buf.pop(0))

    while len(char_buf) > 0:
        await out_queue.put(char_buf.pop(0))

    await out_queue.put(None)


async def do_translation_phase_3_tokenize(in_queue, out_queue):
    """
    Perform the third translation phase:
        The source tile is decomposed into preprocessing tokens and sequences of white-space characters.
        - From the ISO standard document.

    :param in_queue: input queue.
    :param out_queue: lexer token output queue.
    :return: None
    """

    symbols = ('+', '-', '*', '/', '%', '=', '<', '>', '!', '=',
               '&', '|', '^', '~', '.', ':', ';', ',', '[', ']',
               '(', ')', '{', '}', '?', '#', '\n', '\'', '\"',
               ' ', '\\')

    get_next_char = True
    in_string = False
    escape_char = False
    save_buf = False

    token_buf = []
    char = ' '

    while True:
        # Get next character from the queue
        if get_next_char:
            char = await in_queue.get()
            if not char:
                break
        else:
            get_next_char = True

        # Handle string token
        if in_string:
            if not escape_char and char[0] == '\"':
                in_string = False
                save_buf = True
            elif not escape_char and char[0] == '\\':
                escape_char = True
            else:
                escape_char = False

            token_buf[1] = token_buf[1] + char[0]
            continue

        if char[0] in symbols:
            # Handle symbol
            if len(token_buf) > 0:
                save_buf = True
                get_next_char = False
            else:
                token_buf.append(char[1])
                token_buf.append(char[0])

                if char[0] == '\"':
                    in_string = True
                else:
                    save_buf = True
        else:
            # Handle character
            if len(token_buf) == 0:
                token_buf.append(char[1])
                token_buf.append(char[0])
            else:
                token_buf[1] = token_buf[1] + char[0]

            continue

        if save_buf:
            await out_queue.put(LexerToken(token_buf[0], token_buf[1], is_identifier_compatible(token_buf[1])))
            token_buf.clear()
            save_buf = False

    if len(token_buf) > 0:
        await out_queue.put(LexerToken(token_buf[0], token_buf[1], is_identifier_compatible(token_buf[1])))

    await out_queue.put(None)


async def do_translation_phase_4(in_queue, out_queue):
    """
    Perform the first translation phase:
        Preprocessing directives are executed and macro invocations are expanded.
        A #include preprocessing directive causes the named header or source file to be processed from phase
        1 through phase 4, recursively.
        - From the ISO standard document.
    """

    while True:
        # Get next character from the queue
        tok = await in_queue.get()
        if not tok:
            break

        await out_queue.put(tok)

    await out_queue.put(None)


# Summarize all Translation-Phases tasks
translation_tasks = [
    do_translation_phase_1,
    do_translation_phase_2,
    do_translation_phase_3_remove_comments,
    do_translation_phase_3_tokenize,
    do_translation_phase_4
]


async def run_translation(input_funct, input_text: str, phase: int, trigraphs_enabled: bool):
    """
    Run preprocessor on input code.

    :param input_funct: input text function.
    :param input_text: code text for string-input function, source file name for file-input function.
    :param phase: how many translation phases to run.
    :param trigraphs_enabled: allow trigraphs expansions.
    :return: processed output text
    """

    if phase < 1 or phase > 4:
        # TODO: add error.
        pass
    elif phase >= 3:
        phase += 1

    data_queues = [asyncio.Queue() for _ in range(5)]
    active_tasks =\
        [asyncio.create_task(translation_tasks[0](input_funct, input_text, data_queues[0], trigraphs_enabled))]
    out_text = []

    for i in range(1, phase):
        active_tasks.append(translation_tasks[i](data_queues[i - 1], data_queues[i]))

    active_tasks.append(asyncio.create_task(cat_output_text(data_queues[phase - 1], out_text)))

    await asyncio.gather(*active_tasks)

    return "".join(out_text)


# async def do_tokenize_from_string(in_string: str):
#     '''
#     Read a short string and perform tokenization, as if it appeared during the third translation phase.
#     :param in_string: input code string
#     :return: preprocessor lexer token-list
#     '''
#
#     queue_cli_macro = asyncio.Queue(3)
#
#     parse_lst = list()
#
#     '''
#     Since the input string does not go through the first two translation phases, it's necessary to
#     validate no illegal sequences appear in the string.
#     '''
#     if '//' in in_string or '/*' in in_string or '*/' in in_string:
#         # TODO: handle invalid input warning
#         pass
#     if '\r' in in_string:
#         # TODO: handle unsupported characters in input string warning
#         pass
#
#         macro_in_task = asyncio.create_task(read_input_string(in_string, queue_cli_macro))
#         macro_tokenize_task =(
#             asyncio.create_task(do_translation_phase_3_tokenize(queue_cli_macro, parse_lst)))
#
#         await asyncio.gather(macro_in_task, macro_tokenize_task)
#
#     return parse_lst


# async def do_tokenize_from_file(file_name: str):
#     '''
#     Read a source file and perform the first three translation phases producing a preprocessor token list.
#     :param file_name: input source file
#     :return: preprocessor lexer token-list
#     '''
#
#     queue_phase_1 = asyncio.Queue(5)
#     queue_phase_2 = asyncio.Queue(5)
#     queue_phase_3 = asyncio.Queue(5)
#
#     parse_lst = list()
#
#     phase_1_task = asyncio.create_task(do_translation_phase_1(file_name, queue_phase_1))
#     phase_2_task = asyncio.create_task(do_translation_phase_2(queue_phase_1, queue_phase_2))
#     phase_3_task_cr = asyncio.create_task(do_translation_phase_3_remove_comments(queue_phase_2, queue_phase_3))
#     phase_3_task = asyncio.create_task(do_translation_phase_3_tokenize(queue_phase_3, parse_lst))
#
#     await asyncio.gather(phase_1_task, phase_2_task, phase_3_task_cr, phase_3_task)
#
#     return parse_lst


# def do_process_directives(lexer_lst: list, macros_dict: dict):
#     """
#     Perform preprocessor directive processing.
#     :param lexer_lst: lexer token-list.
#     :param macros_dict: dictionary of defined macros.
#     :return: None.
#     TODO: move to cparser
#     """
#
#     i = 0
#     while i < len(lexer_lst):
#         if lexer_lst[i] == '#':
#             # This might be a directive
#             pass
#
#         else:
#             i += 1


__all__ = ["run_translation", "input_txt_from_file", "input_txt_from_string"]