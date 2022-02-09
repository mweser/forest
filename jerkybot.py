from forest import utils
from forest.pdictng import aPersistDict
from forest.core import Message, Response, hide, QuestionBot, run_bot, get_uid
import os
from aiohttp import web

class JerkyBot(QuestionBot):
    def __init__(self):
        self.order_state = aPersistDict("order_state")
        self.pending_orders = aPersistDict("pending_orders")
        self.order_details = aPersistDict("order_details")
        self.order_price = aPersistDict("order_price")
        self.order_paid = aPersistDict("order_paid")
        super().__init__()

    async def do_order(self, msg: Message, order_id = get_uid()):
        size = (msg.arg1 or "").lower()
        jerky_type = (msg.arg2 or "").lower()
        quantity = ""
        valid_types = "orig spicy truffle not4gma insane punjabi garlic teriyaki".split()
        await self.send_message(msg.uuid, "Here's our menu!", attachments=["jerky/menu.png"])
        # only prompt if they don't give a type in their order
        if jerky_type and not self.ask_yesno_question(msg.uuid, "Would you like to place an order now?"):
            return "Okay, whenever you change your mind just say 'order'!"
        # get a UID to store info for this order
        while jerky_type not in valid_types:
            jerky_type = (await self.ask_freeform_question(msg.uuid, "What type would you like? (name from the above menu)")).lower()
            if jerky_type not in valid_types:
                await self.send_message(msg.uuid, "Sorry, please choose an option from the menu!")
        while size.replace("oz", "", 1) not in "2 6 12":
            size = await self.ask_freeform_question(msg.uuid, "What size would you like? (2oz, 6oz, 12oz)")
            size = size.replace("oz", "", 1)
        while not quantity.isnumeric():
            quantity = await self.ask_freeform_question(msg.uuid, "How many would you like to order? (As a number)")
        await self.pending_orders.set(msg.uuid, order_id)
        parameters = [quantity, size, jerky_type]
        price = {2:11, 6:30,
        await self.order_details.set(order_id, parameters)
        await self.order_state.set(order_id, "PENDING")
        await self.send_message(utils.get_secret("ADMIN"), f"Order {order_id} created!")
        return f"Ok, created your pending order {order_id} with these parameters: {parameters}]"

    async def payment_response(self, msg: Message, amount_pmob: int) -> Response:
        maybe_order = await self.pending_orders.get(msg.uuid, get_uid())
        price = None
        await self.order_paid.set(maybe_order, amount_pmob)
        if maybe_order:
            price = await self.order_prices.get(maybe_order)
            if amount_pmob >= price:
                await self.order_state.set(maybe_order, "PAID")
                await self.pending_orders.remove(msg.uuid)
                await self.send_message(utils.get_secret("ADMIN"), f"Order {maybe_order} paid!")
                return "Thanks for paying for your order"

if __name__ == "__main__":
    run_bot(JerkyBot)
