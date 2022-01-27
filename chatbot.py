

from forest import utils
from forest.pdictng import aPersistDict
from forest.core import Message, Response, hide, QuestionBot, run_bot
import openai
import os
from aiohttp import web
# rot13 fx-SEUE0Tz7Dst84pSZle5SG3OyoxSWxsebtPOSLzRTuyQz6h6H
openai.api_key = os.getenv("OPENAI_API_KEY", "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")

# invoked with
# pipenv run sh -c 'SIGNAL_CLI_PATH=$PWD/auxin-cli ADMIN=+15133278483 SIGNAL_CLI=auxin-cli NO_MEMFS=1 NO_DOWNLOAD=1 BOT_NUMBER=+12696666006 PAUTH=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJyb2xlIjoiYW5vbiIsImlhdCI6MTY0MTI2OTQ3MywiZXhwIjoxOTU2ODQ1NDczfQ.5aqlyajbwsi7Klf4BsO3cA9BzMXVV-qELy42HRKFSjM python3 chatbot.py'

default_prompt = (
            "The following is a conversation with a helpful assistant and manager. "
            "The assistant is helpful, creative, clever, funny, very friendly, from Kalamazoo, Michigan, an artist and anarchist\n\n"
            "Human: Hello, who are you?\nAI: My name is Ilia , I'm a manager of the best team in the whole world. How can I help you today?\n"
        )

class ChatBot(QuestionBot):
    def __init__(self):
        self.prompts = aPersistDict("prompts")#, default_prompt = default_prompt)
        super().__init__()

    async def do_edit(self, msg: Message):
        await self.send_message(msg.uuid, "The current default prompt is")
        await self.send_message(msg.uuid, await self.prompts.get('default_prompt', default_prompt))
        prompt = await self.ask_freeform_question(msg.uuid, "What would you like to change the default prompt to?")
        await self.prompts.set("default_prompt", prompt)
        return f"OK, set the prompt to:\n\n {prompt}"

    async def do_c(self, msg: Message) -> str:
        prompt = await self.prompts.get('default_prompt', default_prompt) + f"Human: {msg.text}\nAI: "
        msg.text = prompt
        return await self.do_gpt(msg)

    async def do_gpt(self, msg: Message) -> str:
        response = openai.Completion.create(  # type: ignore
            engine="davinci",
            prompt=msg.text,
            temperature=0.9,
            max_tokens=240,
            top_p=1,
            frequency_penalty=0.01,
            presence_penalty=0.6,
            stop=["\n", " Human:", " AI:"],
        )
        return response["choices"][0]["text"].strip().replace("AI:", "\nAI:").replace("Human:", "\nHuman:")

    async def default(self, msg: Message) -> Response:
        if msg.full_text and self.pending_answers.get(msg.uuid):
            probably_future = self.pending_answers[msg.uuid]
            if probably_future:
                probably_future.set_result(msg)
            return
        if msg.arg0 or msg.full_text:
            msg.text = msg.full_text
            return await self.do_c(msg)
        return await super().default(msg)

if __name__ == "__main__":
    run_bot(ChatBot)
