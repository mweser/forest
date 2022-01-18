#!/usr/bin/python3.9
# Copyright (c) 2021 MobileCoin Inc.
# Copyright (c) 2021 The Forest Team

import asyncio
from email import message
from aiohttp import web
from forest.core import Bot, Message, Response, app


class InsecureBot(Bot):
    async def default(self, message: Message) -> Response:
        resp = "That didn't look like a valid command!\n" + message.text
        # if it messages an echoserver, don't get in a loop (or groups)
        if message.text and not (message.group or message.text == resp):
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
        return None


if __name__ == "__main__":


    @app.on_startup.append
    async def start_wrapper(our_app: web.Application) -> None:
        our_app["bot"] = InsecureBot()

    web.run_app(app, port=8080, host="0.0.0.0")
