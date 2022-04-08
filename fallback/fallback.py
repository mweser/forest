#!/usr/bin/python3.9
# Copyright (c) 2021 MobileCoin Inc.
# Copyright (c) 2021 The Forest Team

from typing import Optional
from forest.core import Bot, Message, run_bot
from acrossword import Ranker


class FallbackBot(Bot):
    def __init__(
        self, bot_number: Optional[str] = None, phrases: Optional[list[str]] = None
    ) -> None:
        self.ranker = Ranker()
        if not phrases:
            with open("phrases.txt", "r") as file:
                phrases = file.readlines()
        self.phrases = phrases
        print(self.phrases)
        super().__init__(bot_number)

    async def do_fallback(self, msg: Message) -> str:
        top_result = await self.ranker.rank(
            texts=self.phrases,
            query=msg.full_text,
            top_k=1,
            model=self.ranker.default_model,
        )
        return top_result


if __name__ == "__main__":
    run_bot(FallbackBot)
