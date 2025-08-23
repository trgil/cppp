"""
CPPP standalone-mode main entry point: __main__.py

Author:     Gil Treibush
Version:    1.0.0-alpha.1
License:    MIT License
"""

import argparse
import sys
import re
import os
import platform
from cppp.cppp import Cppp, VERSION


# Extract & store all define/undefine CLI parameters
def extract_macro_ops(argv):
    macro_ops = []

    for i, arg in enumerate(argv):
        try:
            if arg.startswith('-D'):
                value = arg[2:] if len(arg) > 2 else argv[i + 1]
                macro_ops.append(('define', value))
            elif arg.startswith('-U'):
                value = arg[2:] if len(arg) > 2 else argv[i + 1]
                macro_ops.append(('undefine', value))
        except IndexError:
            print(f"Missing macro value after {arg}.")
            # TODO: add error handle

    return macro_ops


# Remove comments from CLI parameters
def strip_comments(s):
    # Remove C++-style comments
    s = re.sub(r'//.*?(?=\n|$)', '', s)
    # Remove C-style block comments (greedy match)
    s = re.sub(r'/\*.*?\*/', '', s, flags=re.DOTALL)
    return s


# Quick, valid macro name check
def is_valid_macro_name(name):
    return re.match(r'^[A-Za-z_]\w*$', name)


# Process all define/undefine CLI options
def process_cli_macros(macro_ops):
    macro_table = {}

    for op, raw in macro_ops:
        raw = raw.strip()

        # Drop illegal line splicing
        if '\\\n' in raw:
            print(f"Dropping macro due to illegal line splice: {raw}")
            continue

        # Strip comments
        clean = strip_comments(raw)

        # Extract macro name before formatting
        if '=' in clean:
            name = clean.split('=', 1)[0].strip()
            formatted = clean.replace('=', ' ', 1)
        else:
            name = clean.strip()
            formatted = name

        if op == 'undefine':
            if name in macro_table:
                del macro_table[name]
            continue

        macro_table[name] = formatted

    return list(macro_table.values())


# Get include paths from standard system env variables
def get_env_include_paths():
    paths = []
    for var in ['CPATH', 'C_INCLUDE_PATH', 'CPLUS_INCLUDE_PATH', 'INCLUDE']:
        if var in os.environ:
            env_paths = os.environ[var].split(os.pathsep)
            paths.extend(p.strip() for p in env_paths if p.strip())
    return paths


# Get standard system include paths (OS specific)
def get_system_include_paths():
    system = platform.system()
    if system == 'Linux':
        return ['/usr/include', '/usr/local/include']
    elif system == 'Darwin':  # macOS
        return [
            '/Library/Developer/CommandLineTools/usr/include',
            '/usr/include',
            '/usr/local/include'
        ]
    elif system == 'Windows':
        return [
            r'C:\Program Files (x86)\Microsoft SDKs\Include',
            r'C:\MinGW\include',
            r'C:\msys64\usr\include'
        ]
    else:
        return []


# Collect & organize all include paths
def resolve_include_paths(cli_I_flags, use_env=True, use_system=True):
    include_paths = []

    # CLI flags
    include_paths.extend(cli_I_flags)

    # Environment variables
    if use_env:
        include_paths.extend(get_env_include_paths())

    # System defaults
    if use_system:
        include_paths.extend(get_system_include_paths())

    # Normalize and remove duplicates
    seen = set()
    normalized = []
    for path in include_paths:
        abs_path = os.path.abspath(path)
        if abs_path not in seen:
            seen.add(abs_path)
            normalized.append(abs_path)

    return normalized


# Extract & store all include paths CLI parameters
def extract_include_paths(argv):
    include_paths = []

    for i, arg in enumerate(argv):
        if arg.startswith('-I'):
            value = arg[2:] if len(arg) > 2 else argv[i + 1]
            include_paths.append(value)

    return include_paths

