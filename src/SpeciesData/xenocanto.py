#!/usr/bin/env python3
# Get data from Xenocanto API v. 2
import pandas as pd
from utils.api import APIRequests


class Xenocanto(APIRequests):

    def __init__(self):
        super(Xenocanto, self).__init__("https://xeno-canto.org/api/2/recordings")
        self.__tags = {"gen": None, "rec": None, "cnt": None, "loc": None, "rmk": None, "also": None, "type": None,
                       "q": None, "q>": None, "q<": None, "area": None, "since": None, "year": None, "month": None,
                       "nr": None, "lat": None, "lon": None, "box": None, "lic": None}
        self.__target = None

    def setQuery(self, q):
        if q:
            self.__target = str(q).strip()

    def setSpecies(self, g, s=None):
        if g:
            g = str(g).strip()
            if s:
                self.__target = g + " " + str(s).strip()
            else:
                self.__tags["gen"] = g

    def setCountry(self, c):
        self.__tags["cnt"] = str(c).lower().strip()

    def setLocality(self, l):
        self.__tags["loc"] = str(l).lower().strip()

    def setAuthor(self, n):
        self.__tags["rec"] = str(n).lower().strip()

    def setRemark(self, r):
        self.__tags["rmk"] = str(r).lower().strip()

    def setCatalogNumber(self, n, n2=None):
        self.__tags["nr"] = str(int(n))
        if n and n2:
            self.__tags["nr"] = "-".join([str(int(c)) for c in [n, n2]])

    def setBackgroundSpecies(self, b):
        self.__tags["also"] = str(b).lower().strip()

    def setQuality(self, q, direction=0):
        q = str(q).upper().strip()
        if q in ["A", "B", "C", "D", "E"]:
            if direction > 0:
                self.__tags["q>"] = q
            elif direction < 0:
                self.__tags["q<"] = q
            else:
                self.__tags["q"] = q

    def setType(self, t):
        t = str(t).lower().strip()
        if t in ["call", "song"]:
            self.__tags["type"] = t

    def setRegion(self, r):
        self.__tags["area"] = str(r).lower().strip()

    def setPeriod(self, y=None, m=None, d=None):
        if d:
            self.__tags["since"] = str(int(d))
            if y and m:
                self.__tags["since"] = "-".join([str(int(p)) for p in [y, m, d]])
        else:
            if y:
                self.__tags["year"] = str(int(y))
            if m:
                self.__tags["month"] = str(int(m))

    def setCoordinates(self, lat1=None, long1=None, lat2=None, long2=None):
        if long1:
            if lat2 and long2:
                self.__tags["box"] = ",".join([str(float(c)) for c in [lat1, long1, lat2, long2]])
            else:
                self.__tags["lon"] = str(float(long1))
        if lat1 and not lat2 and not long2:
            self.__tags["lat"] = str(float(lat1))

    def setLicence(self, l, *args):
        l = [l]
        l.extend(args)
        l = [str(s).upper().strip() for s in l]
        self.__tags["lic"] = "-".join(l)

    def getRecordings(self):
        tags = dict(filter(lambda k: k[1] != None, self.__tags.items()))
        target = self.__target
        searchStrings = []
        if target:
            searchStrings.append(target)

        for k in tags.keys():
            searchStrings.append("%s:%s" % (k, tags[k]))

        if searchStrings:
            params = {"query": " ".join(searchStrings), "page": 1}
            end = False
            df = pd.DataFrame()
            while not end:
                req = self._get(payload = params)
                if req:
                    response = req.json()
                    df = pd.concat([df, pd.DataFrame(response["recordings"])])
                    end = response["page"] == response["numPages"]
                    params["page"] += 1
                else:
                    end = True
            return df

xeno = Xenocanto()
xeno.setSpecies("troglodytes","troglodytes")
recordings = xeno.getRecordings()