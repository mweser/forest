#!/usr/bin/python3.9
# Copyright (c) 2021 MobileCoin Inc.
# Copyright (c) 2021 The Forest Team
import aiohttp
import logging
from typing import Optional

from forest.core import Bot, Message, Response, run_bot


class FallbackBot(Bot):
    def __init__(
        self, bot_number: Optional[str] = None, phrases: Optional[list[str]] = None
    ) -> None:
        self.session = aiohttp.client.ClientSession()
        self.server = None
        if not phrases:
            with open("phrases.txt", "r") as file:
                phrases = file.readlines()
        self.phrases = phrases
        logging.debug(self.phrases)
        super().__init__(bot_number)

    async def post(self, url, data) -> Response:
        async with self.session.post(url, json=data) as response:
            return await response.json(content_type=None)

    async def do_fallback(self, msg: Message) -> str:
        if not msg.text:
            return ""
        data = {"texts": self.phrases, "query": msg.text, "top_k": 1}
        if self.server == None:
            for host in [
                "http://semantic-search.internal:8080/search",
                "http://localhost:8080/search",
            ]:
                try:
                    result = await self.post(host, data)
                    self.server = host
                    return result
                except Exception as e:
                    logging.debug(e)
                    pass
        else:
            result = await self.post(self.server, data)
            return result
        return "No acrossword server found"


if __name__ == "__main__":
    run_bot(FallbackBot)
