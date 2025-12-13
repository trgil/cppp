"""
A macro substitution handler: substitutions.py

Author:     Gil Treibush
Version:    1.0.0-alpha.1
License:    MIT License
"""

from .ltoken import LexerToken


def _do_dict_sub(macro_val_tokens: list, params_dict: dict, va_args: list, macros_dict: dict):
    """
    Perform value substitution.
    :param macro_val_tok: the macro to be substituted (list of tokens).
    :param params_dict: defined macros dictionary.
    :param va_args: defined macros dictionary.
    :param macros_dict: expand the macro repeatedly.
    :return: expanded value.
    """

    expansion_list = []
    va_args_list = []

    # TODO: handle trailing commas methods for variadic macros
    # TODO: handle concatenation and stringification

    # Compile va_args into a list of comma-separated arguments
    if va_args:
        va_args_list += va_args[0]

        i = 1
        while i < len(va_args):
            va_args_list.append(LexerToken((-1, -1), ',', False))
            va_args_list += va_args[i]
            i += 1

    for macro_tok in macro_val_tokens:
        if macro_tok in params_dict:
            expansion_list += params_dict[macro_tok]
        elif macro_tok == "__VA_ARGS__":
            expansion_list += va_args_list
        else:
            expansion_list.append(macro_tok)

    return expansion_list


# ##############################################################################
#                                      API
# ##############################################################################


def cpp_directive_do_sub_fun(macro_tok: list, macros_dict: dict, single_expansion: bool = False):
    """
    Perform macro substitution.
    :param macro_tok: the macro to be substituted (list of tokens).
    :param macros_dict: defined macros dictionary.
    :param single_expansion: expand the macro repeatedly.
    :return: expanded value.
    """

    # Validate macro exists in the global macro dictionary
    if macro_tok[0].val not in macros_dict:
        # TODO: return an error
        return []

    sub_macro = macros_dict[macro_tok[0].val]

    # Validate macro is function-like
    if not sub_macro.function_like:
        # TODO: return an error (consider calling cpp_directive_do_sub_obj)
        return []

    # Validate function like macro starts with a '(' character
    if macro_tok[1].val != '(':
        # TODO: return an error (consider calling cpp_directive_do_sub_obj)
        return []
    else:
        parentheses_count = 1
        i = 2

    parameters_lst = []  # Collect all the parameters passed to the macro
    parameters_count = 0

    expansion_queue = []  # Holds expanded value of the macro (tokens).
    va_args = None

    # Get all arguments into a list
    while i < len(macro_tok):
        if parentheses_count == 1:
            if macro_tok[i].val == ')':
                # Argument list is done!
                break
            elif macro_tok[i].val == ',':
                """
                Emtpy argument check can be done here. However, starting from the C99 standard (ISO/IEC 9899:1999),
                empty arguments (arguments consisting of no preprocessing tokens) in macro calls are allowed. This
                was also adopted in C++11 (ISO/IEC 14882:2011):
                
                    The number of arguments (including those arguments consisting of no preprocessing tokens)
                    shall equal the number of parameters in the macro definition of the function-like macro;
                    - From the ISO standard document.
                    
                We move argument index forward and move on.
                """
                parameters_count += 1
                i += 1
                continue

        if not parameters_lst or len(parameters_lst) <= parameters_count:
            parameters_lst.append([])

        # Adjust parentheses count
        if macro_tok[i].val == '(':
            parentheses_count += 1
        elif macro_tok[i].val == ')':
            parentheses_count -= 1

        parameters_lst[parameters_count].append(macro_tok[i])
        i += 1

    # We can't have fewer arguments than parameters:
    if sub_macro.params_num < len(parameters_lst):
        # Handle error
        pass

    sub_dict = dict(zip(sub_macro.params, parameters_lst))

    # If there are more arguments than parameters, it must be a variadic macro to be valid.
    if len(parameters_lst) > sub_macro.params_num:
        if not sub_macro.variadic:
            # TODO: handle error
            pass
        else:
            """
            If this is a variadic macro, with more arguments than parameters, we need to handle the extra arguments.
            All remaining arguments are stored in a sub-list.
            """
            va_args = parameters_lst[sub_macro.params_num:]

    # Do macro substitution

    sub_cycle = False if single_expansion else True
    expanded_macros_lst = []  # Holds expanded macros (names), to prevent substitution loops.

    # Do first (object-like) substitution
    expansion_queue += _do_dict_sub(sub_macro.val, sub_dict, va_args, macros_dict)
    expanded_macros_lst.append(macro_tok[0].val)  # Add the macro itself to the expanded macros list.

    # Do additional substitutions
    while sub_cycle:
        sub_cycle = False
        i = 0

        # Go over the entire expansion list
        while i < len(expansion_queue):
            i += 1

    return expansion_queue


def cpp_directive_do_sub_obj(macro_tok, macros_dict: dict, single_expansion: bool = False):
    """
    Perform macro substitution.
    :param macro_tok: the macro to be substituted (token of the macro name).
    :param macros_dict: defined macros dictionary.
    :param single_expansion: expand the macro repeatedly.
    :return: expanded value.
    """

    # Validate macro exists in the global macro dictionary
    if macro_tok.val not in macros_dict:
        # TODO: return an error
        return []

    # Get the macro from the global macro dictionary
    sub_macro = macros_dict[macro_tok.val]

    # Validate macro is object-like
    if sub_macro.function_like:
        # TODO: return an error (consider calling cpp_directive_do_sub_fun)
        return []

    expansion_queue = []  # Holds expanded value of the macro (tokens).
    expanded_macros_lst = []  # Holds expanded macros (names), to prevent substitution loops.
    sub_cycle = False if single_expansion else True

    expansion_queue += sub_macro.val  # Do first (object-like) substitution
    expanded_macros_lst.append(macro_tok.val)  # Add the macro itself to the expanded macros list.

    # Do additional substitutions
    while sub_cycle:
        sub_cycle = False
        i = 0

        # Go over the entire expansion list
        while i < len(expansion_queue):
            if (expansion_queue[i].identifier_compatible and (expansion_queue[i].val in macros_dict) and
                    (expansion_queue[i] not in expanded_macros_lst)):

                if macros_dict[expansion_queue[i].val].function_like:
                    # Expand a function-like macro
                    i += 1  # Temporary W/A
                else:
                    expanded_macros_lst.append(expansion_queue[i].val)
                    expansion_queue[i:i+1] = (
                        cpp_directive_do_sub_obj(expansion_queue[i], macros_dict, True))
                sub_cycle = True
            else:
                i += 1

    return expansion_queue


__all__ = ["cpp_directive_do_sub_obj", "cpp_directive_do_sub_fun"]
