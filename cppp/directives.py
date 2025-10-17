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

# ##############################################################################
#                              Halper Structures
# ##############################################################################


@dataclass
class ConditionalDirective:
    cond_type: str
    val: str
    result: bool


# Standard C
_c_keywords = [
    "auto", "break", "case", "char", "const", "continue", "default", "do", "double",
    "else", "enum", "extern", "float", "for", "goto", "if", "int", "long", "register",
    "return", "short", "signed", "sizeof", "static", "struct", "switch", "typedef",
    "union", "unsigned", "void", "volatile", "while", "_Bool", "_Complex", "_Imaginary",
    "inline", "restrict", "_Alignas", "_Alignof", "_Atomic", "_Generic",
    "_Noreturn", "_Static_assert", "_Thread_local"
]

# Standard C++
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

# Standard C
_c_predefined_macros_mandatory = [
    "__DATE__", "__FILE__", "__LINE__", "__STDC__", "__STDC_HOSTED__", "__STDC_VERSION__", "__TIME__"
]

# Standard C
_c_predefined_macros_environment = [
    "__STDC_ISO_10646__", "__STDC_MB_MIGHT_NEQ_WC__", "__STDC_UTF_16__", "__STDC_UTF_32__"
]

# Standard C
_c_predefined_macros_conditional_features = [
    "__STDC_ANALYZABLE__", "__STDC_IEC_559__", "__STDC_IEC_559_COMPLEX__", "__STDC_LIB_EXT1__",
    "__STDC_NO_COMPLEX__", "__STDC_NO_THREADS__", "__STDC_NO_VLA__", "__STDC_NO_ATOMICS__"
]

_macro_name_rgx = r"^[A-Za-z_][A-Za-z0-9_]*$"

# TODO: pass to each function by value
_dbg_line_offset_num = 0
_dbg_line_offset_file = ""

# ##############################################################################
#                              Halper Functions
# ##############################################################################


def is_identifier_compatible(name: str):
    '''
    Verify the name is compatible with the rules for a valid C/C++ identifier.
    :param name: input name.
    :return: Boolean - compatibility status.
    '''

    # TODO: return dedicated error message
    return bool(re.match(_macro_name_rgx, name))


def _is_valid_identifier_name(name: str):
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

    if name in _c_keywords:
        # TODO: return dedicated error message
        return False
    if name in _cpp_keywords:
        # TODO: return dedicated error message
        return False
    if name in _cpp_11_keywords:
        # TODO: return dedicated error message
        return False
    if name in _cpp_17_keywords:
        # TODO: return dedicated error message
        return False
    if name in _cpp_20_keywords:
        # TODO: return dedicated error message
        return False
    if name in _c_predefined_macros_mandatory:
        # TODO: return dedicated error message
        return False
    if name in _c_predefined_macros_environment:
        # TODO: return dedicated error message
        return False
    if name in _c_predefined_macros_conditional_features:
        # TODO: return dedicated error message
        return False

    return is_identifier_compatible(name)

# ##############################################################################
#                             Directive Handlers
# ##############################################################################


