#!/usr/bin/python3.9
# Copyright (c) 2021 MobileCoin Inc.
# Copyright (c) 2021 The Forest Team
# Need to run a small server that accepts POST requests with:
# query,
# search phrases,
# and webhook to reply to.
# Then run Ranker over the query and phrases
# returning a ranked list (perhaps cut off at a top_n)
from aiohttp import web
from acrossword import Ranker

ranker = Ranker()


async def no_get(request: web.Request) -> web.Response:
    raise web.HTTPFound(location="https://signal.org/")


async def search_handler(request: web.Request) -> web.Response:
    data = await request.json()
    texts = data["texts"]
    query = data["query"]
    top_k = 1
    if data.get("top_k"):
        top_k = data["top_k"]
    print(texts, query, top_k)
    result = await ranker.rank(
        texts=texts,
        query=query,
        top_k=top_k,
        model=ranker.default_model,
    )
    return web.json_response(result)


app = web.Application()

app.add_routes([web.get("/", no_get), web.post("/search", search_handler)])

if __name__ == "__main__":
    web.run_app(app, port=8080, host="::", access_log=None)
