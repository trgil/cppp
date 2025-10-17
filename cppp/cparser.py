"""
A source parser source: cparser.py

Author:     Gil Treibush
Version:    1.0.0-alpha.1
License:    MIT License
"""

import asyncio
from typing import Callable

from .ltoken import LexerToken
from .directives import is_identifier_compatible, directives_external_define_do_process

# ##############################################################################
#                           Common Input/Output Phases
# ##############################################################################


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

# ##############################################################################
#                               Translation Phases
# ##############################################################################


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


async def do_translation_phase_3_tokenize(in_queue, out_queue, keep_trace: bool = True):
    """
    Perform the third translation phase:
        The source tile is decomposed into preprocessing tokens and sequences of white-space characters.
        - From the ISO standard document.

    :param in_queue: input queue.
    :param out_queue: lexer token output queue.
    :param keep_trace: Keep track of the trace data for each token.
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
            if not keep_trace:
                token_buf[0] = (-1, -1)
            await out_queue.put(LexerToken(token_buf[0], token_buf[1], is_identifier_compatible(token_buf[1])))
            token_buf.clear()
            save_buf = False

    if len(token_buf) > 0:
        if not keep_trace:
            token_buf[0] = (-1, -1)
        await out_queue.put(LexerToken(token_buf[0], token_buf[1], is_identifier_compatible(token_buf[1])))

    await out_queue.put(None)


async def do_translation_phase_3_aggregate_tokens(in_queue, out_queue):
    """
    This is not an official part of the third translation phase (as described by the C standard),
    but, it performs some additional translation tasks which generally belong to this stage.
    Translation tasks: combine three '.' symbols into the ellipsis symbol, translate digraphs & combine
    logical operators into dedicated symbols.

    :param in_queue: lexer token input queue.
    :param out_queue: lexer token output queue.
    :return: None
    """

    token_buf = []

    while True:
        # Get next token from the queue
        tok = await in_queue.get()
        if not tok:
            break

        # Append the token to the aggregation queue
        token_buf.append(tok)

        if len(token_buf) > 2:
            # Handle an ellipsis symbol
            if token_buf[-3].val == '.' and token_buf[-2].val == '.' and token_buf[-1].val == '.':
                token_buf.pop()
                token_buf.pop()
                token_buf[-1].val = '...'

            # Handle digraphs
            if token_buf[-2].val == '<':
                if token_buf[-1].val == ':':
                    # Digraph "<:" -> '['
                    token_buf.pop()
                    token_buf[-1].val = '['
                elif token_buf[-1].val == '%':
                    # Digraph "<%" -> '{'
                    token_buf.pop()
                    token_buf[-1].val = '{'
            elif token_buf[-2].val == '%':
                if token_buf[-1].val == '>':
                    # Digraph "%>" -> '}'
                    token_buf.pop()
                    token_buf[-1].val = '}'
                elif token_buf[-1].val == ':':
                    # Digraph "%:" -> '#'
                    token_buf.pop()
                    token_buf[-1].val = '#'
            elif token_buf[-2].val == ':':
                if token_buf[-1].val == '>':
                    # Digraph ":>" -> ']'
                    token_buf.pop()
                    token_buf[-1].val = ']'

            # TODO: add handling for preprocessor relevant operators

        # Push latest token into the output queue
        while len(token_buf) > 3:
            await out_queue.put(token_buf.pop(0))

    # Push remaining tokens into the output queue
    while len(token_buf) > 0:
        await out_queue.put(token_buf.pop(0))

    await out_queue.put(None)


async def do_translation_phase_4(in_queue, out_queue, macro_dict):
    """
    Perform the first translation phase:
        Preprocessing directives are executed and macro invocations are expanded.
        A #include preprocessing directive causes the named header or source file to be processed from phase
        1 through phase 4, recursively.
        - From the ISO standard document.
    """

    directive_buf = []

    while True:
        # Get next character from the queue
        tok = await in_queue.get()
        if not tok:
            break

        if len(directive_buf):
            if tok.val == '\n':
                # End the macro read
                directive_buf.clear()
            else:
                directive_buf.append(tok)
        elif tok.val == '#':
            # Start macro read
            directive_buf.append(tok)
        else:
            # Process non-macro text
            if tok.identifier_compatible:
                # Check if it's a macro name
                pass
            await out_queue.put(tok)

    await out_queue.put(None)

# ##############################################################################
#                                   Runners
# ##############################################################################


async def do_macro_parse_from_list(in_queue):
    """
    Perform macro translation from tokens from the CLI into a cMacro object.
    """

    macro_tokens = []
    truncate_space = True

    while True:
        # Get next character from the queue
        tok = await in_queue.get()
        if not tok:
            break

        if truncate_space and tok.val == " ":
            continue
        elif tok.val == " ":
            truncate_space = True
        else:
            truncate_space = False

        macro_tokens.append(tok)

    return macro_tokens


# Summarize all Translation-Phases tasks
translation_tasks = [
    do_translation_phase_1,
    do_translation_phase_2,
    do_translation_phase_3_remove_comments,
    do_translation_phase_3_tokenize,
    do_translation_phase_3_aggregate_tokens,
    do_translation_phase_4
]


async def run_translation(input_funct, input_text: str, phase: int, trigraphs_enabled: bool, macro_dict: None = None):
    """
    Run preprocessor pipeline up to given phase stage, on input code.

    :param input_funct: input text function.
    :param input_text: code text for string-input function, source file name for file-input function.
    :param phase: how many translation phases to run.
    :param trigraphs_enabled: allow trigraphs expansions.
    :param macro_dict: dictionary of predefined macros
    :return: processed output text
    """

    # Translation phase 4 needs a dictionary parameter to track macros
    if phase >=4 and macro_dict is None:
        macro_dict = {}

    # Validate phase number
    if phase < 1 or phase > 4:
        # TODO: add error.
        pass
    elif phase >= 3:
        phase += 2  # Because phase 3 adds 3 sub-phases instead of 1 (2 extra)

    # Generate data queues for inner-pipeline communication
    data_queues = [asyncio.Queue() for _ in range(len(translation_tasks))]
    # Set initial code input method
    active_tasks =\
        [asyncio.create_task(translation_tasks[0](input_funct, input_text, data_queues[0], trigraphs_enabled))]
    out_text = []

    # Set active pipeline tasks
    for i in range(1, phase):
        if i == 5:  # Phase 4 processes macros - requires macro dictionary
            active_tasks.append(translation_tasks[i](data_queues[i - 1], data_queues[i], macro_dict))
        else:
            active_tasks.append(translation_tasks[i](data_queues[i - 1], data_queues[i]))

    active_tasks.append(asyncio.create_task(cat_output_text(data_queues[phase - 1], out_text)))

    # TODO: handle exceptions returning from pipe execution
    await asyncio.gather(*active_tasks)

    return "".join(out_text)


async def make_macro_from_cli(macro_txt: str, macro_dict):
    """
    Run a reduced translation pipeline for CLI macros only:
        The contents of definition are tokenized and processed as if they
        appeared during translation phase three in a ‘#define’ directive.
            - From the GCC documentation.

    The input should go through a quick processing and comment removal, before getting here.

    :param macro_txt: macro input text.
    :param macro_dict: dictionary of predefined macros
    :return: processed output text
    """

    queue_phase_1 = asyncio.Queue(5)
    queue_phase_3 = asyncio.Queue(5)
    queue_phase_3_2 = asyncio.Queue(5)

    phase_1_task = asyncio.create_task(
        do_translation_phase_1(input_txt_from_string, macro_txt, queue_phase_1))

    phase_3_task = asyncio.create_task(
        do_translation_phase_3_tokenize(queue_phase_1, queue_phase_3, False))

    phase_3_2_task = asyncio.create_task(
        do_translation_phase_3_aggregate_tokens(queue_phase_3, queue_phase_3_2))

    macro_parser_task = asyncio.create_task(
        do_macro_parse_from_list(queue_phase_3_2))

    # TODO: handle exceptions returning from pipe execution
    await asyncio.gather(phase_1_task, phase_3_task, phase_3_2_task, macro_parser_task)
    new_macro_tokens = await macro_parser_task

    # TODO: Parse macro and return value
    directives_external_define_do_process(new_macro_tokens, macro_dict)


__all__ = ["run_translation", "input_txt_from_file", "input_txt_from_string", "make_macro_from_cli"]