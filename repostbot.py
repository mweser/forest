#!/usr/bin/python3.9
# Copyright (c) 2021 MobileCoin Inc.
# Copyright (c) 2021 The Forest Team

from multiprocessing.connection import answer_challenge
import os
import os.path
import asyncio
import json
from tokenize import maybe
from urllib import response
import mc_util
from prometheus_async import aio
from prometheus_async.aio import time
from prometheus_client import Summary
from forest.core import Bot, Message, run_bot, Response, QuestionBot
from forest.pdictng import aPersistDict
import glob
from typing import Any, Dict, Optional
import time
import datetime

from ulid2 import generate_ulid_as_base32
from ulid2 import get_ulid_time, get_ulid_timestamp

#pwd = os.getcwd()



class RepostBot(QuestionBot):
    user_images: Dict[str, str] = {}

    def __init__(self):
        self.messages: dict[str, list[str]] = aPersistDict("messages")
        self.keyslist = []
        super().__init__()

    #from mobilepal 
    async def handle_message(self, message: Message) -> Response:
        if message.attachments and len(message.attachments):
            attachment_info = message.attachments[0]
            attachment_path = attachment_info.get("fileName")
            timestamp = attachment_info.get("uploadTimestamp")
            download_success = False
            download_path = "/dev/null"
            for _ in range(6):
                if attachment_path is None:
                    attachment_paths = glob.glob(
                        f"/tmp/unnamed_attachment_{timestamp}.*"
                    )
                    if len(attachment_paths) > 0:
                        attachment_path = attachment_paths.pop()
                        download_path = self.user_images[
                            message.source
                        ] = f"{attachment_path}"
                else:
                    download_path = self.user_images[
                        message.source
                        ] = f"/tmp/{attachment_path}"
                if not (
                    os.path.exists(download_path)
                    and os.path.getsize(download_path) == attachment_info.get("size", 1)
                ):
                    await asyncio.sleep(4)
                else:
                    download_success = True
                    break
                download_success = False
            if not message.arg0:
                return f"Saving this image to your Bot!"
        return await super().handle_message(message)

    #from mobilepal
    async def do_make(self, message: Message) -> Response:
        
        """Enter a dialog workflow where you can create a new post, delete your posts, or send a blast."""
        if not message.arg1:
            maybe_resp = message.arg1 = await self.ask_freeform_question(
                message.source,
                "Would you like to make a new post, delete your posts, or send a blast?"
            )
        else:
            maybe_resp = message.arg1
        if maybe_resp.lower() == "post":
            maybe_payload = message.full_text = await self.ask_freeform_question(
                message.source, "What content would you like to include in this post?"
            )
            if maybe_payload:
                    await self.do_post(message)
                    return "Made a post!"
        elif maybe_resp.lower() == "request":
            target = await self.ask_freeform_question(
                message.source,
                "Who should this pay, you or someone else?\nYou can reply 'me' or 'else'.",
            )
            if target.lower() == "me":
                message.arg1 = await self.get_address(message.source)
            else:
                message.arg1 = await self.ask_freeform_question(
                    message.source, "What MobileCoin address should this request pay?"
                )
            message.arg2 = await self.ask_freeform_question(
                message.source, "For how many MOB should this request be made?"
            )
            message.arg3 = await self.ask_freeform_question(
                message.source, "What memo would you like to use? ('None' for empty"
            )
            if message.arg3.lower() == "none":
                message.arg3 = ""
            _do_paywallet = await self.do_paywallet(message)
            return "You can copy and paste your payment result here to test it.\nIf you don't like your result, you can try again!"
        elif maybe_resp.lower().startswith("gift"):
            return await self.do_makegift(message)
        return "I'm sorry, I didn't get that."



    async def do_post(self, message: Message) -> Response:
        #if cmd := self.match_command(message):
        #    # invoke the function and return the response
        #    return await getattr(self, "do_" + cmd)(message)
        #if message.text == "TERMINATE":
        #    return "signal session reset"

        if len(message.full_text): # full_text can be empty during receipts and typing indicators
            if message.source.startswith('+'):
                source = message.source[1:]
            else:
                source = message.source
            timestamp = message.timestamp
            message_key = generate_ulid_as_base32(message.timestamp)
            self.humantime = get_ulid_time(message_key).strftime("%d-%b-%Y (%H:%M:%S.%f)")
            self.keyslist.append(message_key)
            await self.messages.set(message_key, message.full_text)

    async def delete_from_pdict(self, pdict, key):
        await pdict.remove(key)

    def ulid_to_human(self, ulid: str) -> str:
        return get_ulid_time(ulid).strftime("%d-%b-%Y (%H:%M:%S.%f)")

    async def do_replay(self, message: Message) -> str:
        output_text = ""
        for val in await self.messages.keys():
            output_text += f"{await self.messages.get(val)}\n"
        await self.send_message(msg="", attachments=["/tmp/image.jpg"], recipient=message.source)
        return output_text


    async def do_delete(self, _: Message) -> str:
        keys = await self.messages.keys()
        tasks = []
        for key in keys:
            task = await self.messages.remove(key)
            tasks.append(task)
        print(tasks)
        return "deleted log"

   
if __name__ == "__main__":
    run_bot(RepostBot)
