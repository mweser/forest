from mc_util import b64_receipt_to_full_service_receipt

def print_unknown_field(label, data):
    print(label + " -> " + data.hex())


result = b64_receipt_to_full_service_receipt(
    'CiIKIBRB19Uul7i2HivDzB8fMCOLbgAlnTq+cRbJF2KUSEI0EiIKIDhFYUymnMjt47yuEDj8x5zjsk402vyUMIgHPObC4gORGI/BNyI3CiIKICag6rwwgjGQ6Nm9zMol/2WEzaaLW5l3l6MX7pm4VK5LEcW6zicsFO8jGgiZG6Ak6hTstg==')

unknown1 = b'\x1a'
unknown2 = b'\x08\x99\x1b\xa0$\xea\x14\xec\xb6'
unknown_tuple = (b'\x1a', b'\x08\x99\x1b\xa0$\xea\x14\xec\xb6')

unknown_field = b'\x99\x1b\xa0$\xea\x14\xec\xb6'

result_str = str(result)
print(result_str.replace("'", "\""))

print_unknown_field('unknown1', unknown1)
print_unknown_field('unknown2', unknown2)
# print_unknown_field('unknown_tuple', unknown_tuple)
print_unknown_field('unknown_field', unknown_field)
