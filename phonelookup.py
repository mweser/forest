import os
from twilio.rest import Client

api_key = os.environ['TWILIO_ACCOUNT_SID']
secret = os.environ['TWILIO_AUTH_TOKEN']
client = Client(api_key, secret)
num = None


class wLookup(Client):
    def do_lookup():
        phone_number = client.lookups.v1.phone_numbers(num).fetch(type=["carrier"])
        resp = f"{num}\n" + str(phone_number.carrier)
        return resp
