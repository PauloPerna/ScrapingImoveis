import sys
import os
sys.path.append(os.getcwd())
print(sys.path)
# Testing Requests Function
from GetPropertiesData import OptionsRequest
import requests
RequestsSession = requests.Session()
headers = {
    "Accept" : r'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    "Accept-Encoding" : r'gzip, deflate, br',
    "Accept-Language" : r'en-US,en;q=0.5',
    "Alt-Used" : r'glue-api.vivareal.com',
    "Connection" : r'keep-alive',
    "Host" : r'glue-api.vivareal.com',
    "Sec-Fetch-Dest" : r'document',
    "Sec-Fetch-Mode" : r'navigate',
    "Sec-Fetch-Site" : r'cross-site',
    "Sec-GPC" : r'1',
    "TE" : r'trailers',
    "Upgrade-Insecure-Requests" : r'1',
    "User-Agent" : r'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:108.0) Gecko/20100101 Firefox/108.0'
}
response = OptionsRequest(RequestsSession, headers, r'https://glue-api.vivareal.com/v3/locations', verbose = True)
print(response.headers)
print(response.status_code)