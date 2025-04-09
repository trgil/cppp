"""
CPP directives handlers source: directives.py

Author:     Gil Treibush
Version:    1.0.0-alpha.1
License:    MIT License
"""

import re
from dataclasses import dataclass

from .cmacro import CMacro
from .ltoken import LexerToken


@dataclass
class ConditionalDirective:
    cond_type: str
    val: str
    result: bool


_c_keywords = [
    "auto", "break", "case", "char", "const", "continue", "default", "do", "double",
    "else", "enum", "extern", "float", "for", "goto", "if", "int", "long", "register",
    "return", "short", "signed", "sizeof", "static", "struct", "switch", "typedef",
    "union", "unsigned", "void", "volatile", "while", "_Bool", "_Complex", "_Imaginary",
    "inline", "restrict", "_Alignas", "_Alignof", "_Atomic", "_Generic",
    "_Noreturn", "_Static_assert", "_Thread_local"
]

_cpp_keywords = [
    "asm", "bool", "catch", "class", "const_cast", "delete", "dynamic_cast",
    "explicit", "export", "false", "friend", "inline", "mutable", "namespace", "new",
    "operator", "private", "protected", "public", "reinterpret_cast", "static_cast",
    "template", "this", "throw", "true", "try", "typeid", "typename", "using",
    "virtual", "wchar_t"
]

# C++11 and later
_cpp_11_keywords = [
    "alignas", "alignof", "char16_t", "char32_t", "constexpr", "decltype",
    "final", "noexcept", "nullptr", "override", "static_assert", "thread_local"
]

# C++17 and later
_cpp_17_keywords = [
    "concept", "consteval", "constinit", "requires"
]

# C++20 and later
_cpp_20_keywords = [
    "co_await", "co_return", "co_yield", "requires", "constexpr", "export",
    "synchronized", "atomic_cancel", "atomic_commit", "atomic_noexcept"
]

_macro_name_rgx = r"^[A-Za-z_][A-Za-z0-9_]*$"


def is_identifier_compatible(name):
    '''
    Verify the name is compatible with the rules for a valid C/C++ identifier.
    :param name: input name.
    :return: Boolean - compatibility status.
    '''

    return bool(re.match(_macro_name_rgx, name))


def _is_valid_identifier_name(name):
    '''
    Verify the name is compatible with the rules for a valid C/C++ identifier. Verify that the
    name does not clash with C/C++ keywords or other macros.
    :param name: input name.
    :return: None.
    '''

    # Note: produce warnings on:
    #   String size (check compiler length limit).
    #   Redefines a reserved keyword.
    #   Uses a reserved pattern.
    #   Contains an illegal character (unlikely).

    # TODO: implement other checks

    return is_identifier_compatible(name)


def _cpp_directive_handle_define(lexer_lst, i, macros_dict, token_len, token_total_len):
    """
    Process a #define-type macros.
    """

    # TODO: to be implemented

    ### Debug Prints ###
    print(f"Directive handler: define")

    return 0


def _cpp_directive_handle_undef(lexer_lst, i, macros_dict, token_len, token_total_len):
    """
    Process an #undef macro.
    """

    # TODO: to be implemented

    ### Debug Prints ###
    print(f"Directive handler: undef")

    return 0


def _cpp_directive_handle_if(lexer_lst, i, macros_dict, token_len, token_total_len):
    """
    Process an #if macro.
    """

    # TODO: to be implemented

    ### Debug Prints ###
    print(f"Directive handler: if")

    return 0


def _cpp_directive_handle_elif(lexer_lst, i, macros_dict, token_len, token_total_len):
    """
    Process an #elif macro.
    """

    # TODO: to be implemented

    ### Debug Prints ###
    print(f"Directive handler: elif")

    return 0


def _cpp_directive_handle_else(lexer_lst, i, macros_dict, token_len, token_total_len):
    """
    Process an #else macro.
    """

    # TODO: to be implemented

    ### Debug Prints ###
    print(f"Directive handler: else")

    return 0


def _cpp_directive_handle_endif(lexer_lst, i, macros_dict, token_len, token_total_len):
    """
    Process an #endif macro.
    """

    # TODO: to be implemented

    ### Debug Prints ###
    print(f"Directive handler: endif")

    return 0


def _cpp_directive_handle_defs_ifdef(lexer_lst, i, macros_dict, token_len, token_total_len):
    """
    Process an #ifdef macro.
    """

    # TODO: to be implemented

    ### Debug Prints ###
    print(f"Directive handler: ifdef")

    return 0


def _cpp_directive_handle_defs_ifndef(lexer_lst, i, macros_dict, token_len, token_total_len):
    """
    Process an #ifndef macro.
    """

    # TODO: to be implemented

    ### Debug Prints ###
    print(f"Directive handler: ifndef")

    return 0


