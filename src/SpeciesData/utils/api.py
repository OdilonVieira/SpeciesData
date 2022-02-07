#!/usr/bin/env python3
import requests

class APIRequests:
    def __init__(self,endpoint):
        self.__endpoint = endpoint #the API endpoint

    def _get(self,sublevels=None,payload=None):
        #basic method to validate GET requests.
        try:
            url = self.__endpoint
            if isinstance(sublevels,str):
                url += sublevels
            return requests.get(url,params=payload)
        except:
            print("An error occurred during the request, check the internet connection and the URL variables.")
            return False

    def endpoint(self):
        return self.__endpoint

    def _setEndpoint(self,endpoint):
        self.__endpoint = str(endpoint).strip()
