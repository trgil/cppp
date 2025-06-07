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
from cppp.cparser import run_translation, input_txt_from_file, input_txt_from_string
import asyncio
from pathlib import Path


class TestTranslationPhase4:
    def test_defined_macros(self):
        output_text = asyncio.run(run_translation(input_txt_from_file,
                                                  str(Path("tests/c_test_files") / "cppp_test_05.h"),
                                                  4,
                                                  False))

        assert output_text == 'int main(void)\n{\nreturn 0;\n}'
