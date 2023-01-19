#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 13 10:33:00 2023

@author: perna
"""
import requests
import pandas as pd
from datetime import datetime, timedelta
import re

def GetPropertiesData(state, city, neighborhood = "", size = 250, verbose = False):
    """
    GetPropertiesData: Get data from properties in an address directly related to stringAddress
 
    Parameters
    ----------
    state : str
        State to search    
    city : str
        City to search    
    neighborhood : str
        Neighborhood to search    
    size : int
        Number of observations to get, values bigger than 300 can lead to an error
    verbose : bool
        Should verbose?
    
    Returns
    -------
    dfProperties : pandas.DataFrame
        pandas.DataFrame with `size` number of properties with the following columns
            'link' : str, property's url,
            'preco' : int, property's price,
            'metragem' : int, property's area,
            'estado' : str, state's name,
            'cidade' : str, city's name,
            'bairro' : str, neighborhood's name,
            'rua' : str, street's name,
            'numero' : int, number address,
            'geo_point' : str, geolocation,
            'quartos' : int, property's number of bedrooms,
            'banheiros' : int, property's number of bathrooms,
            'vagas' : int, property's number of parking
    """
    hasNeighborhood = neighborhood != ""
    stringAddress = city + ", " + state + " - " + neighborhood if hasNeighborhood else city + ", " + state
    RequestsSession = requests.Session()
    AddressDictionary = GetAddressDictionary(RequestsSession, stringAddress, verbose = verbose, hasNeighborhood = hasNeighborhood)
    properties = GetProperties(RequestsSession,AddressDictionary, size = size, verbose = verbose)
    dfProperties = GetDataFrame(properties)
    return dfProperties

def GetAddressDictionary(RequestsSession, stringAddress, verbose = False, hasNeighborhood = True):
    AddressDictionary = ""
    if hasNeighborhood:
        AddressDictionary = GetAddressNeighborhood(RequestsSession, stringAddress, verbose = verbose)
    if type(AddressDictionary) == str:
        AddressDictionary = GetAddressCity(RequestsSession, stringAddress, verbose = verbose)
    return AddressDictionary

def GetAddressNeighborhood(RequestsSession, stringAddress, verbose = False):
    response = AddressRequest(RequestsSession, stringAddress, verbose = verbose)
    AddressDictionaryNeighborhood = GetDataIfExists(response, ['neighborhood','result','locations',0,'address'])
    return AddressDictionaryNeighborhood 

def GetAddressCity(RequestsSession, stringAddress, verbose = False):
    stringAddress = re.split(" - ",stringAddress)[0]
    response = AddressRequest(RequestsSession, stringAddress, verbose = verbose)
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
    response = OptionsRequest(RequestsSession, headers, r'https://glue-api.vivareal.com/v3/locations', verbose = verbose)
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
    response = GetRequest(RequestsSession, headers, params, url)
    jsonResponse = response.json()
    return jsonResponse

def OptionsRequest(RequestsSession, headers, url, verbose = False):
    response = RequestsSession.request('OPTIONS',
                  url,
                  headers=headers)
    if verbose:
        print("Options request:")
        print(response)
    return response

def GetRequest(RequestsSession, headers, params, url, verbose = False):
    response = RequestsSession.request(r'GET',
                  url,
                  headers = headers,
                  params = params)
    if verbose:
        print("Get request:")
        print(response)
    return response

def GetDataIfExists(observation, path):
    # TODO: Refactor
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
                return 'NA'
            data = filteredData[0][1]
        # this is a path
        else:
            if item not in data.keys():
                return 'NA'
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
    response = OptionsRequest(RequestsSession, headers, r'https://glue-api.vivareal.com/v2/listings')
    if verbose:
        print("First request:")
        print(response)
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
    response = RequestsSession.request(r'GET',
                  url,
                  params=params,
                  headers = headers)
    if verbose:
        print("Seccond request:")
        print(response)
        
    # TODO: tratar erro 400 quando tem menos imóveis do que size
    
    properties = response.json()['search']['result']['listings']
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