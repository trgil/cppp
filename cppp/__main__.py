"""
CPPP standalone-mode main entry point: __main__.py

Author:     Gil Treibush
Version:    1.0.0-alpha.1
License:    MIT License
"""

import argparse
from cppp.cppp import Cppp

def main():
    predefined_macros_cli = {}

    # Parse CLI arguments
    parser = argparse.ArgumentParser(description="Preprocess C/C++ code.")

    # Add the "file name" argument
    parser.add_argument(
        'inFilename',  # Positional "file" argument
        metavar='FILENAME',
        type=str,
        help="A valid C/C++ source code file, for processing."
    )
    parser.add_argument(
        '-f', '--file',  # Short and long "file" flag
        dest='inFilename',
        type=str,
        help="A valid C/C++ source code file, for processing."
    )
    parser.add_argument(
        '-o', '--out',  # Short and long "file" flag
        dest='outFilename',
        type=str,
        default='out.i',
        help="Output file name."
    )
    parser.add_argument(
        '-D',
        metavar='MACRO[=VALUE]',
        action='append',
        help="Pass CLI macro definitions as -DMACRO[=VALUE]"
    )

    args = parser.parse_args()

    if args.inFilename is None:
        parser.error("The valid filename is required. Passed as first positional argument or using -f/--file.")

    if args.D:
        for macro_df in args.D:
            if '=' not in macro_df:
                predefined_macros_cli[macro_df] = 1
            else:
                name, value = macro_df.split('=', 1)
                predefined_macros_cli[name] = int(value) if value.isdigit() else value

    TU = Cppp(args.inFilename, predefined_values=predefined_macros_cli)

    ### Debug Prints ###
    print(f"The file name is: {args.inFilename}")

    if args.D:
        print("Macros provided:")
        print(predefined_macros_cli)
    else:
        print("No macros provided.")

    TU.do_translation_phase_1()


if __name__ == "__main__":
    main()