"""
CPP directives handlers source: directives.py

Author:     Gil Treibush
Version:    1.0.0-alpha.1
License:    MIT License
"""

import re


def _cpp_directive_handle_define(lexer_lst, macros_lst):
    pass


def _cpp_directive_handle_undef(lexer_lst, macros_lst):
    pass


def _cpp_directive_handle_if(lexer_lst, macros_lst):
    pass


def _cpp_directive_handle_elif(lexer_lst, macros_lst):
    pass


def _cpp_directive_handle_else(lexer_lst, macros_lst):
    pass


def _cpp_directive_handle_endif(lexer_lst, macros_lst):
    pass


def _cpp_directive_handle_defs_ifdef(lexer_lst, macros_lst):
    pass


def _cpp_directive_handle_defs_ifndef(lexer_lst, macros_lst):
    pass


def _cpp_directive_handle_include(lexer_lst, macros_lst):
    pass


def _cpp_directive_handle_error(lexer_lst, macros_lst):
    pass


def _cpp_directive_handle_warning(lexer_lst, macros_lst):
    pass


def _cpp_directive_handle_line(lexer_lst, macros_lst):
    pass


def _cpp_directive_handle_pragma(lexer_lst, macros_lst):
    pass


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

_macro_name_rgx = r"^[A-Za-z_][A-Za-z0-9_]*$"

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


def is_identifier_compatible(name):
    return bool(re.match(_macro_name_rgx, name))


def _is_valid_identifier_name(name):
    # Note: produce warnings on:
    #   String size (check compiler length limit).
    #   Redefines a reserved keyword.
    #   Uses a reserved pattern.
    #   Contains an illegal character (unlikely).
    return is_identifier_compatible(name)


def cpp_directives_do_process(lexer_lst, i):
    if lexer_lst[i + 1] == '\n':
        # This is an empty directive
        return 2

    if not lexer_lst[i + 1].val in _cpp_directive_handlers.keys():
        # Raise error
        print(f"Unknown directive {lexer_lst[i + 1]}")
        return 0
    else:
        _cpp_directive_handlers[lexer_lst[i + 1].val](lexer_lst, i + 1)


def do_macro_sub(lexer_lst, i):
    pass


__all__ = ["is_identifier_compatible", "cpp_directives_do_process", "do_macro_sub"]