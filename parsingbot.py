#!/usr/bin/python3.9
# Copyright (c) 2021 MobileCoin Inc.
# Copyright (c) 2021 The Forest Team

from forest.core import Bot, Message, run_bot
from forest.semantic_dist import get_synonyms
from padatious import IntentContainer
from glob import glob
from os.path import basename
from typing import Optional

class ParsingBot(Bot):
    def __init__(self, bot_number: Optional[str] = None) -> None:
        self.commands = [
            name.removeprefix("do_") for name in dir(self) if name.startswith("do_")
        ]
        print(self.commands)        
        self.container = IntentContainer('intent_cache')
        no_syns = []
        for command in self.commands:
            syns = get_synonyms(command)
            if len(syns) > 0:
                self.container.add_intent(command, syns, reload_cache=True)
            else:
                no_syns.append(command)
        self.container.add_intent('fallback', no_syns, reload_cache=True)

        super().__init__(bot_number)

    def match_command(self, msg: Message) -> str:
        if msg.full_text:
            intent = self.container.calc_intent(msg.full_text)
            print(intent)
            if intent.conf > 0.5:
                return(intent.name)
        return super().match_command(msg)

    async def do_fallback(self, msg: Message) -> str:
        """
        Simple, Hello, world program. Type /hello and the bot will say "Hello, world!"

        """
        return super().match_command(msg)

    async def do_hello(self, _: Message) -> str:
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

    async def do_imagine(self, message: Message) -> str:
        """
        Repeats what you said. Type /echo foo and the bot will say "foo".
        """
        return('imagining ' + message.text)

    async def do_paint(self, message: Message) -> str:
        """
        Repeats what you said. Type /echo foo and the bot will say "foo".
        """
        return("painting " + message.text)

if __name__ == "__main__":
    run_bot(ParsingBot)
