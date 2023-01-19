import sys
import os
sys.path.append(os.getcwd())
print(sys.path)
# Testing Requests Function
from GetPropertiesData import GetRequest
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
params = {
    'portal': 'VIVAREAL',
    'fields': 'neighborhood,city,account,condominium,poi,street',
    'includeFields': 'address.neighborhood,address.city,address.state,address.zone,address.locationId,address.point,url,advertiser.name,uriCategory.page,condominium.name,address.street',
    'size': 6,
    'q': "Ribeirão Preto, SP",
    'amenities': 'Amenity_NONE',
    'constructionStatus': 'ConstructionStatus_NONE',
    'listingType': 'USED',
    'businessType': 'SALE',
    'unitTypes': '',
    'usageTypes': '',
    'unitSubTypes': '',
    'unitTypesV3': '',
    '__vt': '',
}
url = 'https://glue-api.vivareal.com/v3/locations'
response = GetRequest(RequestsSession, headers, params, url, verbose = True)
print(response.headers)
print(response.status_code)
print(response.encoding)
print(response.content)
print(response.json())