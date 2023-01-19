#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 13 10:33:00 2023

@author: perna
"""
import requests
import urllib
import pandas as pd
from datetime import datetime, timedelta
import re

# stringAddress = "City, State - Neighborhood"
# stringAddress = "Ribeirão Preto, SP"
# stringAddress = "São José dos Campos, SP - Jardim Aquários"
def GetPropertiesData(stringAddress, size = 250, verbose = False):
    Neighborhood = " - " in stringAddress
    RequestsSession = requests.Session()
    AddressDictionary = GetAddressDictionary(RequestsSession, stringAddress, verbose = verbose, Neighborhood = Neighborhood)
    properties = GetProperties(RequestsSession,AddressDictionary, size = size, verbose = verbose)
    return GetDataFrame(properties)

def GetAddressDictionary(RequestsSession, stringAddress, verbose = False, Neighborhood = True):
    AddressDictionary = ""
    if Neighborhood:
        AddressDictionary = GetAddressNeighborhood(RequestsSession, stringAddress, verbose = False, Neighborhood = True)
    if type(AddressDictionary) == str:
        AddressDictionary = GetAddressCity(RequestsSession, stringAddress, verbose = False, Neighborhood = True)
    return AddressDictionary

def GetAddressNeighborhood(RequestsSession, stringAddress, verbose = False, Neighborhood = True):
    response = AddressRequest(RequestsSession, stringAddress)
    AddressDictionaryNeighborhood = GetDataIfExists(response, ['neighborhood','result','locations',0,'address'])
    return AddressDictionaryNeighborhood 

def GetAddressCity(RequestsSession, stringAddress, verbose = False, Neighborhood = True):
    stringAddress = re.split(" - ",stringAddress)[0]
    response = AddressRequest(RequestsSession, stringAddress)
    AddressDictionaryCity = GetDataIfExists(response, ['city','result','locations',0,'address'])
    return AddressDictionaryCity 

def AddressRequest(RequestsSession, stringAddress, verbose = False):
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
    request = RequestsSession.request('OPTIONS',
                  r'https://glue-api.vivareal.com/v3/locations',
                  headers=headers)
    if verbose:
        print("First request:")
        print(request)        
    params = {
        'portal': 'VIVAREAL',
        'fields': 'neighborhood,city,account,condominium,poi,street',
        'includeFields': 'address.neighborhood,address.city,address.state,address.zone,address.locationId,address.point,url,advertiser.name,uriCategory.page,condominium.name,address.street',
        'size': 6,
        'q': stringAddress,
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
    request = RequestsSession.request(r'GET',
                  url,
                  headers = headers,
                  params = params)
    if verbose:
        print("Seccond request:")
        print(request)      
    return request.json()

def GetDataIfExists(observation, path):
    # Iterate over path through observation
    # path may have a codition in the string form "[key,value]"
    # observation[path[0]][path[1]][path[2]]...
    data = observation
    for item in path:
        # this is a filter
        if type(item) == list:
            name = item[0]
            value = item[1]
            filteredData = [i for i in list(data.items()) if name in i[1] and i[1][name] == value]
            if filteredData == []:
                return 'data not found (debug: GetDataIfExists)'
            data = filteredData[0][1]
        # this is a path
        else:
            if item not in data.keys():
                return 'data not found (debug: GetDataIfExists)';
            else:
                data = data[item]
                if(type(data) == list):
                    data = {i:j for i,j in enumerate(data)}
    return data

def GetProperties(RequestsSession, AddressDictionary,size=250, verbose = False):
    # First check if GET is valid
    yesterday = datetime.now() - timedelta(days=1)
    yesterdayRfc822 = yesterday.strftime('%a, %d %b %Y %H:%M:%S GMT')
    headers = {'Accept' : 'application/json, text/javascript, */*; q=0.01',
                'Accept-Encoding' : 'gzip, deflate, br',
                'Accept-Language' : 'en-US,en;q=0.5',
                'Connection' : 'keep-alive',
                'Host' : 'glue-api.vivareal.com',
                'If-Modified-Since' : yesterdayRfc822,
                'Origin' : 'https://www.vivareal.com.br',
                'Referer' : 'https://www.vivareal.com.br/',
                'Sec-Fetch-Dest' : 'empty',
                'Sec-Fetch-Mode' : 'cors',
                'Sec-Fetch-Site' : 'cross-site',
                'Sec-GPC' : '1',
                'TE' : 'trailers',
                'User-Agent' : 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:108.0) Gecko/20100101 Firefox/108.0',
                'x-domain' : 'www.vivareal.com.br'}
    r = RequestsSession.request('OPTIONS',
                  r'https://glue-api.vivareal.com/v2/listings',
                  headers=headers)
    if verbose:
        print("First request:")
        print(r)
    
    # Input address parameters in params
    params = {
        'addressCity' : AddressDictionary['city'],
        'addressLocationId' : AddressDictionary['locationId'],
        'addressNeighborhood' : AddressDictionary['neighborhood'],
        'addressState' : AddressDictionary['state'],
        'addressCountry' : 'Brasil',
        'addressStreet' : AddressDictionary['street'],
        'addressZone' : AddressDictionary['zone'],
        'addressPointLat' : AddressDictionary['point']['lat'],
        'addressPointLon' : AddressDictionary['point']['lat'],
        'business' : 'SALE',
        'facets' : 'amenities',
        'unitTypes' : '',
        'unitSubTypes' : '',
        'unitTypesV3' : '',
        'usageTypes' : '',
        'listingType' : 'USED',
        'parentId' : 'null',
        'categoryPage' : 'RESULT',
        'includeFields' : 'search(result(listings(listing(displayAddressType,amenities,usableAreas,constructionStatus,listingType,description,title,unitTypes,nonActivationReason,propertyType,unitSubTypes,id,portal,parkingSpaces,address,suites,publicationType,externalId,bathrooms,usageTypes,totalAreas,advertiserId,bedrooms,pricingInfos,showPrice,status,advertiserContact,videoTourLink,whatsappNumber,stamps),account(id,name,logoUrl,licenseNumber,showAddress,legacyVivarealId,phones),medias,accountLink,link)),totalCount),page,seasonalCampaigns,fullUriFragments,nearby(search(result(listings(listing(displayAddressType,amenities,usableAreas,constructionStatus,listingType,description,title,unitTypes,nonActivationReason,propertyType,unitSubTypes,id,portal,parkingSpaces,address,suites,publicationType,externalId,bathrooms,usageTypes,totalAreas,advertiserId,bedrooms,pricingInfos,showPrice,status,advertiserContact,videoTourLink,whatsappNumber,stamps),account(id,name,logoUrl,licenseNumber,showAddress,legacyVivarealId,phones),medias,accountLink,link)),totalCount)),expansion(search(result(listings(listing(displayAddressType,amenities,usableAreas,constructionStatus,listingType,description,title,unitTypes,nonActivationReason,propertyType,unitSubTypes,id,portal,parkingSpaces,address,suites,publicationType,externalId,bathrooms,usageTypes,totalAreas,advertiserId,bedrooms,pricingInfos,showPrice,status,advertiserContact,videoTourLink,whatsappNumber,stamps),account(id,name,logoUrl,licenseNumber,showAddress,legacyVivarealId,phones),medias,accountLink,link)),totalCount)),account(id,name,logoUrl,licenseNumber,showAddress,legacyVivarealId,phones,phones),developments(search(result(listings(listing(displayAddressType,amenities,usableAreas,constructionStatus,listingType,description,title,unitTypes,nonActivationReason,propertyType,unitSubTypes,id,portal,parkingSpaces,address,suites,publicationType,externalId,bathrooms,usageTypes,totalAreas,advertiserId,bedrooms,pricingInfos,showPrice,status,advertiserContact,videoTourLink,whatsappNumber,stamps),account(id,name,logoUrl,licenseNumber,showAddress,legacyVivarealId,phones),medias,accountLink,link)),totalCount)),owners(search(result(listings(listing(displayAddressType,amenities,usableAreas,constructionStatus,listingType,description,title,unitTypes,nonActivationReason,propertyType,unitSubTypes,id,portal,parkingSpaces,address,suites,publicationType,externalId,bathrooms,usageTypes,totalAreas,advertiserId,bedrooms,pricingInfos,showPrice,status,advertiserContact,videoTourLink,whatsappNumber,stamps),account(id,name,logoUrl,licenseNumber,showAddress,legacyVivarealId,phones),medias,accountLink,link)),totalCount))',
        'size' : size,
        'from':'',
        'q':'',
        'developmentsSize':'5',
        '__vt':'',
        'levels':'CITY',
        'ref':'',	
        'pointRadius':'',	
        'isPOIQuery':''}
    url = r'https://glue-api.vivareal.com/v2/listings'
    r = RequestsSession.request(r'GET',
                  url,
                  params=params,
                  headers = headers)
    if verbose:
        print("Seccond request:")
        print(r)
        
    # TODO: tratar erro 400 quando tem menos imóveis do que size
    
    properties = r.json()['search']['result']['listings']
    return properties
    
def GetDataFrame(properties):
        data_frame = pd.DataFrame()
        for prop in properties:
            prop_data = GetObservationData(prop)
            data_frame = pd.concat(
                [
                    data_frame,
                    prop_data
                ])
        return data_frame
    
def GetObservationData(observation):
    link = 'https://www.vivareal.com.br' + GetDataIfExists(observation,['link','href'])
    preco = GetDataIfExists(observation,['listing','pricingInfos',['businessType','SALE'],'price'])
    metragem = GetDataIfExists(observation,['listing','usableAreas',0])
    estado = GetDataIfExists(observation, ['link','data','state'])
    cidade = GetDataIfExists(observation, ['link','data','city'])
    bairro = GetDataIfExists(observation, ['link','data','neighborhood'])
    rua = GetDataIfExists(observation, ['link','data','street'])
    numero = GetDataIfExists(observation, ['link','data','streetNumber'])
    geo_point = str(GetDataIfExists(observation, ['link','address','point','lat'])) + ', ' + str(GetDataIfExists(observation, ['link','address','point','long']))
    quartos = GetDataIfExists(observation,['listing','bedrooms',0])
    banheiros = GetDataIfExists(observation,['listing','bathrooms',0])
    vagas = GetDataIfExists(observation,['listing','parkingSpaces',0])
    return pd.DataFrame.from_dict(data = {
                'link' : [link],
                'preco' : [preco],
                'metragem' : [metragem],
                'estado' : [estado],
                'cidade' : [cidade],
                'bairro' : [bairro],
                'rua' : [rua],
                'numero' : [numero],
                'geo_point' : [geo_point],
                'quartos' : [quartos],
                'banheiros' : [banheiros],
                'vagas' : [vagas]
                })
