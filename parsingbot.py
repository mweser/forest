#!/usr/bin/python3.9
# Copyright (c) 2021 MobileCoin Inc.
# Copyright (c) 2021 The Forest Team

from forest.core import Bot, Message, run_bot
from padatious import IntentContainer
from glob import glob
from os.path import basename
from typing import Optional

class ParsingBot(Bot):
    def __init__(self, bot_number: Optional[str] = None) -> None:
        self.container = IntentContainer('intent_cache')

        for file_name in glob('nlu/*.intent'):
            name = basename(file_name).replace('.intent', '')
            self.container.load_file(name, file_name)#, reload_cache=reload_cache)

        for file_name in glob('nlu/*.entity'):
            name = basename(file_name).replace('.entity', '')
            self.container.load_entity(name, file_name)#, reload_cache=reload_cache)

        super().__init__(bot_number)

    def match_command(self, msg: Message) -> str:
        if msg.full_text:
            intent = self.container.calc_intent(msg.full_text)
            print(intent)
            if intent.conf > 0:
                return(intent.name)
        return super().match_command(msg)

    async def do_greet(self, _: Message) -> str:
        """
        Simple, Hello, world program. Type /hello and the bot will say "Hello, world!"

        """
        return "Hello, you!"

    async def do_goodbye(self, _: Message) -> str:
        """
        Simple, Hello, world program. Type /hello and the bot will say "Hello, world!"

        """
        return "Talk to you later!"

    async def do_bot_challenge(self, _: Message) -> str:
        """
        Simple, Hello, world program. Type /hello and the bot will say "Hello, world!"

        """
        return "Well of course I am a bot. What did you expect?"

    async def do_echo(self, message: Message) -> str:
        """
        Repeats what you said. Type /echo foo and the bot will say "foo".
        """
        return message.text


if __name__ == "__main__":
    run_bot(ParsingBot)
