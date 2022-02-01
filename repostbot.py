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
from ulid2 import generate_ulid_as_base32
from ulid2 import get_ulid_time, get_ulid_timestamp
import datetime
from typing import Any, AsyncIterator, Callable, Optional, Type, Union


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
            if message.source.startswith('+'):
                source = message.source[1:]
            else:
                source = message.source
            timestamp = message.timestamp
            # message_key = str(source)+str(timestamp)
            message_key = generate_ulid_as_base32(message.timestamp/1000)
            self.humantime = get_ulid_time(message_key).strftime("%d-%b-%Y (%H:%M:%S.%f)")
            self.keyslist.append(message_key)
            self.messages[message_key] = message.full_text
            

    async def ulid_to_human(self, ulid):
        return get_ulid_time(ulid).strftime("%d-%b-%Y (%H:%M:%S.%f)")

    async def do_replay(self, _: Message) -> str:
        d = self.messages.dict_
        # return await [(key, val) for val in self.messages.get(keys)]
        output_text = ""
        for val in list(d.keys()):
            output_text += f"key: {val},\n    time: {await self.ulid_to_human(val)},\n    val: {d[val]}\n"
        return output_text # [d[item] for item in list(d.keys())[0:3]]

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
    

