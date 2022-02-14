#!/usr/bin/python3.9
# Copyright (c) 2021 MobileCoin Inc.
# Copyright (c) 2021 The Forest Team

from forest.core import Bot, Message, Response, run_bot

gid = None
class RelayBot(Bot):
    async def default(self, msg: Message) -> Response:
        if msg.full_text and not msg.group:
            await self.send_message(None, msg=msg.full_text, group=gid)

    async def do_list(self, msg: Message) -> Response:
        #list groups the bot is in

    async def do_add(self, msg: Message) -> Response:
        #add group for the bot to relay messages to.
        msg.text = gid


if __name__ == "__main__":
    run_bot(RelayBot)
