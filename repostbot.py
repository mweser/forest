#!/usr/bin/python3.9
# Copyright (c) 2021 MobileCoin Inc.
# Copyright (c) 2021 The Forest Team

import asyncio
from xmlrpc.client import Boolean

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

import random

class ReplayBot(Bot):
    def __init__(self):
        self.messages: dict[str, list[str]] = aPersistDict("messages")
        self.keyslist = []
        self.bj_p1_count = 0
        self.bj_p2_count = 0
        self.pval = 0
        self.dval = 0
        self.psuit = ""
        self.dsuit = ""
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
            
    def ulid_to_human(self, ulid: str) -> str:
        return get_ulid_time(ulid).strftime("%d-%b-%Y (%H:%M:%S.%f)")

    async def do_replay(self, _: Message) -> str:
        output_text = ""
        for val in await self.messages.keys():
            output_text += f"key: {val},\n    time: {self.ulid_to_human(val)},\n    val: {await self.messages.get(val)}\n"
        return output_text

    async def do_listing(self, _: Message) -> str:
        pass

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

    def deal_card(self):
        val = random.choice([1,2,3,4,5,6,7,8,9,10,11])
        suit = random.choice(["Spades", "Hearts", "Clubs", "Diamonds"])
        return val, suit

    def busted(self, counter):
        if counter > 21:
            return True
        else:
            return False
    
    async def do_hit(self, _: Message):
        return await self.blackjack_handler(hit=1)
    async def do_stand(self, _: Message):
        return await self.blackjack_handler(hit=0)

    async def blackjack_handler(self, hit: Boolean):
        if self.pval == 0:
            self.pval, self.psuit = self.deal_card()
        if self.dval == 0:
            self.dval, self.dsuit = self.deal_card()
        if hit:
            self.pval, self.psuit = self.deal_card()
            self.bj_p1_count += self.pval
        self.dval, self.dsuit = self.deal_card()
        self.bj_p2_count += self.dval
        print(self.bj_p1_count, self.bj_p2_count)
        #return pval, psuit, dval, dsuit, self.busted(self.bj_p1_count), self.busted(self.bj_p2_count)
        tmp1 = self.bj_p1_count
        tmp2 = self.bj_p2_count
        if self.busted(self.bj_p1_count):
            if self.busted(self.bj_p2_count):
                self.bjclear()
                return "Both busted."
            self.bjclear()
            return f"You busted with a total of {tmp1}."
        if self.busted(self.bj_p2_count):
            self.bjclear()
            return f"Dealer busted with a total of {tmp2}, you win."
        return f"Player has {self.pval} of {self.psuit}. Dealer has {self.dval} of {self.dsuit}. Player count is {self.bj_p1_count}. Dealer count is {self.bj_p2_count}."

    async def do_bjclear(self, _: Message):
        return self.bjclear()
    def bjclear(self):
        self.bj_p1_count = 0
        self.bj_p2_count = 0
        self.pval = 0
        self.dval = 0
        self.psuit = ""
        self.dsuit = ""
        return "Cleared the game."
if __name__ == "__main__":
    run_bot(ReplayBot)
    

