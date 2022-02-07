#!/usr/bin/env python3
# Get data from GBIF API v.1
import pandas as pd
import urllib.parse as urlparse
from utils.api import APIRequests

class GBIF(APIRequests):
    def __init__(self):
        super(GBIF, self).__init__("https://api.gbif.org/v1/")

    def speciesOccurrences(self,name):
        limit = 300
        offset = 0
        end = False
        df = pd.DataFrame()
        while not end:
            payload = {"q": urlparse.quote(str(name).lower()), "limit": limit, "offset": offset}
            req = self._get("occurrence/search",payload=payload)
            if req:
                response = req.json()
                df = pd.concat([df, pd.DataFrame(response["results"])])
                end = response["endOfRecords"]
                offset += limit
            else:
                end = True

        return df

gbifData = GBIF()
print(gbifData.speciesOccurrences("Cyanistes caeruleus"))