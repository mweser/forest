#!/usr/bin/python3.9
# Copyright (c) 2021 MobileCoin Inc.
# Copyright (c) 2021 The Forest Team

import asyncio

import mc_util
from prometheus_async import aio
from prometheus_async.aio import time
from prometheus_client import Summary
from forest.core import Bot, Message, run_bot, Response
from forest.pdictng import aPersistDict


class ReplayBot(Bot):
    def __init__(self):
        self.messages: dict[str, list[str]] = aPersistDict("messages")
        self.keyslist = []
        super().__init__()

    async def handle_message(self, message: Message) -> Response:
        if len(message.full_text): # full_text can be empty during receipts and typing indicators
            print("fulltext:", message.full_text)
            if message.source.startswith('+'):
                source = message.source[1:]
            else:
                source = message.source
            timestamp = message.timestamp
            message_key = str(source)+str(timestamp)
            self.keyslist.append(message_key)
            self.messages[message_key] = message.full_text
        return await super().handle_message(message)

    async def do_hello(self, _: Message) -> str:
        return "Hello, world!"

    async def do_replay(self, _: Message) -> str:
        d = self.messages.dict_
        # return await [(key, val) for val in self.messages.get(keys)]
        return d

if __name__ == "__main__":
    run_bot(ReplayBot)
    