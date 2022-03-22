#!/usr/bin/python3.9
# Copyright (c) 2021 MobileCoin Inc.
# Copyright (c) 2021 The Forest Team

import json
from re import template
from forest import utils
from forest.core import Bot, Message, Response, run_bot
from personate.core.agents import Agent

# from acrossword import Document, DocumentCollection, Ranker

# The bot class imports my new simple Agent class from Personate.
# It should set up a Frame, Ranker, Filter, knowledge and examples
# It should set Activators, (as synonyms of a do_activate function?)
# Can we set a Face here as well? (avatar, profile name etc)
# Can we build a Memory here? from pdictng?


class Imposter(Bot):
    def __init__(self) -> None:
        # Accept a JSON config file in the same format as Personate.
        # Can be generated at https://ckoshka.github.io/personate/
        config_file = utils.get_secret("CONFIG_FILE")
        self.agent = Agent.from_json(config_file)
        super().__init__()

    def match_command(self, msg: Message) -> str:
        if not msg.arg0:
            return ""
        # Look for direct match before checking activators
        if hasattr(self, "do_" + msg.arg0):
            return msg.arg0
        # If we're not in a group we can just respond to the message
        if msg.full_text and not msg.group:
            return "respond"
        # Try activators
        if any(o in msg.full_text for o in self.agent.activators):
            return "respond"
        # Pass the buck
        return super().match_command(msg)

    async def do_respond(self, msg: Message) -> str:
        return await self.agent.generate_agent_response(msg.full_text)


if __name__ == "__main__":
    run_bot(Imposter)
