#!/usr/bin/env python3
# coding=utf-8

from rofi_set_audio_out import PactlWrapper
from unittest.mock import patch


@patch(
    "rofi_set_audio_out.PactlWrapper.run_cmd",
    return_value=("0\tcard0 \tinfo0", "", 0),
)
def test_list_cards_single(mock):
    cards = PactlWrapper.list_cards()
    for i, card in enumerate(cards):
        assert card["id"] == str(i)
        assert card["name"] == f"card{i}"
    mock.assert_called_once()


@patch(
    "rofi_set_audio_out.PactlWrapper.run_cmd",
    return_value=("0\tcard0 \tinfo0\n1\tcard1\tinfo1", "", 0),
)
def test_list_cards_multiple(mock):
    cards = PactlWrapper.list_cards()
    for i, card in enumerate(cards):
        assert card["id"] == str(i)
        assert card["name"] == f"card{i}"
    mock.assert_called_once()


@patch(
    "rofi_set_audio_out.PactlWrapper.run_cmd",
    return_value=("0\tcard0 \tinfo0\n", "", 0),
)
def test_list_cards_trailing_new_line(mock):
    cards = PactlWrapper.list_cards()
    for i, card in enumerate(cards):
        assert card["id"] == str(i)
        assert card["name"] == f"card{i}"
    mock.assert_called_once()


@patch(
    "rofi_set_audio_out.PactlWrapper.run_cmd",
    return_value=(
        """
        Karte #0
        \tProfile:
        \t\tinput:analog-stereo-0: Description (Input)
        \t\toutput:analog-stereo-0: Description (Output)
        \t\toutput:analog-stereo+input:analog-stereo-0: Description (Output + Input)
        Karte #1
        \tProfile:
        \t\tinput:analog-stereo-1: Description (Input)
        \t\toutput:analog-stereo-1: Description (Output)
        \t\toutput:analog-stereo+input:analog-stereo-1: Description (Output + Input)
        """,
        "",
        0,
    ),
)
def test_get_card_profiles__output(mock):
    profiles = PactlWrapper.get_card_profiles(card_id=0)
    assert profiles[0] == "output:analog-stereo-0"
    profiles = PactlWrapper.get_card_profiles(card_id=1)
    assert profiles[0] == "output:analog-stereo-1"
    assert mock.call_count == 2


@patch(
    "rofi_set_audio_out.PactlWrapper.run_cmd",
    return_value=(
        """
        Karte #0
        \tProfile:
        \t\tinput:analog-stereo-0: Description (Input)
        \t\toutput:analog-stereo-0: Description (Output)
        \t\toutput:analog-stereo+input:analog-stereo-0: Description (Output + Input)
        Karte #1
        \tProfile:
        \t\tinput:analog-stereo-1: Description (Input)
        \t\toutput:analog-stereo-1: Description (Output)
        \t\toutput:analog-stereo+input:analog-stereo-1: Description (Output + Input)
        """,
        "",
        0,
    ),
)
def test_get_card_profiles__input(mock):
    profiles = PactlWrapper.get_card_profiles(card_id=0, output=False)
    assert profiles[0] == "input:analog-stereo-0"
    profiles = PactlWrapper.get_card_profiles(card_id=1, output=False)
    assert profiles[0] == "input:analog-stereo-1"
    assert mock.call_count == 2
