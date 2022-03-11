#!/usr/bin/python3.9
# Copyright (c) 2021 MobileCoin Inc.
# Copyright (c) 2021 The Forest Team

from forest.core import Bot, Message, run_bot
import os
from os import system
import urllib.request, urllib.parse
import json, time

key = ''

class AddressBot(Bot):
    async def do_address(self, msg: Message, api=key, delay=3) -> str:
        #msg.text = msg
        address = msg.text
        base = r"https://maps.googleapis.com/maps/api/geocode/json?"
        addP = "address=" + urllib.parse.quote_plus(address)
        GeoUrl = base + addP + "&key=" + api
        response = urllib.request.urlopen(GeoUrl)
        jsonRaw = response.read()
        jsonData = json.loads(jsonRaw)
        print(jsonData)
        resu = jsonData["results"][0]
        post_code = -1
        finList = [None]*4
        for i in resu["address_components"]:
            print(i)
            if i["types"][0] == "postal_code":
                post_code = i[
                    "long_name"
                ]
                finList = [
                    resu["formatted_address"],
                    resu["geometry"]["location"]["lat"],
                    resu["geometry"]["location"]["lng"],
                    post_code,
                ]
                return f"{finList}"

if __name__ == "__main__":
    run_bot(AddressBot)
