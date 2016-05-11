class OSM(object):
    """Implementation for OSM.combobox (ComboBox)"""
    def __init__(self):
        self.editable = True
        self.enabled = True
        self.dropdownWidth = 'WWWWWWW'
        self.width = ''
    def onSelChange(self, selection):
        import arcpy
        from arcpy import env
        import urllib
        import urllib2
        import os
        import shutil
        import errno

        timeout = 600

        def make_dir(path):
            try:
                os.makedirs(path)
            except OSError:
                if not os.path.isdir(path):
                    raise

        # load the OpenStreetMap specific toolbox
        arcpy.ImportToolbox(r"c:\program files (x86)\arcgis\desktop10.3\ArcToolbox\Toolboxes\OpenStreetMap Toolbox.tbx")

        #get bounding box of current viewing extent or (largest) layer?
        toclayer = pythonaddins.GetSelectedTOCLayerOrDataFrame()
        try:
            lyrDesc = arcpy.Describe(toclayer)
        except:
            msg = pythonaddins.MessageBox("No TOC layer is selected.", "Error", 0)
            print(msg)

        #get path to project
        mxd = arcpy.mapping.MapDocument("current")
        mxdpath = mxd.filePath
        #get data frame and df PCS
        df  = arcpy.mapping.ListDataFrames(mxd)[0]
        try:
            dfPCS = df.spatialReference.PCSCode
        except:
            err_dfcs = pythonaddin.MessageBox("Data frame has no coordinate system assigned.", "Error", 0)
            print(err_dfcs)

        #create path to GIS data directory in project directory
        rootpath = re.split("05_GIS",mxdpath)[0]
        OSMdir = os.path.join(rootpath, "05_GIS", "av_daten", "10_OSM", selection)

        #create osm dir if not existent
        make_dir(OSMdir)

        #create temp directory for storing osm xml data
        OSMtmp = os.path.join(OSMdir, "ztmp")
        make_dir(OSMtmp)


        lyrext = lyrDesc.extent
        #transform coord of extent if not WGS84
        GK3 = "31467"
        GK4 = "31468"
        utmn32 = "5652"
        utmn33 = "5653"
        wgs = "4326"
        gt = "DHDN_To_ETRS_1989_8_NTv2"
        gt1 = "ETRS_1989_To_WGS_1984"
        gt2 = "DHDN_To_WGS_1984_4_NTv2"
        #gt = "DHDN_to_WGS_1984_4_NTv2 + ETRS_1989_to_WGS_1984"
        trafoDict = {GK3: gt2, GK4: gt2, utmn32: gt1, utmn33: gt1}
        dfPCS = lyrDesc.spatialReference.PCSCode
        if not str(dfPCS) == wgs:
            if str(dfPCS) in [utmn32, utmn33]:
                lyrext = lyrext.projectAs(wgs, gt1)
            elif str(dfPCS) in [GK3, GK4]:
                lyrext = lyrext.projectAs(wgs, gt2)
            else:
                lyrext = lyrext.projectAs(wgs)

        bboxtuple = (lyrext.YMin, lyrext.XMin, lyrext.YMax, lyrext.XMax)

        #bboxtuple = (41.88269405444917,12.48070478439331,41.89730998384814,12.503278255462645)
        overpassurl = "https://overpass-api.de/api/interpreter?data=[out:xml];"

        #end tag for query
        etag = """out body; >; out skel qt;"""

        ######## queries #########
        churches = """
        (
          node["amenity"="place_of_worship"]["religion"="christian"]{0};
          way["amenity"="place_of_worship"]["religion"="christian"]{0};
          relation["amenity"="place_of_worship"]["religion"="christian"]{0};
        );"""

        qHighway = """
        (
          way["highway"]{0};
        );"""

        qWEA = """
        (
          node [power=generator][power_source=wind]{0};
          node [power=generator]["generator:source"=wind]{0};
          way [power=generator][power_source=wind]{0};
          way [power=generator]["generator:source"=wind]{0};
        ); """

        qHospitals = """
         (
          node["amenity"="hospital"]{0};
          way["amenity"="hospital"]{0};
          relation["amenity"="hospital"]{0};
         );"""

        #for classes of protected areas see http://wiki.openstreetmap.org/wiki/DE:Tag:boundary%3Dprotected_area
        qSchutz = """
         (
          node["boundary"="protected_area"]{0};
          way["boundary"="protected_area"]{0};
          relation["boundary"="protected_area"]{0};
         );"""

        #make dictionary from queries
        qDict = {"Streets": qHighway, "WEA": qWEA, "Hospitals": qHospitals, "Schutzgebiete": qSchutz}

        #create full query
        query = (qDict[selection] + etag).format(bboxtuple)
        #fetch data from Overpass
        requesturl = overpassurl + urllib.quote_plus(query)

        myRequest = urllib2.Request(requesturl)
        #file path for temporary osm data
        OSMdata = os.path.join(OSMtmp, "osm.xml")
        try:
            OSMurlHandle = urllib2.urlopen(myRequest, timeout=timeout)
            OSMfile = file(OSMdata, 'wb')
            OSMfile.write(OSMurlHandle.read())
            OSMfile.close()
        except urllib2.URLError, e:
            raise
            # if hasattr(e, 'reason'):
            #     AddMsgAndPrint('Unable to reach the server.', 2)
            #     AddMsgAndPrint(e.reason, 2)
            # elif hasattr(e, 'code'):
            #     AddMsgAndPrint('The server was unable to fulfill the request.', 2)
            #     AddMsgAndPrint(e.code, 2)

        # define the names for the feature dataset and the feature classes
        #inputName = "OSM"
        inputName = selection
        #set workspace to scratch workspace
        wspace = env.scratchWorkspace

        validatedTableName = arcpy.ValidateTableName(inputName, wspace)
        nameOfTargetDataset = os.path.join(wspace, validatedTableName)

        fcpoint = os.path.join(validatedTableName, selection + r"_osm_pt")
        fcline = os.path.join(validatedTableName, selection + r"_osm_ln")
        fcpoly = os.path.join(validatedTableName, selection + r"_osm_ply")

        nameOfPointFeatureClass = os.path.join(wspace, fcpoint)
        nameOfLineFeatureClass = os.path.join(wspace, fcline)
        nameOfPolygonFeatureClass = os.path.join(wspace, fcpoly)

        #import downloaded osm.xml into default database and get attributes
        arcpy.OSMGPFileLoader_osmtools(OSMdata, "CONSERVE_MEMORY", "ALL", nameOfTargetDataset, nameOfPointFeatureClass, nameOfLineFeatureClass, nameOfPolygonFeatureClass)


        # filter the points to only process the attribute carrying nodes
        #filteredPointLayer = 'Only attributed nodes'
        #arcpy.MakeFeatureLayer_management(r'stuttgart\stuttgart_osm_pt', filteredPointLayer, "osmSupportingElement = 'no'")

        # extract the name tag for the filtered point features
        #arcpy.OSMGPAttributeSelector_osmtools(filteredPointLayer, 'name,note')

        tmpLayer = []
        #loop feature classes get attributes and project to coord of project dataframe
        for fc in arcpy.ListFeatureClasses(feature_dataset=selection):
            # extract the name tag for all line features
            arcpy.OSMGPAttributeSelector_osmtools(fc, 'name')
            #export fc to shape in memory
            #shptmp = arcpy.FeatureClassToFeatureClass_conversion (fc, OSMtmp, shpName)
            arcpy.FeatureClassToShapefile_conversion(os.path.join(wspace, selection, fc), OSMtmp)
            tmpLayer.append(fc)
            #print warning if dfPCS is not utm or gk
            if not str(dfPCS) in trafoDict.keys():
                outMSG = ("The data frame coordinate system does not"
                "match any of the following EPSG codes: {0}. Therefore no transformation was used"
                "while reprojecting, which might lead to inaccuracies.").format(trafoDict.keys())
                PCSwarning = pythonaddins.MessageBox(outMSG, "PCS Warning", 0)
                print(PCSwarning)
            outshp = os.path.join(OSMdir, fc + ".shp")
            shptmp = os.path.join(OSMtmp, fc + ".shp")
            arcpy.Project_management(shptmp, outshp, str(dfPCS), trafoDict[str(dfPCS)])


        #delete fc from scratch db afterwards
        arcpy.Delete_management(os.path.join(wspace, selection))
        arcpy.Delete_management(os.path.join(wspace, selection + "_osm_relation"))
        arcpy.Delete_management(os.path.join(wspace, selection + "_osm_revision"))

        #remove layers
        #for lyr in tmpLayer:
         #   rlyr = arcpy.mapping.ListLayers(mxd, lyr, df)[0]
          #  try:
           #     arcpy.mapping.RemoveLayer(df, rlyr)
           # except:
            #    raise
        lyrs = arcpy.mapping.ListLayers(mxd, selection + "*")
        for lyr in lyrs:
            if not lyr.isGroupLayer:
                try:
                    arcpy.mapping.RemoveLayer(df, lyr)
                except:
                    raise

        groupLyr = arcpy.mapping.ListLayers(mxd, selection)[0]
        arcpy.env.workspace = OSMdir
        fcList = arcpy.ListFeatureClasses()
        for f in fcList:
            #nlyr = arcpy.MakeFeatureLayer_management(os.path.join(OSMdir, f))
            lyr = arcpy.mapping.Layer(os.path.join(OSMdir, f))
                #arcpy.mapping.ListLayers(mxd, str(nlyr))[0]
            arcpy.mapping.AddLayerToGroup(df, groupLyr, lyr)


        #move layers to OSM group layer
        #lyrs = arcpy.mapping.ListLayers(mxd, selection + "*")
        #get group layer object
        #groupLyr = arcpy.mapping.ListLayers(mxd, selection)[0]
        #for lyr in lyrs:
        #    if not lyr.isGroupLayer:
        #        arcpy.mapping.AddLayerToGroup(df, groupLyr, lyr)


        #add shapes to project (create group layer?)

        #delete temporary data dir
        try:
            shutil.rmtree(OSMtmp)
        except:
            raise

        pass

    def onEditChange(self, text):
        pass
    def onFocus(self, focused):
        self.items = ["Streets", "WEA", "Hospitals", "Schutzgebiete"]
        pass
    def onEnter(self):
        pass
    def refresh(self):
        pass
        
