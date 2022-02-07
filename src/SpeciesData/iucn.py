#!/usr/bin/env python3
# Get data from IUCN API v. 3
import pandas as pd
import urllib.parse as urlparse
from utils.api import APIRequests

class IUCN(APIRequests):
    def __init__(self,token):
        super(IUCN, self).__init__("https://apiv3.iucnredlist.org/api/v3/") #define the API endpoint
        self._token = token #define the Token necessary to perform some requests.

    def version(self):
        # return the current version of the API
        req = self._get("version")
        if req:
            return req.json()["version"]
        return False

    def countries(self):
        # return a DataFrame of countries in the IUCN database
        payload = {"token":self._token}
        req = self._get("country/list",payload)
        if req:
            return pd.DataFrame(req.json()["results"])
        return False

    def speciesByCountry(self,isocode):
        # return a DataFrame of species that occur in a specific country
        countries = self.countries()
        if not countries.empty:
            if countries["isocode"].isin([isocode]).any():
                payload = {"token": self._token}
                req = self._get("country/getspecies/"+isocode, payload)
                if req:
                    return pd.DataFrame(req.json()["result"])
            else:
                print("Wrong country isocode.")
        return False

    def regions(self):
        # return the regions considered by the IUCN
        payload = {"token": self._token}
        req = self._get("region/list", payload)
        if req:
            return pd.DataFrame(req.json()["results"])
        return False

    def speciesByRegion(self,regionIdentifier):
        # return a DataFrame of species that occur in a specific region
        regions = self.regions()
        if not regions.empty:
            if regions["identifier"].isin([regionIdentifier]).any():
                payload = {"token": self._token}
                urlbase = "species/region/" + regionIdentifier + "/page/"
                page = 0
                count = 1
                df = pd.DataFrame()
                # the query pages are limited to 10000 records, so the next block
                #concatenates DataFrames of different query pages while records count != 0
                while count != 0:
                    req = self._get(urlbase+str(page), payload)
                    if req:
                        count = int(req.json()["count"])
                        if count > 0:
                            df = pd.concat([df, pd.DataFrame(req.json()["result"])])
                    else:
                        count = 0
                    page += 1
                return df
            else:
                print("Wrong region identifier.")
        return False

    def speciesByCategory(self,category):
        # return a DataFrame of species classified in a specific conservation category
        category = str(category).upper()
        payload = {"token": self._token}
        urlbase = "species/category/"
        if self.speciesCategories().isin([category]).any():
            urlbase += category.replace("/","")
            req = self._get(urlbase, payload)
            if req:
                return pd.DataFrame(req.json()["result"])
        else:
            print("Wrong category. See 'speciesCategories()' to get valid category types.")

    def speciesCategories(self):
        # return the IUCN categories
        return pd.Series(["DD", "LC", "NT", "VU", "EN", "CR", "EW", "EX", "LR/lc", "LR/nt", "LR/cd"]).str.upper()

    def speciesCount(self,regionIdentifier=None):
        # return a species count by region or global (default)
        payload = {"token": self._token}
        urlbase = "speciescount"
        if self.regions()["identifier"].isin([regionIdentifier]).any():
            urlbase += "/region/" + regionIdentifier

        req = self._get(urlbase, payload)
        if req:
            res = req.json()
            return pd.DataFrame({
                "count": [res["count"],res["speciescount"]],
                "note": [res["note1"], res["note2"]]
            })

    def speciesNomenclature(self,name,commons=False):
        # return species common names or synonyms
        payload = {"token": self._token}
        urlbase = "species/synonym/"
        if commons:
            urlbase = "species/common_names/"
        urlbase += urlparse.quote(str(name).lower())
        req = self._get(urlbase, payload)
        if req:
            return pd.DataFrame(req.json()["result"])

    def speciesLink(self,name):
        # return the link to the species page on IUCN website
        urlbase = "weblink/" + urlparse.quote(str(name).lower())
        req = self._get(urlbase)
        if req:
            return req.json()["rlurl"]

    def speciesGroups(self):
        # return the groups of species considered by the IUCN (e.g. birds, mammals etc.)
        payload = {"token": self._token}
        req = self._get("comp-group/list", payload)
        if req:
            return pd.DataFrame(req.json()["result"])

    def speciesByGroup(self,group):
        # return a DataFrame of species in a specific group
        payload = {"token": self._token}
        if self.speciesGroups()["group_name"].isin([group]).any():
            urlbase = "comp-group/getspecies/" + urlparse.quote(str(group).lower())
            req = self._get(urlbase, payload)
            if req:
                return pd.DataFrame(req.json()["result"])

    def speciesInformations(self,name_id,regionIdentifier=None,byId=False):
        # return a DataFrame with basic informations of a species by region or global (default)
        return self.__speciesQuery(name_id,"informations",regionIdentifier,byId)

    def speciesCitation(self,name_id,regionIdentifier=None,byId=False):
        # return a DataFrame with the text citation of the species data, by region or global (default)
        return self.__speciesQuery(name_id,"citation",regionIdentifier,byId)

    def speciesHabitats(self,name_id,regionIdentifier=None,byId=False):
        # return a DataFrame with the habitats of a species, by region or global (default)
        return self.__speciesQuery(name_id,"habitats",regionIdentifier,byId)

    def speciesOccurrences(self,name_id,regionIdentifier=None,byId=False):
        # return a DataFrame with occurrences of a specie, by region or global (default)
        return self.__speciesQuery(name_id,"occurrences",regionIdentifier,byId)

    def speciesThreats(self,name_id,regionIdentifier=None,byId=False):
        # return a DataFrame with the main threats of a species, by region or global (default)
        return self.__speciesQuery(name_id,"threats",regionIdentifier,byId)

    def speciesConservation(self,name_id,regionIdentifier=None,byId=False):
        # return a DataFrame with the conservation plans related to a species, by region or global (default)
        return self.__speciesQuery(name_id,"conservation",regionIdentifier,byId)

    def speciesHistory(self,name_id,regionIdentifier=None,byId=False):
        # return a DataFrame with the conservation history of a species, by region or global (default)
        return self.__speciesQuery(name_id,"history",regionIdentifier,byId)

    def speciesTaxonomicNotes(self,name_id,regionIdentifier=None,byId=False):
        # return a DataFrame with taxonomic notes of a species, by region or global (default)
        return self.__speciesQuery(name_id,"narrative",regionIdentifier,byId)

    def plantGrowthForms(self,name_id,regionIdentifier=None,byId=False):
        # return a DataFrame with growth forms of a plant species, by region or global (default)
        return self.__speciesQuery(name_id, "grouthForms", regionIdentifier, byId)

    def __speciesQuery(self,name_id,queryType,regionIdentifier=None,byId=False):
        # method that perform different query types possibles in the IUCN API

        #define the payload (token) that will be used as a GET variable
        payload = {"token": self._token}
        # define the url query types
        urlbase = pd.DataFrame({
            "occurrences":["species/countries/"],
            "history":["species/history/"],
            "threats": ["threats/species/"],
            "habitats":["habitats/species/"],
            "conservation":["measures/species/"],
            "narrative":["species/narrative/"],
            "citation":["species/citation/"],
            "informations":["species/"],
            "grouthForms":["growth_forms/species/"]
        })
        if urlbase.keys().isin([queryType]).any():
            # Here the url are formated for the specific query types
            urlbase = urlbase[queryType][0]
            if byId:
                urlbase += "id/"
            elif ~pd.Series(["narrative","citation","informations"]).isin([queryType]).any():
                urlbase += "name/"
            urlbase += urlparse.quote(str(name_id).lower())
            if self.regions()["identifier"].isin([regionIdentifier]).any():
                urlbase += "/region/" + str(regionIdentifier).lower()
            # Make the request
            req = self._get(urlbase, payload)
            # Check the request state
            if req:
                # return the result formated as a pandas.DataFrame
                return pd.DataFrame(req.json()["result"])

#iucnData = IUCN("9bb4facb6d23f48efbf424bb05c0c1ef1cf6f468393bc745d42179ac4aca5fee")