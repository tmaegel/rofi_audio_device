#!/usr/bin/env python3
# coding=utf-8

from typing import Tuple, Union

import logging
import logging.handlers
import os
import re
import subprocess
import sys

logger = logging.getLogger(os.path.basename(__file__))
logger.setLevel(logging.DEBUG)
handler = logging.handlers.SysLogHandler(address="/dev/log")
logger.addHandler(handler)
handler.setFormatter(logging.Formatter("%(name)10s - %(levelname)8s - %(message)s"))


class CmdWrapper:
    @staticmethod
    def run_cmd(cmd: list[str]) -> Tuple[str, str, int]:
        proc = None
        try:
            with subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            ) as proc:
                out, err = proc.communicate()
        except subprocess.CalledProcessError as exc:
            logger.critical("Error while running command '%s': %s", cmd, exc)
            raise RuntimeError(f"Error while running command '{cmd}': {exc}") from exc
        except FileNotFoundError as exc:
            logger.critical("Error while running command '%s': %s", cmd, exc)
            raise RuntimeError(f"Error while running command '{cmd}': {exc}") from exc
        finally:
            if proc and proc.returncode > 0:
                raise RuntimeError(
                    f"Error while running command '{cmd}' [{proc.returncode}]"
                )
        if proc:
            return out.decode("utf-8"), err.decode("utf-8"), proc.returncode

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

        return cards

    @staticmethod
    def get_card_profiles(card_id: Union[int, str], output=True) -> list[str]:
        profiles = []
        card_found = False
        card_regex = re.compile("^Karte #(?P<card_id>[0-9])+")
        if output:
            profile_regex = re.compile("^(?P<profile>output:[a-zA-Z0-9-]+): .*$")
        else:
            profile_regex = re.compile("^(?P<profile>input:[a-zA-Z0-9-]+): .*$")
        out, _, _ = PactlWrapper.run_cmd(["pactl", "list", "cards"])
        for line in out.split("\n"):
            line = line.strip()
            if card_found is False:
                if target := re.search(card_regex, line):
                    if str(card_id) == target.groupdict()["card_id"]:
                        card_found = True
            else:
                if target := re.search(card_regex, line):
                    break
                if target := re.search(profile_regex, line):
                    profiles.append(target.groupdict()["profile"])

        return profiles

    @staticmethod
    def sef_default_sink(card_id: Union[int, str]) -> None:
        PactlWrapper.run_cmd(["pactl", "set-default-sink", str(card_id)])

    @staticmethod
    def set_card_profile(card_id: Union[int, str], card_profile: str) -> None:
        PactlWrapper.run_cmd(["pactl", "set-card-profile", str(card_id), card_profile])


class RofiWrapper:
    def __init__(self, prompt: str, no_custom: bool = True):
        self.configure("prompt", prompt)
        self.configure("no-custom", str(no_custom).lower())
        # self.configure("markup-rows", "true")

    @staticmethod
    def configure(key: str, value: str) -> None:
        print(f"\0{key}\x1f{value}")

    @staticmethod
    def output(entry: str, info: str) -> None:
        print(f"{entry}\0info\x1f{info}")

    @staticmethod
    def get_value() -> Union[str, None]:
        try:
            return sys.argv[1]
        except KeyError:
            logger.error("No argument detected.")

        return None

    @staticmethod
    def first_call() -> bool:
        rofi_retv = os.getenv("ROFI_RETV", None)
        if not rofi_retv:
            logger.error("ROFI_RETV is not set.")
            sys.exit(1)
        if int(rofi_retv) == 0:
            return True

        return False

    @staticmethod
    def get_info() -> dict[str, str]:
        info_dict = {}
        info = os.getenv("ROFI_INFO", None)
        if not info:
            logger.error("ROFI_INFO is not set.")
            sys.exit(1)
        info = info.split(",")
        if len(info) < 2:
            logger.error(
                "ROFI_INFO is not fully set. Expected attributes are card_id and type."
            )
            sys.exit(1)
        for attr in info:
            kv = attr.split("=", 1)
            key = kv[0]
            value = kv[1]
            if key == "card_id":
                info_dict[key] = int(value)
            elif key == "type":
                info_dict[key] = value
            else:
                logger.warning("Invalid attribute {key} in ROFI_INFO. Ignored.")

        return info_dict

    def output_cards(self, cards: list[dict[str, str]]) -> None:
        for card in cards:
            self.output(entry=card["name"], info=f"card_id={card['id']},type=card")

    def output_card_profiles(self, card_id: Union[int, str]) -> None:
        profiles = PactlWrapper.get_card_profiles(card_id)
        for profile in profiles:
            self.output(entry=profile, info=f"card_id={card_id},type=profile")


def main():
    try:
        CmdWrapper.run_cmd(["which", "pactl"])
    except RuntimeError:
        logger.error("pactl is not installed on your system.")
        sys.exit(1)

    rofi = RofiWrapper(prompt="output >")

    if rofi.first_call():
        logger.info("rofi was called for the first time.")
        cards = PactlWrapper.list_cards()
        if not cards:
            logger.warning("No devices/cards were found on the system.")
            sys.exit(0)
        if len(cards) > 1:
            rofi.output_cards(cards)
        else:
            rofi.output_card_profiles(cards[0]["id"])
    else:
        info = rofi.get_info()
        if info["type"] == "card":
            logger.info("rofi was called for the second time with the type 'card'.")
            PactlWrapper.sef_default_sink(info["card_id"])
            rofi.output_card_profiles(info["card_id"])
        elif info["type"] == "profile":
            logger.info(
                "rofi was called for the second/third time with the type 'profile'."
            )
            profile = rofi.get_value()
            if profile:
                PactlWrapper.set_card_profile(info["card_id"], profile)
            else:
                sys.exit(1)
        else:
            logger.warning(
                "rofi was called for the second time with the invalid type '%s'.",
                info["type"],
            )
            sys.exit(1)


if __name__ == "__main__":
    main()