def main():
    """
    Run CPPP directly according to CLI parameters.

    Handle macros passed from the command line (compatible with GCC conventions):

    '-D name' - Predefine name as a macro, with definition 1.

    '-D name=definition' -  The contents of definition are tokenized and processed as if they
    appeared during translation phase three in a ‘#define’ directive. In particular, the definition
    is truncated by embedded newline characters.

    If you are invoking the preprocessor from a shell
    or shell-like program you may need to use the shell’s quoting syntax to protect characters such
    as spaces that have a meaning in the shell syntax.

    If you wish to define a function-like macro on the command line, write its argument list with
    surrounding parentheses before the equals sign (if any). Parentheses are meaningful to most
    shells, so you should quote the option. With sh and csh,-D'name(args...)=definition' works.

    -D and-U options are processed in the order they are given on the command line. All-imacros
    file and-include file options are processed after all-D and-U options.

    '-U name' - Cancel any previous definition of name, either built in or provided with a '-D' option.

        - From the GCC documentation.
    """

    """
    Since GCC-style "-U" & "-D" flags are order-sensitive and can appear multiple times it's necessary to intercept
    them directly from sys.argv before they are processed with argparse.
    """
    macro_table = process_cli_macros(extract_macro_ops(sys.argv))

    """
    Since GCC-style "-I" flags are order-sensitive it's necessary to intercept them directly from sys.argv before they
    are processed with argparse.
    """
    include_paths = resolve_include_paths(extract_include_paths(sys.argv))

    # Parse CLI arguments
    parser = argparse.ArgumentParser(
        description="CPPP: C/C++ Python Preprocessor",
        epilog="Note: compling with GCC conventions, -D and -U flags are processed in the order of appearance."
    )

    # Input file - positional
    parser.add_argument(
        'input_file',
        type=str,
        nargs='?',  # Optional argument
        metavar='FILENAME',
        help="C/C++ source file to process (can also be passed via: -f/-i/--file)"
    )
    # Input file - via flag
    parser.add_argument(
        '-f', '--file', '-i',
        dest='input_file_flag',
        type=str,
        required=False,
        metavar='FILENAME',
        help='C/C++ source file to process (can also be passed as first positional argument)'
    )
    # Output file
    parser.add_argument(
        '-o', '--out',
        dest='output_file',
        type=str,
        required=False,
        metavar='FILENAME',
        help='Output file (defaults to <input filename>.i)'
    )
    # Macro definitions - for documentation purposes only!
    parser.add_argument(
        '-D',
        metavar='MACRO[=VALUE]',
        help='Pass CLI macro definitions (e.g. -DDEBUG or -DVERSION=2)'
    )
    # Macro undefinitions - for documentation purposes only!
    parser.add_argument(
        '-U',
        metavar='MACRO',
        help='Pass CLI macro to undefine (e.g. -UOLD_MACRO)'
    )
    # Include path - for documentation purposes only!
    parser.add_argument(
        '-I',
        metavar='PATH',
        help='Pass include directory path (e.g. -I/usr/lib/)'
    )
    # Version
    parser.add_argument(
        '-v', '--version',
        action='store_true',
        help='Show version and exit'
    )

    args = parser.parse_args()

    # Handle version
    if args.version:
        print(f"CPPP version: {VERSION}")
        sys.exit(0)

    # Get input file name
    # TODO: add option to input code from sys.stdin (e.g. "sys.stdin.read()" as input file)
    input_file = args.input_file_flag or args.input_file
    if not input_file:
        parser.error("No input file provided. As first positional argument or -f/-i/--file.")

    # Derive an output-file name
    base_name = os.path.splitext(input_file)[0]
    output_file = args.output_file or (base_name + '.i')

    # if args.D:
    #     for macro_df in args.D:
    #         if '=' not in macro_df:
    #             # Compatible with GCC CLI flag: '-D name - Predefine name as a macro, with definition 1'.
    #             predefined_macros_cli[macro_df] = 1
    #         else:
    #             name, value = macro_df.split('=', 1)
    #             predefined_macros_cli[name] = int(value) if value.isdigit() else value
    #
    # TU = Cppp(args.inFilename, predefined_values=predefined_macros_cli)
    #
    # ### Debug Prints ###
    # print(f"The file name is: {args.inFilename}")
    #
    # if args.D:
    #     print("Macros provided:")
    #     print(predefined_macros_cli)
    # else:
    #     print("No macros provided.")
    #
    # TU.do_tokenize()


if __name__ == "__main__":
    main()