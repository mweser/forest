# Copyright (c) 2021 MobileCoin Inc.
# Copyright (c) 2021 The Forest Team
import logging
from aiohttp import web
from forest.core import Bot, Message, Response, app
from forest import utils
import requests
import logging
import json


class FaerieBot(Bot):
    async def do_faeriefact(self, _: Message) -> str:
        "Learn a fact about faeries"

        return "faeries are very pretty and smell nice"

    async def do_ponytalk(self, message: Message) -> str:
        """
        make request to the Hugging Face model API
        """
        huggingface_token = utils.get_secret("HUGGINGFACE_TOKEN")
        api_endpoint = "https://api-inference.huggingface.co/models/transfaeries/Twilight-Sparkle-GPT"
        request_headers = {"Authorization": "Bearer {}".format(huggingface_token)}
        if not message.text:
            message.text = "hello twilight!"

        data = json.dumps(message.text)
        response = requests.request(
            "POST", api_endpoint, headers=request_headers, data=data
        )
        ret = json.loads(response.content.decode("utf-8"))
        if ret["generated_text"]:
            ret = ret["generated_text"]
        return ret

    async def default(self, _: Message) -> None:
        return None


if __name__ == "__main__":

    @app.on_startup.append
    async def start_wrapper(our_app: web.Application) -> None:
        our_app["bot"] = FaerieBot()

    web.run_app(app, port=8080, host="0.0.0.0")
