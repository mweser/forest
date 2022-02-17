#!/usr/bin/python3.9
# Copyright (c) 2021 MobileCoin Inc.
# Copyright (c) 2021 The Forest Team

import functools
import logging
import os
from typing import Optional, cast


def filter_aiohttp(record: logging.LogRecord) -> bool:
    "Suppress verbose aiohttp logs"

    str_msg = str(getattr(record, "msg", ""))
    if "was destroyed but it is pending" in str_msg:
        return False
    if str_msg.startswith("task:") and str_msg.endswith(">"):
        return False
    return True


logger_class = logging.getLoggerClass()

logger = logging.getLogger()
logger.setLevel("DEBUG")
fmt = logging.Formatter("{levelname} {module}:{lineno}: {message}", style="{")
console_handler = logging.StreamHandler()
console_handler.setLevel(
    ((os.getenv("LOGLEVEL") or os.getenv("LOG_LEVEL")) or "INFO").upper()
)
console_handler.setFormatter(fmt)
console_handler.addFilter(filter_aiohttp)
logger.addHandler(console_handler)


@functools.cache  # don't load the same env more than once?
def load_secrets(env: Optional[str] = None, overwrite: bool = False) -> None:
    if not env:
        env = os.environ.get("ENV", "dev")
    try:
        logging.info("loading secrets from %s_secrets", env)
        secrets = [
            line.strip().split("=", 1)
            for line in open(f"{env}_secrets")
            if line and not line.startswith("#")
        ]
        can_be_a_dict = cast(list[tuple[str, str]], secrets)
        if overwrite:
            new_env = dict(can_be_a_dict)
        else:
            new_env = (
                dict(can_be_a_dict) | os.environ
            )  # mask loaded secrets with existing env
        os.environ.update(new_env)
    except FileNotFoundError:
        pass


def get_secret(key: str, env: Optional[str] = None) -> str:
    try:
        secret = os.environ[key]
    except KeyError:
        load_secrets(env)
        secret = os.environ.get(key) or ""  # fixme
    if secret.lower() in ("0", "false", "no"):
        return ""
    return secret


LOCAL = os.getenv("FLY_APP_NAME") is None

if get_secret("LOGFILES") or not LOCAL:
    handler = logging.FileHandler("debug.log")
    handler.setLevel("DEBUG")
    handler.setFormatter(fmt)
    handler.addFilter(filter_aiohttp)
    logger.addHandler(handler)