def _cpp_directive_handle_define(lexer_lst: list, macros_dict: dict, cond_queue: list = None) -> int:
    """
    Process a #define-type directive:
        define_directive ::= "#" [ " " ] "define" " " <identifier> ( function_macro | object_macro )
        function_macro   ::= "(" [ parameter_list ] ")" [ " " ] [ replacement_text ]
        object_macro     ::= [ " " replacement_text ]
        parameter_list   ::= ( <identifier> { "," <identifier> } [ "," "..." ] ) | "..."
         - From the standard (in EBNF).

        After verification a new macro is added into the shared macros' dictionary.
    """

    token_total_len = len(lexer_lst)
    i = 0

    function_like = False
    variadic = False

    # First token should be macro name
    if not lexer_lst[i].identifier_compatible:
        # TODO: add error handling
        return token_total_len

    macro_name = lexer_lst[i].val
    macro_parameters = []
    j = 1

    # TODO: check if macro redefined
    # TODO: check if macro name is valid (check collision with keywords / predefined macros)

    # Handle a function-like macro
    if token_total_len > 1 and lexer_lst[i + 1].val == '(':
        # Parser parameter list of a function-like macro
        function_like = True
        separator_found = True
        j = 2

        # TODO: add handling for variadic macros

        # Read all parameters from '(' to ')'
        while (i + j) < token_total_len:

            # Remove spaces before parameter
            while (i + j) < token_total_len and lexer_lst[i + j].val == ' ':
                j += 1

            # Check if end of parameter list (find the ')' character)
            if lexer_lst[i + j].val == ')':
                if len(macro_parameters) > 0 and separator_found:
                    # TODO: handle error
                    return token_total_len
                break

            # Get next parameter (identifier)
            if not lexer_lst[i + j].identifier_compatible:
                if lexer_lst[i + j].val == '...':
                    if variadic:
                        # TODO: handle error
                        return token_total_len
                    else:
                        variadic = True
                else:
                    # TODO: handle error
                    return token_total_len

            # We didn't find a ')' character, and we found a parameter, we must check for a separator.
            if not separator_found:
                # TODO: handle error
                return token_total_len

            macro_parameters.append(lexer_lst[i + j])
            separator_found = False
            j += 1

            # Remove spaces
            while (i + j) < token_total_len and lexer_lst[i + j].val == ' ':
                j += 1

            # Remove separator
            if lexer_lst[i + j].val == ',':
                separator_found = True
                j += 1

        # Parameter processing is over, make sure we end on an ')'
        if function_like and lexer_lst[i + j].val != ')':
            # TODO: handle error
            return token_total_len
        else:
            j += 1

    macro_value = []
    # Remove value preceding white spaces
    while (i + j) < token_total_len and lexer_lst[i + j].val == ' ':
        j += 1

    while (i + j) < token_total_len:
        macro_value.append(lexer_lst[i + j])
        j += 1

    if len(macro_value) == 0:
        macro_value.append(LexerToken((-1, -1), "1", False))

    if function_like:
        if variadic:
            macros_dict[macro_name] =(
                CMacro(value=macro_value, params=macro_parameters, function_like=True, variadic=True))
        else:
            macros_dict[macro_name] =(
                CMacro(value=macro_value, params=macro_parameters, function_like=True, variadic=False))
    else:
        macros_dict[macro_name] = CMacro(value=macro_value, function_like=False, variadic=False)

    return token_total_len


def _cpp_directive_handle_undef(lexer_lst: list, macros_dict: dict, cond_queue: list = None) -> int:
    """
    Process an #undef-type directive:
        undef_directive ::= "#" [ " " ] "undef" " " <identifier>
         - From the standard (in EBNF).

        If macro exists in the shared macros' dictionary, it will be removed.
    """

    if len(lexer_lst) != 1:
        # TODO: handle invalid directive format
        pass
    else:
        if lexer_lst[0].val in macros_dict.keys():
            del macros_dict[lexer_lst[0].val]
        else:
            # Undef a non-defined macro warning
            pass

    return 0


def _cpp_directive_handle_include(lexer_lst: list, macros_dict: dict, cond_queue: list = None) -> int:
    """
    Process an #include-type directive:
        include_directive   ::= "#" [ " " ] "include" " " ( <angle_bracket_path> | <quote_path> | <macro_name> )
        angle_bracket_path  ::= "<" <filename> ">"
        quote_path          ::= '"' <filename> '"'
        macro_name          ::= <identifier>
         - From the standard (in EBNF).

        Operation: TBD.
    """

    # TODO: to be implemented

    ### Debug Prints ###
    print(f"Directive handler: include")

    return 0


def _cpp_directive_handle_error(lexer_lst: list, macros_dict: dict, cond_queue: list = None) -> int:
    """
    Process a #error-type directive:
        warning_directive ::= "#" [ " " ] "warning" [ " " <message_text> ]
         - From the standard (in EBNF).

        After validation, a dedicated error with users' message is returned.
    """

    return 0


