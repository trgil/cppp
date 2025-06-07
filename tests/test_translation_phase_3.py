"""
test_translation_phase_3.py

Pytest test suite for third translation phase:
        The source tile is decomposed into preprocessing tokens and sequences of
        white-space characters (including comments). Each comment is replaced by one space character.
        The source file is decomposed into preprocessing tokens and sequences of white-space characters.

Translation function requirements to be tested:
- C-Style comments are removed.
- C++-Style comments are removed.
- Code is tokenized properly.

Author: Gil Treibush
"""

import pytest
from cppp.cparser import (input_txt_from_file, input_txt_from_string, do_translation_phase_1,
                          do_translation_phase_2, do_translation_phase_3_remove_comments,
                          do_translation_phase_3_tokenize, cat_output_text)
import asyncio


async def do_run_phase_iii_i(input_funct, input_text: str, trigraphs_enabled: bool):
    queue_phase_1 = asyncio.Queue(5)
    queue_phase_2 = asyncio.Queue(5)
    queue_phase_3 = asyncio.Queue(5)
    out_text = []

    phase_1_task = asyncio.create_task(
        do_translation_phase_1(input_funct, input_text, queue_phase_1, trigraphs_enabled))
    phase_2_task = asyncio.create_task(
        do_translation_phase_2(queue_phase_1, queue_phase_2))
    phase_3_1_task = asyncio.create_task(
        do_translation_phase_3_remove_comments(queue_phase_2, queue_phase_3))

    out_text_task = asyncio.create_task(cat_output_text(queue_phase_3, out_text))

    await asyncio.gather(phase_1_task, phase_2_task, phase_3_1_task, out_text_task)

    return "".join(out_text)


class TestTranslationPhase3_1:
    def test_remove_cpp_style_comments(self):
        in_str = ' a\n b // xyz\n   c // /* //\n d / / // */\n  e'

        output_text = asyncio.run(do_run_phase_iii_i(input_txt_from_string,
                                                     in_str,
                                                     False))
        assert output_text == 'a\nb\nc\nd / /\ne'

    def test_remove_c_style_comments(self):
        in_str = 'a\n b /* xyz */ c\n c /*\n d / /* // a */\n  e'

        output_text = asyncio.run(do_run_phase_iii_i(input_txt_from_string, in_str, False))
        assert output_text == 'a\nb c\nc\ne'

    def test_do_not_remove_comments_in_strings(self):
        in_str = 'a\n b "/* xyz */ c\n" c /*\n d / /* // a */\n " // // /* " // bbb \ne'

        output_text = asyncio.run(do_run_phase_iii_i(input_txt_from_string, in_str, False))
        assert output_text == 'a\nb "/* xyz */ c\n" c\n" // // /* "\ne'


async def do_run_phase_iii_ii(input_funct, input_text: str, trigraphs_enabled: bool):
    queue_phase_1 = asyncio.Queue(5)
    queue_phase_2 = asyncio.Queue(5)
    queue_phase_3 = asyncio.Queue(5)
    queue_phase_4 = asyncio.Queue(5)
    out_text = []

    phase_1_task = asyncio.create_task(
        do_translation_phase_1(input_funct, input_text, queue_phase_1, trigraphs_enabled))
    phase_2_task = asyncio.create_task(
        do_translation_phase_2(queue_phase_1, queue_phase_2))
    phase_3_1_task = asyncio.create_task(
        do_translation_phase_3_remove_comments(queue_phase_2, queue_phase_3))
    phase_3_2_task = asyncio.create_task(
        do_translation_phase_3_tokenize(queue_phase_3, queue_phase_4))

    out_text_task = asyncio.create_task(cat_output_text(queue_phase_4, out_text))

    await asyncio.gather(phase_1_task, phase_2_task, phase_3_1_task, phase_3_2_task, out_text_task)

    return "".join(out_text)


class TestTranslationPhase3_2:
    def test_basic_tokenization_1(self):
        in_str = \
            ('int test_field_4;\n// A /* B */ // C \n/* // / *** * / */\n\n/*\n* /\n' +
             '// Comment 2\n*	/ \n*/ \nint test_field_5;')

        output_text = asyncio.run(do_run_phase_iii_ii(input_txt_from_string, in_str, False))

        assert output_text == 'int test_field_4;\nint test_field_5;'

    def test_basic_tokenization_2(self):
        in_str = 'int test_field_4;\n   // A /* B */ // C\n/* // / *** * / */'

        output_text = asyncio.run(do_run_phase_iii_ii(input_txt_from_string, in_str, False))

        assert output_text == 'int test_field_4;\n'

    def test_tokenization_empty_text(self):
        in_str = \
            ('// Comment, "String in a C++ style comment"\n' +
             '// Comment, "Unterminated string in a C++ style comment\n' +
             '/* Comment, "String in a C style comment" */\n' +
             '/* Comment, "Unterminated string in a C style comment */\n')

        output_text = asyncio.run(do_run_phase_iii_ii(input_txt_from_string, in_str, False))

        assert output_text == ''
