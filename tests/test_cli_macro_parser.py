"""
test_text_input.py

Pytest test suite for parsing macros provided from the CLI.

CLI macros requirements to be tested:
- Parse CLI-style macros.
- Input functions shall be implemented as generators, returning a character per iteration.

Edge cases:
- empty string/file input.

Error handling testing:
- File does not exist test.

Author: Gil Treibush
"""


import pytest
import asyncio
from cppp.cparser import make_macro_from_cli


class TestCliMacros:
    def test_regular_cli_macros(self):
        input_macros = ["TM1 TEST_MACRO_BODY1", "TM2", "TM3 TEST_BODY3_P1 TEST_BODY3_P2 TEST_BODY3_P3"]

        output_macros = [("TM1", "[CLI][LexerToken((-1, -1), TEST_MACRO_BODY1, True)] (-1, -1)"),
                         ("TM2", "[CLI][LexerToken((-1, -1), 1, False)] (-1, -1)"),
                         ("TM3", "[CLI][LexerToken((-1, -1), TEST_BODY3_P1, True), LexerToken((-1, -1),  , False)," +
                          " LexerToken((-1, -1), TEST_BODY3_P2, True), LexerToken((-1, -1),  , False)," +
                          " LexerToken((-1, -1), TEST_BODY3_P3, True)] (-1, -1)")]

        macro_dict = {}

        # Run external macro parser
        for test_macro in input_macros:
            macro_ret = asyncio.run(make_macro_from_cli(test_macro, macro_dict))

        # Check results - number of defined macros
        assert len(macro_dict.keys()) == 3

        # Check results - values
        for test_res in output_macros:
            assert str(macro_dict[test_res[0]]) == test_res[1]

    def test_function_like_cli_macros(self):
        input_macros = ["TM0(   ) TEST_MACRO_BODY_0",
                        "TM1() TEST_MACRO_BODY_1",
                        "TM2(A)        TEST_MACRO_BODY_2",
                        "TM3(A, B) TEST_MACRO_BODY_3",
                        "TM4(A,B, C,   D,   E) TEST_MACRO_BODY_4"]

        output_macros = [("TM0", "[CLI][LexerToken((-1, -1), TEST_MACRO_BODY_0, True)] function like, (-1, -1)"),
                         ("TM1", "[CLI][LexerToken((-1, -1), TEST_MACRO_BODY_1, True)] function like, (-1, -1)"),
                         ("TM2", "[CLI][LexerToken((-1, -1), TEST_MACRO_BODY_2, True)]" +
                          "[LexerToken((-1, -1), A, True)] function like, (-1, -1)"),
                         ("TM3", "[CLI][LexerToken((-1, -1), TEST_MACRO_BODY_3, True)]" +
                          "[LexerToken((-1, -1), A, True), LexerToken((-1, -1), B, True)] function like, (-1, -1)"),
                         ("TM4", "[CLI][LexerToken((-1, -1), TEST_MACRO_BODY_4, True)]" +
                          "[LexerToken((-1, -1), A, True)," +
                          " LexerToken((-1, -1), B, True), LexerToken((-1, -1), C, True)," +
                          " LexerToken((-1, -1), D, True), LexerToken((-1, -1), E, True)] function like, (-1, -1)"),]

        macro_dict = {}

        # Run external macro parser
        for test_macro in input_macros:
            macro_ret = asyncio.run(make_macro_from_cli(test_macro, macro_dict))

        # Check results - number of defined macros
        assert len(macro_dict.keys()) == 5

        # Check results - values
        for test_res in output_macros:
            assert str(macro_dict[test_res[0]]) == test_res[1]

    def test_function_like_variadic_cli_macros(self):
        input_macros = ["TM0( ...) TEST_MACRO_BODY_0",
                        "TM1(...) TEST_MACRO_BODY_1",
                        "TM2( ...  )   TEST_MACRO_BODY_2",
                        "TM3(A, ... ) TEST_MACRO_BODY_3",
                        "TM4(A,B, C,   ...) TEST_MACRO_BODY_4"]

        output_macros = [("TM0", "[CLI][LexerToken((-1, -1), TEST_MACRO_BODY_0, True)]" +
                          "[LexerToken((-1, -1), ..., False)] variadic, function like, (-1, -1)"),
                         ("TM1", "[CLI][LexerToken((-1, -1), TEST_MACRO_BODY_1, True)]" +
                          "[LexerToken((-1, -1), ..., False)] variadic, function like, (-1, -1)"),
                         ("TM2", "[CLI][LexerToken((-1, -1), TEST_MACRO_BODY_2, True)]" +
                          "[LexerToken((-1, -1), ..., False)] variadic, function like, (-1, -1)"),
                         ("TM3", "[CLI][LexerToken((-1, -1), TEST_MACRO_BODY_3, True)]" +
                          "[LexerToken((-1, -1), A, True), LexerToken((-1, -1), ..., False)]" +
                          " variadic, function like, (-1, -1)"),
                         ("TM4", "[CLI][LexerToken((-1, -1), TEST_MACRO_BODY_4, True)]" +
                          "[LexerToken((-1, -1), A, True), LexerToken((-1, -1), B, True)," +
                          " LexerToken((-1, -1), C, True), LexerToken((-1, -1), ..., False)]" +
                          " variadic, function like, (-1, -1)"),]

        macro_dict = {}

        # Run external macro parser
        for test_macro in input_macros:
            macro_ret = asyncio.run(make_macro_from_cli(test_macro, macro_dict))

        # Check results - number of defined macros
        assert len(macro_dict.keys()) == 5

        # Check results - values
        for test_res in output_macros:
            assert str(macro_dict[test_res[0]]) == test_res[1]
