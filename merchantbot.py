import logging
import asyncio
import mc_util
from forest import utils
from forest.core import Message, run_bot, QuestionBot, Response
from forest.pdictng import aPersistDict, aPersistDictOfLists

class TalkBack(QuestionBot):
    def __init__(self) -> None:
        self.addresses = aPersistDict("addresses")
        self.cart_items = aPersistDictOfLists("cart_items")
        super().__init__()

    async def do_get_address(self) -> None:
        await self.addresses.get(obj)

    async def do_add_item(self, msg: Message) -> None:
        user = msg.uuid
        await self.cart_items.extend(user, {"item": msg.text, "price": 10, "quantity": 1})

    async def do_dump(self, msg: Message) -> None:
        out = []
        for item in await self.cart_items.get(msg.uuid):
            out.append(item)
        return out

    async def do_keys(self, msg: Message) -> None:
        return self.cart_items.dict_.keys()

    async def do_cart(self, msg: Message) -> None:
        out = []
    
    async def do_clear(self, msg: Message) -> None:
        await self.cart_items.pop(msg.uuid)






    # async def get_address_dict(self, msg: Message) -> dict:
    #     addr_data = await self.ask_address_question_(
    #         msg.uuid, require_confirmation=True
    #     )
    #     if not addr_data:
    #         return {}
    #     bits = {
    #         field: component["short_name"]
    #         for component in addr_data["address_components"]
    #         for field in component["types"]
    #     }
    #     return {
    #         "addressLine1": bits["street_number"] + " " + bits["route"],
    #         "addressLine2": bits["locality"],
    #         "stateCode": bits["administrative_area_level_1"],
    #         "city": bits["locality"],
    #         "postcode": bits["postal_code"],
    #     }

if __name__ == "__main__":
    run_bot(TalkBack)