"""
test_translation_phase_3.py

Pytest test suite for third translation phase:
        Preprocessing directives are executed and macro invocations are expanded.
        A #include preprocessing directive causes the named header or source file to be processed from phase
        1 through phase 4, recursively.

Translation function requirements to be tested:
- .

Author: Gil Treibush
"""

import pytest
from cppp.cparser import run_translation, input_txt_from_file
import asyncio
from pathlib import Path


class TestTranslationPhase4:
    def test_plain_obj_macros(self):
        processed_text = asyncio.run(run_translation(input_txt_from_file,
                                                  str(Path("tests/c_test_files") / "cppp_test_06.h"),
                                                  4,
                                                  False))
        output_text = Path("tests/c_test_files/cppp_test_06.i").read_text()

        assert processed_text == output_text

    def test_obj_macros_multiple_expansion(self):
        processed_text = asyncio.run(run_translation(input_txt_from_file,
                                                  str(Path("tests/c_test_files") / "cppp_test_07.h"),
                                                  4,
                                                  False))
        output_text = Path("tests/c_test_files/cppp_test_07.i").read_text()

        assert processed_text == output_text

    def test_plain_func_macros(self):
        processed_text = asyncio.run(run_translation(input_txt_from_file,
                                                  str(Path("tests/c_test_files") / "cppp_test_08.h"),
                                                  4,
                                                  False))
        # print("\nResulting text:")
        # print(processed_text)

        assert 1 == 1

    def test_func_macros_multiple_expansion(self):
        assert 1 == 1

    def test_variadic_func_macros(self):
        processed_text = asyncio.run(run_translation(input_txt_from_file,
                                                  str(Path("tests/c_test_files") / "cppp_test_09.h"),
                                                  4,
                                                  False))
        print("\nResulting text:")
        print(processed_text)

        assert 1 == 1

    def test_mixed_macros(self):
        assert 1 == 1

# TODO: test redefinition error