def _cpp_directive_handle_include(lexer_lst, i, macros_dict, token_len, token_total_len):
    """
    Process an #include macro.
    """

    # TODO: to be implemented

    ### Debug Prints ###
    print(f"Directive handler: include")

    return 0


def _cpp_directive_handle_error(lexer_lst, i, macros_dict, token_len, token_total_len):
    """
    Process an #error macro - Not currently supported!
    """

    return 0


def _cpp_directive_handle_warning(lexer_lst, i, macros_dict, token_len, token_total_len):
    """
    Process a #warning macro - Not currently supported!
    """

    return 0


def _cpp_directive_handle_line(lexer_lst, i, macros_dict, token_len, token_total_len):
    """
    Process a #line macro - Not currently supported!
    """

    return 0


def _cpp_directive_handle_pragma(lexer_lst, i, macros_dict, token_len, token_total_len):
    """
    Process a #pragma macro - Not currently supported!
    """

    return 0


_cpp_directive_handlers = {
    "define":   _cpp_directive_handle_define,
    "undef":    _cpp_directive_handle_undef,
    "if":       _cpp_directive_handle_if,
    "elif":     _cpp_directive_handle_elif,
    "else":     _cpp_directive_handle_else,
    "endif":    _cpp_directive_handle_endif,
    "ifdef":    _cpp_directive_handle_defs_ifdef,
    "ifndef":   _cpp_directive_handle_defs_ifndef,
    "include":  _cpp_directive_handle_include,
    "error":    _cpp_directive_handle_error,
    "warning":  _cpp_directive_handle_warning,
    "line":     _cpp_directive_handle_line,
    "pragma":   _cpp_directive_handle_pragma
}


def _do_macro_sub(lexer_lst, i, macros_dict):

    # TODO: to be implemented

    return 1


def _cpp_directive_get_size(lexer_lst, i):
    """
    Find the size of the defined macro - from '#' to '\n'.
    :param lexer_lst: lexer token-list.
    :param i: current token index.
    :return: token-length of the macro.
    """

    directive_tokens = 1
    directive_non_space_tokens = 0

    while i + directive_tokens < len(lexer_lst):
        if lexer_lst[i + directive_tokens] == '\n':
            break
        elif lexer_lst[i + directive_tokens] != ' ':
            directive_non_space_tokens += 1

        directive_tokens += 1

    return directive_tokens, directive_non_space_tokens


def _do_perform_directive(lexer_lst, i, macros_dict):
    """
    Perform preprocessor directive processing.
    :param lexer_lst: lexer token-list.
    :param i: current token index.
    :param macro_dict: dictionary of defined macros.
    :return: list index offset after processing the directive.
    """

    tokens_total_len, tokens_len = _cpp_directive_get_size(lexer_lst, i)

    if tokens_len == 0:
        # This is an empty directive (might be reported with flags such as '-Wpedantic').
        del lexer_lst[i]
        return 0

    # Find first directive token
    j = 1
    while j < tokens_total_len and lexer_lst[i + j] == ' ':
         j += 1

    if lexer_lst[i + j].val in _cpp_directive_handlers.keys():
        # This seems to be a valid directive

        # Remove anything prior to the first token
        del lexer_lst[i:i + j]

        # Get the directive handler function
        directive_handler = _cpp_directive_handlers[lexer_lst[i].val]

        # Call handler function
        directive_offset = directive_handler(lexer_lst, i, macros_dict, tokens_len, tokens_total_len - j)

        # Remove the rest of the directive
        del lexer_lst[i:i + (tokens_total_len - j)]

        return directive_offset

    else:
        # TODO: handle unresolved directive error
        return 1 # Handle as if not a directive


def directives_do_process(lexer_lst, macros_dict):
    """
    Perform preprocessor directive processing.
    :param lexer_lst: lexer token-list.
    :param macro_dict: dictionary of defined macros.
    :return: None.
    """

    i = 0

    while i < len(lexer_lst):
        if lexer_lst[i] == '#':
            # This might be a directive

            j = 1

            while (i - j) >= 0:
                if lexer_lst[i - j] == ' ':
                    continue
                else:
                    break

            if i == 0 or lexer_lst[i - j] == '\n':
                # This is indeed a directive
                directive_offset = _do_perform_directive(lexer_lst, i, macros_dict)
                i += directive_offset

        elif lexer_lst[i].identifier_compatible and lexer_lst[i].val in macros_dict.keys():
            # This is a defined macro - do substitution
            macro_offset = _do_macro_sub(lexer_lst, i, macros_dict)
            i += macro_offset

        else:
            i += 1


__all__ = ["is_identifier_compatible", "directives_do_process"]