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

        if cmd := self.match_command(message):
            # invoke the function and return the response
            return await getattr(self, "do_" + cmd)(message)
        if message.text == "TERMINATE":
            return "signal session reset"

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
        return await self.default(message)
        #return await super().handle_message(message)

    async def do_hello(self, _: Message) -> str:
        return "Hello, world!"

    async def do_replay(self, _: Message) -> str:
        d = self.messages.dict_
        # return await [(key, val) for val in self.messages.get(keys)]
        return d

    async def delete_from_pdict(self, pdict, key):
        await pdict.remove(key)

    async def do_delete(self, _: Message) -> str:
        keys = await self.messages.keys()
        tasks = []
        for key in keys:
            task = await self.messages.remove(key)
            tasks.append(task)
        print(tasks)
        return "deleted log"

if __name__ == "__main__":
    run_bot(ReplayBot)

