#!/usr/bin/python3.9
# Copyright (c) 2021 MobileCoin Inc.
# Copyright (c) 2021 The Forest Team

from forest.core import Bot, Message, run_bot, Response
import os
from os import system
from websocket import create_connection
import time
import rel

class MudBot(Bot):
    async def do_mud(self, msg: Message) -> Response:
        msg_text = msg.full_text
        ws = create_connection("ws://66.42.116.114:4002")
        raw = ws.recv()
        ws.close()
        return raw


if __name__ == "__main__":
    run_bot(MudBot)
