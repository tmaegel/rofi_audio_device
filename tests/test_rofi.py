#!/usr/bin/env python3
# coding=utf-8

from rofi_set_audio_out import RofiWrapper
from unittest import mock

import os
import pytest


def mockenv(**envvars):
    return mock.patch.dict(os.environ, envvars)


def mockenvclear():
    return mock.patch.dict(os.environ, {}, clear=True)


@mockenv(ROFI_INFO="card_id=0,type=card")
def test_rofi_get_info__valid_1():
    info = RofiWrapper.get_info()
    assert info["card_id"] == 0
    assert info["type"] == "card"


@mockenv(ROFI_INFO="card_id=0,type=card,invalid=abc")
def test_rofi_get_info__valid_2():
    info = RofiWrapper.get_info()
    assert info["card_id"] == 0
    assert info["type"] == "card"


@mockenvclear()
def test_rofi_get_info__invalid_1():
    with pytest.raises(SystemExit) as wrapped_exit:
        _ = RofiWrapper.get_info()
    assert wrapped_exit.type == SystemExit
    assert wrapped_exit.value.code == 1


@mockenv(ROFI_INFO="card_id=0")
def test_rofi_get_info__invalid_2():
    with pytest.raises(SystemExit) as wrapped_exit:
        _ = RofiWrapper.get_info()
    assert wrapped_exit.type == SystemExit
    assert wrapped_exit.value.code == 1
