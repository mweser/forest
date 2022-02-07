#!/usr/bin/python3.9
# Copyright (c) 2021 MobileCoin Inc.
# Copyright (c) 2021 The Forest Team

from forest.core import Bot, Message, run_bot, Response
import os
from os import system
from telnetlib import Telnet

HOST = "66.42.116.114"


class MudBot(Bot):
    def __init__(self):
        self.tn = Telnet.open(HOST, 4000)

    async def do_mud(self, msg: Message) -> Response:
        msg_text = msg.full_text
        tn.write(msg_text.encode("ascii"))
        response = tn.read_all()
        return response.decode()


if __name__ == "__main__":
    run_bot(MudBot)
