from mc_util import b64_receipt_to_full_service_receipt, b58_wrapper_to_b64_public_address, \
    b64_public_address_to_b58_wrapper
import json


def print_unknown_field(label, data):
    print(label + " -> " + data.hex())


from_jsonrpc = 'CiIKIBRB19Uul7i2HivDzB8fMCOLbgAlnTq+cRbJF2KUSEI0EiIKIDhFYUymnMjt47yuEDj8x5zjsk402vyUMIgHPObC4gORGI/BNyI3CiIKICag6rwwgjGQ6Nm9zMol/2WEzaaLW5l3l6MX7pm4VK5LEcW6zicsFO8jGgiZG6Ak6hTstg=='

from_daemon = 'CiIKIAB58aXvLRFxPhSDLn9Nb62pYSY0RVWjrc2FAZ9KjWZFEiIKIKvYlgdD5dF5tAVP75ouJ8O9Jm0aNhJPHrRB7zwuonnjGPzCNyI3CiIKIPgL/5bJedIxqvPTGjipui9JT/gluJV1vcgaUnWDVN8lESfy0xGBFTTFGgg2tvL5+dWgbg=='
from_daemon7 = 'CiIKIGy5h/QK6oxSr5WDaeNO+lzyy1dxvKwyjiW0oUXNVI5+EiIKINtaaVH7hy9Wm+6LaIcToJBTfXWScL4XfZUrzwaYa/etGNKIOCI3CiIKILjen4FfDCzHLJbE6GqCA09jfTggt/5JvYiO1V5sS/k6EVLL8OWmLyPWGgj+H7Jkep6z0w=='
from_daemon10 = 'CiIKIMAiAnzOdeWzJhTNoh0EA23BvScK+FANZaGvZxGwv7EKEiIKIPGciqM1wIGE3L69cvoIqlhAMXxc/QPbzxaArV4vW4wBGNmIOCI3CiIKIGLwUYBnyEzl4ioOyFfyJQ4qkZtokrGlFtaza+yZDtRfEdM64yhvE0xkGgj8AhD/Y0N2jw=='
from_daemon11 = 'CiIKIOzIor8qVk4iylcMeR9jzDyJh/SM6cgKJ0C2Ze1PFLdkEiIKINTfpPwc6bd1GLCVVY8idvYD8JludNVkcRx5TzfSurZ4GP6IOCI3CiIKIBDIp7SNbw5KoapzyBqulhAMzJW2oRcIFkmj1E6NqiJAEXmgeTROU1LZGggSSmiR8zga8g=='

in_address = '6cXgXuMAntkv2Zgk3LJPJhBdWLdrT4FVwzvKsgkSM3bfffzzpyXqHyAweFwSYMArmiBuBVMRpQw5uRCztvtx5b75FdBe7Q9AYYjNkX3RnsShm445H4WWARpwmW5NpY3S4wA86UM3vvwkqxXrDFCJfDM4U7kgSP1VrUxhScnLymfXowpuEfrV9ncXmPdxUEHQVSHQia22e7oXcjGJzZ4Ed7EC6Uu8jWb8yHgqBVj1DtwVRC'
print("Converted address b58 -> b64:\n\t" + b58_wrapper_to_b64_public_address(in_address) + "\n\n")
print("\n\nConverted address b64 -> b58:\n\t" + b64_public_address_to_b58_wrapper(
    in_address) + "\n\n")

result = b64_receipt_to_full_service_receipt(from_daemon11)

result_str = str(result).replace("'", "\"")

result_json = json.loads(result_str)
print(json.dumps(result_json, indent=4))
