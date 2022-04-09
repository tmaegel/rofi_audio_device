#!/usr/bin/env python3
# coding=utf-8

from rofi_set_audio_out import PactlWrapper
from unittest.mock import patch

import pytest


@patch(
    "rofi_set_audio_out.PactlWrapper.run_cmd",
    return_value=("0\tcard0 \tinfo0", "", 0),
)
def test_list_cards_single(self):
    cards = PactlWrapper.list_cards()
    for i, card in enumerate(cards):
        assert card["id"] == str(i)
        assert card["name"] == f"card{i}"


@patch(
    "rofi_set_audio_out.PactlWrapper.run_cmd",
    return_value=("0\tcard0 \tinfo0\n1\tcard1\tinfo1", "", 0),
)
def test_list_cards_multiple(self):
    cards = PactlWrapper.list_cards()
    for i, card in enumerate(cards):
        assert card["id"] == str(i)
        assert card["name"] == f"card{i}"


@patch(
    "rofi_set_audio_out.PactlWrapper.run_cmd",
    return_value=("0\tcard0 \tinfo0\n", "", 0),
)
def test_list_cards_trailing_new_line(self):
    cards = PactlWrapper.list_cards()
    for i, card in enumerate(cards):
        assert card["id"] == str(i)
        assert card["name"] == f"card{i}"


def test_get_card_profiles():
    pass
