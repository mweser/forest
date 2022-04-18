#!/usr/bin/python3.9
# Copyright (c) 2021 MobileCoin Inc.
# Copyright (c) 2021 The Forest Team
import aiohttp
from typing import Optional

from forest.core import Bot, Message, Response, run_bot


class FallbackBot(Bot):
    def __init__(
        self, bot_number: Optional[str] = None, phrases: Optional[list[str]] = None
    ) -> None:
        self.session = aiohttp.client.ClientSession()

        if not phrases:
            with open("phrases.txt", "r") as file:
                phrases = file.readlines()
        self.phrases = phrases
        print(self.phrases)
        super().__init__(bot_number)

    async def fetch(self, url, data) -> Response:
        async with self.session.post(url, json=data) as response:
            return await response.json()

    async def do_fallback(self, msg: Message) -> str:
        data = {"texts": self.phrases, "query": msg.text, "top_k": 1}
        result = await self.fetch("http://localhost:8080/search", data)
        return result


if __name__ == "__main__":
    run_bot(FallbackBot)
