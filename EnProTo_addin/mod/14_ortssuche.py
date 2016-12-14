class ortssuche(object):
    """Implementation for ortssuche.combobox (ComboBox)"""
    def __init__(self):
        sel.value =
        self.editable = True
        self.enabled = True
        self.dropdownWidth = ''
        self.width = 'WWWWWWWWW'
    def onSelChange(self, selection):
        pass

    def onEditChange(self, text):
        pass
    def onFocus(self, focused):
        self.items = ["test"]
        pass
    def onEnter(self):
        import arcpy
        from arcpy import env
        import urllib
        import urllib2
        import os
        import shutil
        import ssl
        import itertools
        import json


        #maybe a security risk but solves the issue with
        #URLError: <urlopen error [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed (_ssl.c:590)>
        ssl._create_default_https_context = ssl._create_unverified_context
        import errno

        def make_dir(path):
            try:
                os.makedirs(path)
            except OSError:
                if not os.path.isdir(path):
                    raise

        def createExtent(xmin, ymin, xmax, ymax):
            tmp = arcpy.Array()
            tmp.add(arcpy.Point(xmin, ymin))
            tmp.add(arcpy.Point(xmax, ymin))
            tmp.add(arcpy.Point(xmax, ymax))
            tmp.add(arcpy.Point(xmin, ymax))
            tmp.add(arcpy.Point(xmin, ymin))
            tmppoly = arcpy.Polygon(tmp)
            return tmppoly.extent

        def getCityFromOSM(city, timeout=25):
            overpassurl = "https://overpass-api.de/api/interpreter?data=[out:json];"
            query = """(
              node["name"="{0}"]["place"~"city|town|village"];
            );"""

            etag = """out body; >; out skel qt;"""

            requesturl = overpassurl + urllib.quote_plus(query.format(city) + etag)

            myrequest = urllib2.Request(requesturl)

            try:
                OSMurlHandle = urllib2.urlopen(myrequest, timeout=timeout)
                data = OSMurlHandle.read()
            except urllib2.URLError, e:
                raise

            return data

        def parseOSMjson(data):
            datadecoded = json.loads(data)["elements"]

            citydict = {}

            i = 1
            for node in datadecoded:
                cityname = node["tags"]["name"]
                if "is_in" in node["tags"]:
                    wo = cityname + "," + node["tags"]["is_in"]
                else:
                    wo = cityname

                citydict[i] = {"wo": wo, "coords": [node["lat"],
                    node["lon"]]}

                i += 1
            return citydict

        ######################
        ##constants
        ######################

        extRange = 3000

        GK2 = "31466"
        GK3 = "31467"
        GK4 = "31468"
        GK5 = "31469"
        #NZ-E EPSG Codes
        utmn31NZ = "5651"
        utmn32NZ = "5652"
        utmn33NZ = "5653"
        # "normal" UTM Codes
        utmn31 = "25831"
        utmn32 = "25832"
        utmn33 = "25833"
        wgs = "4326"
        gt = "DHDN_To_ETRS_1989_8_NTv2"
        gt1 = "ETRS_1989_To_WGS_1984"
        gt2 = "DHDN_To_WGS_1984_4_NTv2"
        #gt = "DHDN_to_WGS_1984_4_NTv2 + ETRS_1989_to_WGS_1984"
        trafoDict = {GK2: gt2, GK3: gt2, GK4: gt2, GK5: gt2, utmn31NZ: gt1, utmn32NZ: gt1, utmn33NZ: gt1, utmn31: gt1, utmn32: gt1, utmn33:gt1}

        ######################
        #begin of code
        ######################
        tdata = getCityFromOSM("Gronau")

        cities = parseOSMjson(tdata)

        if len(cities) > 1:
            #message select city
            pythonaddins.MessageBox("Select city:")
        else:
            selCity = 1


       #get path to project
        mxd = arcpy.mapping.MapDocument("current")
        df  = arcpy.mapping.ListDataFrames(mxd)[0]
        try:
            dfPCS = df.spatialReference.PCSCode
        except:
            err_dfcs = pythonaddins.MessageBox("Data frame has no coordinate system assigned.", "Error", 0)
            print(err_dfcs)

        if not str(dfPCS) in trafoDict.keys():
            outMSG = ("The data frame coordinate system did not"
            "match any of the following EPSG codes: {0}. Please choose one of the specified"
            "coordinate systems before using this tool in order to prevent inaccuacies while reprojecting.").format(trafoDict.keys())
            PCSwarning = pythonaddins.MessageBox(outMSG, "PCS Warning", 0)
            print(PCSwarning)
            ####### Continue does not work, loop breaks if error is encounterd!!!!########


        #create point geometry from selected city
        pointGeom = arcpy.PointGeometry(arcpy.Point(cities[selCity]["coords"][0],cities[selCity]["coords"][1]), arcpy.SpatialReference(3857))
        #reproject to coord of df
        tpointGeom = pointGeom.projectAs(str(dfPCS),arcpy.ListTransformations(arcpy.SpatialReference(3857),arcpy.SpatialReference(dfPCS))[0])


        #create extent around point
        pointExtent = tpointGeom.extent()
        panExtent = createExtent(pointExtent.xMin + extRange, pointExtent.yMin + extRange, pointExtent.xMax + extRange, pointExtent.yMax + extRange)

        #create extent
        df.panToExtent(panExtent)


        pass
    def refresh(self):
        pass
        
