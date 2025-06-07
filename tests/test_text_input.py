"""
test_text_input.py

Pytest test suite for code input functions (input form file & input from text).

Input functions requirements to be tested:
- Input code shall be red from a given file/string.
- Input functions shall be implemented as generators, returning a character per iteration.
- Newline sequences/characters shall be replaced with a single '\n'.
- Non-supported characters shall be skipped.
-- Non-supported characters shall be tracked and their number shall be reported when the generator finishes.
- Line number and character position shall be tracked for each character.

Edge cases:
- empty string/file input.

Error handling testing:
- File does not exist test.

Author: Gil Treibush
"""


import pytest
from cppp.cparser import input_txt_from_file, input_txt_from_string
from pathlib import Path


module_file = "cppp_test_01"


@pytest.fixture(scope="module")
def get_file_text():
    src_text_file = str(Path("tests/c_test_files") / (module_file + ".h"))
    result_file = str(Path("tests/c_test_files") / (module_file + ".i"))

    file_text = open(result_file)
    output_text = file_text.read()
    file_text.close()
    return src_text_file, output_text


class TestInputFromText:
    def test_basic_text_input(self, get_file_text):
        src_text_file, output_text = get_file_text

        src_test_file = open(src_text_file, "rb")
        example_text = src_test_file.read()
        src_test_file.close()

        result_text = ""
        lines = set()
        chars = set()

        gen = input_txt_from_string(example_text.decode("utf-8", errors="replace"))

        try:
            while True:
                char, line_num, char_num = next(gen)
                # NOTE: since example_text is a byte array, it must be converted to a utf-8 string with invalid
                # characters being replaced.
                result_text += char
                lines.add(line_num)
                chars.add(char_num)

        except StopIteration as e:
            invalid_count = e.value

        assert result_text == output_text
        assert lines == {1, 2, 3}
        assert chars == {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13}
        assert invalid_count == 3

    def test_empty_string(self):
        example_text = ""

        result_text = ""
        lines = set()
        chars = set()
        for char, line_num, char_num in input_txt_from_string(example_text):
            result_text += char
            lines.add(line_num)
            chars.add(char_num)

            assert result_text == ""
            assert lines == {}
            assert chars == {}


class TestInputFromFile:
    def test_basic_text_input(self, get_file_text):
        src_text_file, output_text = get_file_text

        result_text = ""
        lines = set()
        chars = set()

        gen = input_txt_from_file(src_text_file)

        try:
            while True:
                char, line_num, char_num = next(gen)
                result_text += char
                lines.add(line_num)
                chars.add(char_num)

        except StopIteration as e:
            invalid_count = e.value

        assert result_text == output_text
        assert lines == {1, 2, 3}
        assert chars == {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13}
        assert invalid_count == 3

    def test_invalid_file(self):
        with pytest.raises(FileNotFoundError) as exc_info:
            for char, line_num, char_num in input_txt_from_file("does_not_exist"):
                pass

        assert "No such file or directory" in str(exc_info.value)

    def test_empty_file(self):
        empty_file = str(Path("tests/c_test_files") / ("cppp_test_02.h"))

        result_text = ""
        lines = set()
        chars = set()
        for char, line_num, char_num in input_txt_from_file(empty_file):
            result_text += char
            lines.add(line_num)
            chars.add(char_num)

            assert result_text == ""
            assert lines == {}
            assert chars == {}
