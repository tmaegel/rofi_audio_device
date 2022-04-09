#!/usr/bin/env python3
# coding=utf-8

from typing import Tuple

import logging
import logging.handlers
import os
import re
import subprocess
import sys

APP_NAME = "rofi_set_audio_out"
PROMPT = "output >"

logger = logging.getLogger(APP_NAME)
logger.setLevel(logging.DEBUG)
handler = logging.handlers.SysLogHandler(address="/dev/log")
logger.addHandler(handler)
handler.setFormatter(logging.Formatter("%(name)10s - %(levelname)8s - %(message)s"))


class CmdWrapper:
    @staticmethod
    def run_cmd(cmd: list[str]) -> Tuple[str, str, int]:
        proc = None
        try:
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = proc.communicate()
        except subprocess.CalledProcessError as exc:
            logger.critical(f"Error while running command '{cmd}': {exc}")
            raise RuntimeError(f"Error while running command '{cmd}': {exc}")
        except FileNotFoundError as exc:
            logger.critical(f"Error while running command '{cmd}': {exc}")
            raise RuntimeError(f"Error while running command '{cmd}': {exc}")
        finally:
            if proc and proc.returncode > 0:
                raise RuntimeError(
                    f"Error while running command '{cmd}' [{proc.returncode}]"
                )

        if proc:
            return out.decode("utf-8"), err.decode("utf-8"), proc.returncode
        else:
            return out.decode("utf-8"), err.decode("utf-8"), -1


class PactlWrapper(CmdWrapper):
    @staticmethod
    def list_cards() -> list[dict[str, str]]:
        cards = []
        out, _, _ = PactlWrapper.run_cmd(["pactl", "list", "short", "cards"])
        for card in out.split("\n"):
            info = card.split("\t")
            if len(info) >= 2:
                cards.append({"id": info[0].strip(), "name": info[1].strip()})
        logger.debug(f"list_cards(): {cards}")
        return cards

    @staticmethod
    def get_card_profiles(card_id: int, output=True) -> list[str]:
        profiles = []
        card_begin = False
        card_regex = re.compile("^Karte #(?P<card_id>[0-9])+")
        if output:
            profile_regex = re.compile("^(?P<profile>output:[a-zA-Z0-9-]+): .*$")
        else:
            profile_regex = re.compile("^input:.*: .*$")
        out, _, _ = PactlWrapper.run_cmd(["pactl", "list", "cards"])
        for line in out.split("\n"):
            if card_begin is False:
                if target := re.search(card_regex, line):
                    if str(card_id) == target.groupdict()["card_id"]:
                        card_begin = True
            else:
                if target := re.search(card_regex, line):
                    break
                if target := re.search(profile_regex, line.strip()):
                    profiles.append(target.groupdict()["profile"])

        logger.debug(f"list_card_profiles(): {profiles}")
        return profiles

    @staticmethod
    def sef_default_sink(card_id: int) -> None:
        PactlWrapper.run_cmd(["pactl", "set-default-sink", str(card_id)])


def main():
    try:
        CmdWrapper.run_cmd(["which", "pactl"])
    except RuntimeError:
        logger.error("pactl is not installed on your system.")
        sys.exit(1)

    print("\0prompt\x1f{}".format(PROMPT))
    rofi_retv = int(os.getenv("ROFI_RETV"))

    profiles = PactlWrapper.get_card_profiles(card_id=0)
    logger.info(profiles)

    if rofi_retv == 0:
        print("a")
        print("a")
        print("a")
    elif rofi_retv == 1:
        print("1")
        print("1")
        print("1")


if __name__ == "__main__":
    main()
