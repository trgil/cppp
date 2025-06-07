"""
test_translation_phase_1.py

Pytest test suite for first translation phase:
        Physical source file characters are mapped to the source character set.
        Trigraph sequences, if enabled, are replaced by corresponding single-character internal representations.
        white-space characters are truncated.

Translation function requirements to be tested:
- The function shall truncate white spaces which are not inside comments or strings.
- When enabled, trigraph sequences shall be expanded according to standard mapping.
- When not enabled, trigraph sequences shall be ignored.
- All other characters, which are not in comments or strings, shall be passed into the output queue without change.
- Line number and character position shall be tracked for each character.
- The translation function shall interact correctly with the text input functions (from string and file).

Edge cases:
- String consistent of partial trigraph sequence.
- Empty string
- Empty file

Error handling testing:
- File does not exist test.

Author: Gil Treibush
"""


import pytest
from cppp.cparser import do_translation_phase_1, input_txt_from_string, input_txt_from_file
import asyncio
from pathlib import Path


async def cat_output_text(in_queue, out_text: list):
    lines = set()
    chars = set()

    while True:
        out_m = await in_queue.get()
        if not out_m:
            break

        char, (line_num, char_num) = out_m
        out_text.append(char)
        lines.add(line_num)
        chars.add(char_num)


async def do_run_phase_i(input_funct, input_text: str, trigraphs_enabled: bool):
    queue_phase_1 = asyncio.Queue(5)
    out_text = []

    phase_1_task = asyncio.create_task(
        do_translation_phase_1(input_funct, input_text, queue_phase_1, trigraphs_enabled))

    out_text_task = asyncio.create_task(cat_output_text(queue_phase_1, out_text))

    await asyncio.gather(phase_1_task, out_text_task)

    return "".join(out_text)


input_text_with_trigraphs = 'ab ??= ???! '
expected_text_1 =\
    'ab\n a b\n a b\n a b\n a\n b\n a "a    b           c"\n a // a    b         c\n a /* a    b         c */'


class TestTranslationPhase1:
    def test_white_space_truncation_from_string(self):
        input_text =\
            ('ab\n        a b\n        a  b\n        a          b\n        a\n\n\n' +
             '        b\n        a "a    b           c"\n        a // a    b         c\n' +
             '        a /* a    b         c */')

        output_text_no_trigraphs = asyncio.run(do_run_phase_i(input_txt_from_string, input_text, False))
        assert output_text_no_trigraphs == expected_text_1

    def test_white_space_truncation_from_file(self):
        output_text_no_trigraphs =(
            asyncio.run(do_run_phase_i(input_txt_from_file, str(Path("tests/c_test_files") / "cppp_test_03.h"),
                                       False)))
        assert output_text_no_trigraphs == expected_text_1

    def test_trigraphs_expansion(self):

        output_text_with_trigraphs =(
            asyncio.run(do_run_phase_i(input_txt_from_string, input_text_with_trigraphs, True)))
        assert output_text_with_trigraphs == 'ab # ?| '

    def test_trigraphs_expansion_negative(self):
        output_text_no_trigraphs =(
            asyncio.run(do_run_phase_i(input_txt_from_string, input_text_with_trigraphs, False)))
        assert output_text_no_trigraphs == input_text_with_trigraphs

    def test_empty_file(self):
        output_text_no_trigraphs =(
            asyncio.run(do_run_phase_i(input_txt_from_file, str(Path("tests/c_test_files") / "cppp_test_02.h"),
                                       False)))
        assert output_text_no_trigraphs == ""

    def test_invalid_file(self):
        with pytest.raises(FileNotFoundError) as exc_info:
            output_text_no_trigraphs = (
                asyncio.run(do_run_phase_i(input_txt_from_file, "does_not_exist", False)))

        assert "No such file or directory" in str(exc_info.value)
