from mc_util import b64_receipt_to_full_service_receipt

result = b64_receipt_to_full_service_receipt(
    'CiIKIBRB19Uul7i2HivDzB8fMCOLbgAlnTq+cRbJF2KUSEI0EiIKIDhFYUymnMjt47yuEDj8x5zjsk402vyUMIgHPObC4gORGI/BNyI3CiIKICag6rwwgjGQ6Nm9zMol/2WEzaaLW5l3l6MX7pm4VK5LEcW6zicsFO8jGgiZG6Ak6hTstg==')

result_str = str(result)
print(result_str.replace("'", "\""))
