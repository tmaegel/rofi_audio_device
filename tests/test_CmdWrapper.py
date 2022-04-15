#!/usr/bin/env python3
# coding=utf-8

from rofi_set_audio_out import CmdWrapper

import pytest


def test_run_cmd__success():
    cmd = ["echo", "-n", "test"]
    out, err, ret = CmdWrapper.run_cmd(cmd)
    assert out == "test"
    assert err is None
    assert ret == 0


def test_run_cmd__error_cmd_not_found():
    cmd = ["echo1", "test"]
    with pytest.raises(RuntimeError):
        CmdWrapper.run_cmd(cmd)


def test_run_cmd__error_invalid_arg():
    cmd = ["pwd", "--invalid-arg"]
    with pytest.raises(RuntimeError):
        CmdWrapper.run_cmd(cmd)


def test_run_cmd__error_cmd_failed():
    cmd = ["ls", "abc"]
    with pytest.raises(RuntimeError):
        CmdWrapper.run_cmd(cmd)