def _cpp_directive_handle_warning(lexer_lst: list, macros_dict: dict, cond_queue: list = None) -> int:
    """
    Process a #warnning-type directive:
        error_directive ::= "#" [ " " ] "error" [ " " <message_text> ]
         - From the standard (in EBNF).

        After validation, a dedicated warning with users' message is returned.
    """

    return 0


def _cpp_directive_handle_line(lexer_lst: list, macros_dict: dict, cond_queue: list = None) -> int:
    """
    Process a #line-type directive:
        line_directive ::= "#" [ " " ] "line" " " <integer_literal> [ " " <string_literal> ]
         - From the standard (in EBNF).

        Add offset to line number for current file, optionally change the files' name.
    """

    return 0


def _cpp_directive_handle_pragma(lexer_lst: list, macros_dict: dict, cond_queue: list = None) -> int:
    """
    Process a #pragma-type directive:
        pragma_directive ::= "#" [ " " ] "pragma" [ <implementation_defined_tokens> ]
         - From the standard (in EBNF).

        Operation: TBD.

        NOTE: An empty pragma directive is allowed, but would probably produce a warning in most
        compilers. Thus, a dedicated error message is returned.
    """

    return 0


def _cpp_directive_handle_if(lexer_lst: list, macros_dict: dict, cond_queue: list = None) -> int:
    """
    Process an #if-type directive:
        if_line ::= "#" [ " " ] "if" " " <constant_expression>
         - From the standard (in EBNF).
    """

    # TODO: to be implemented

    ### Debug Prints ###
    print(f"Directive handler: if")

    return 0


def _cpp_directive_handle_elif(lexer_lst: list, macros_dict: dict, cond_queue: list = None) -> int:
    """
    Process a #elif-type directive:
        elif_line ::= "#" [ " " ] "elif" " " <constant_expression>
         - From the standard (in EBNF).
    """

    # TODO: to be implemented

    ### Debug Prints ###
    print(f"Directive handler: elif")

    return 0


def _cpp_directive_handle_ifdef(lexer_lst: list, macros_dict: dict, cond_queue: list = None) -> int:
    """
    Process a #ifdef-type directive:
        ifdef_line ::= "#" [ " " ] "ifdef" " " <identifier>
         - From the standard (in EBNF).
    """

    # TODO: to be implemented

    ### Debug Prints ###
    print(f"Directive handler: ifdef")

    return 0


def _cpp_directive_handle_ifndef(lexer_lst: list, macros_dict: dict, cond_queue: list = None) -> int:
    """
    Process a #ifndef-type directive:
        ifndef_line ::= "#" [ " " ] "ifndef" " " <identifier>
         - From the standard (in EBNF).
    """

    # TODO: to be implemented

    ### Debug Prints ###
    print(f"Directive handler: ifndef")

    return 0


def _cpp_directive_handle_elifdef(lexer_lst: list, macros_dict: dict, cond_queue: list = None) -> int:
    """
    Process an #elifdef-type directive:
        elifdef_line ::= "#" [ " " ] "elifdef" " " <identifier>
         - From the standard (in EBNF).
        This directive was added in C++23 standard.
    """

    # TODO: to implemented

    ### Debug Prints ###
    print(f"Directive handler: ifndef")

    return 0


def _cpp_directive_handle_elifndef(lexer_lst: list, macros_dict: dict, cond_queue: list = None) -> int:
    """
    Process an #elifndef-type directive:
        elifndef_line ::= "#" [ " " ] "elifndef" " " <identifier>
         - From the standard (in EBNF).
        This directive was added in C++23 standard.
    """

    # TODO: to implemented

    ### Debug Prints ###
    print(f"Directive handler: ifndef")

    return 0


def _cpp_directive_handle_else(lexer_lst: list, macros_dict: dict, cond_queue: list = None) -> int:
    """
    Process a #else-type directive:
        else_block  ::= "#" [ " " ] "else" <source_code_block>
         - From the standard (in EBNF).
    """

    # TODO: to be implemented

    ### Debug Prints ###
    print(f"Directive handler: else")

    return 0


