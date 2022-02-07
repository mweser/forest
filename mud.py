#!/usr/bin/python3.9
# Copyright (c) 2021 MobileCoin Inc.
# Copyright (c) 2021 The Forest Team

from forest.core import Bot, Message, run_bot, Response
import os
from os import system
from telnetlib import Telnet

HOST = '66.42.116.114'
tn = Telnet(HOST)

class MudBot(Bot):
    async def do_something(self, msg: Message) -> Response:
        Telnet.open('66.42.116.114', '4000')
        response = tn.read_all()
        return response

if __name__ == "__main__":
    run_bot(MudBot)
