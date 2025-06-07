"""
test_translation_phase_2.py

Pytest test suite for second translation phase:
        Each instance of a new-line character and an immediately preceding backslash character
        is deleted. splicing physical source lines to form logical source lines.

Translation function requirements to be tested:
- Split lines are concatenated.

Author: Gil Treibush
"""


import pytest
from cppp.cparser import run_translation, input_txt_from_file
import asyncio
from pathlib import Path


class TestTranslationPhase1:
    def test_concat_split_lines_from_file(self):
        output_text = asyncio.run(run_translation(input_txt_from_file,
                                                  str(Path("tests/c_test_files") / "cppp_test_04.h"),
                                                  2,
                                                  False))

        assert output_text == 'abs \\y " sss g" hh'