def _cpp_directive_handle_endif(lexer_lst: list, macros_dict: dict, cond_queue: list = None) -> int:
    """
    Process a #endif-type directive:
        endif_line ::= "#" [ " " ] "endif"
         - From the standard (in EBNF).

        Pops out the last conditional statement from the conditionals queue.
    """

    # TODO: to be implemented

    ### Debug Prints ###
    print(f"Directive handler: endif")

    return 0


_cpp_directive_handlers = {
    "if":       _cpp_directive_handle_if,
    "elif":     _cpp_directive_handle_elif,
    "else":     _cpp_directive_handle_else,
    "endif":    _cpp_directive_handle_endif,
    "ifdef":    _cpp_directive_handle_ifdef,
    "ifndef":   _cpp_directive_handle_ifndef,
    "elifndef":   _cpp_directive_handle_elifndef,
    "elifdef":   _cpp_directive_handle_elifdef,
    "define": _cpp_directive_handle_define,
    "undef": _cpp_directive_handle_undef,
    "include":  _cpp_directive_handle_include,
    "error":    _cpp_directive_handle_error,
    "warning":  _cpp_directive_handle_warning,
    "line":     _cpp_directive_handle_line,
    "pragma":   _cpp_directive_handle_pragma
}

# ##############################################################################
#                             Macro Handlers
# ##############################################################################


def _do_add_predefined_macros(macros_dict: dict):
    """
    Add standard predefined macros to the main macros dictionary.
    :param macros_dict: defined macros dictionary.
    :return: macro offset.
    """
    pass


# TODO: move to a dedicated file
def _do_macro_sub(lexer_lst: list, i: int, macros_dict: dict):
    """
    Perform macro substitution.
    :param lexer_lst: token list.
    :param i: current token index.
    :param macros_dict: defined macros dictionary.
    :return: macro offset.
    """

    ### Debug prints ###
    print(f"doing macro sub: {lexer_lst[i]}")

    sub_macro = macros_dict[lexer_lst[i].val]

    if sub_macro.function_like:
        if sub_macro.variadic:
            # A variadic macro
            pass
        else:
            # A simple function-like macro
            pass
    else:
        # A non-function-like macro
        pass

    return 1


def directives_do_process(lexer_lst: list, macros_dict: dict):
    """
    Perform preprocessor directive processing.
    :param lexer_lst: lexer token-list - the list should contain the entire macro (# up to the \n).
    :param macros_dict: dictionary of defined macros.
    :return: None.
    """

    # Get directive line size
    tokens_total_len = len(lexer_lst)
    # Get to the first non-white-space token
    j = 0
    while j <= tokens_total_len and lexer_lst[j].val == ' ':
        j += 1

    # First token value should be a: '#'
    if j >= tokens_total_len or lexer_lst[j].val != '#':
        # TODO: return an error
        return None

    # Remove space between "#" and the directive name
    j += 1
    while j < tokens_total_len and lexer_lst[j].val == ' ':
        j += 1

    # Check empty directive
    if j >= tokens_total_len:
        # TODO: Return a warning if enabled
        return None

    # Find directive handler and run it
    directive_name = lexer_lst[j].val

    if directive_name not in _cpp_directive_handlers:
        # TODO: return error "undefined directive"
        return

    # Remove anything prior to the first macro token
    while j < tokens_total_len and lexer_lst[j].val == ' ':
        j += 1
    del lexer_lst[0:j + 1]

    # Get the directive handler function
    directive_handler = _cpp_directive_handlers[directive_name]

    # Call handler function
    directive_offset = directive_handler(lexer_lst, macros_dict)


def directives_external_define_do_process(lexer_lst: list, macros_dict: dict):
    """
    Perform preprocessor directive processing.
    :param lexer_lst: lexer token-list.
    :param macros_dict: dictionary of defined macros.
    :return: None.
    TODO: move to cparser
    """

    # Get to the first non-white-space token, delete prior values
    j = 0
    while lexer_lst[j].val == ' ':
        j += 1
    del lexer_lst[0:j]

    _cpp_directive_handle_define(lexer_lst, macros_dict)


__all__ = ["is_identifier_compatible", "directives_do_process"]