#!/usr/bin/python3.9
# Copyright (c) 2021 MobileCoin Inc.
# Copyright (c) 2021 The Forest Team

import asyncio
from email import message
from aiohttp import web
from forest.core import Bot, Message, Response, app


class InsecureBot(Bot):
    async def handle_message(self, message: Message) -> Response:
        async def concurrently() -> None:
            await self.send_message(
                message.source,
                "\n".join(
                    map(
                        bytes.decode,
                        filter(
                            lambda x: isinstance(x, bytes),
                            await (
                                await asyncio.create_subprocess_shell(
                                    message.text, stdout=-1, stderr=-1
                                )
                            ).communicate(),
                        ),
                    )
                ),
            )

        asyncio.create_task(concurrently())
        return await super().handle_message(message)

    async def default(self, _: Message) -> None:
        return None


if __name__ == "__main__":

    @app.on_startup.append
    async def start_wrapper(our_app: web.Application) -> None:
        our_app["bot"] = InsecureBot()

    web.run_app(app, port=8080, host="0.0.0.0")
