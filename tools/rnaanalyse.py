import arcpy
import numpy as np
import os

class RNAanalyse(object):
    def __init__(self):
        self.label = "RNAanalyse"
        self.description = "RNA anylse tool"
        self.canRunInBackground = False

    def getParameterInfo(self):
        wea_lyr = arcpy.Parameter(
            displayName="Layer with WEA points.",
            name="wea_lyr",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Input")

        wea_lyr.filter.list = ["POINT"]

        flug_lyr = arcpy.Parameter(
            displayName="Layer with bird observations.",
            name="flug_lyr",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Input")

        flug_lyr.filter.list = ["LINE"]
            
        out_lyr = arcpy.Parameter(
            displayName="Output Layer",
            name="out_lyr",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Output")
            
        # threshold70_bool = arcpy.Parameter(
            # displayName="Use 70/20% (three categories) instead of 75/25% (two categories) threshold rule.",
            # name="threshold70_bool",
            # datatype="GPBoolean",
            # parameterType="Optional",
            # direction="Input")

        #threshold70_bool.value = "False"

        parameters = [wea_lyr, flug_lyr, out_lyr]
            
        return parameters

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        #check if Exemplare field exists
       
       return

    def updateMessages(self, parameters):
        if parameters[1].hasBeenValidated:
            exemplare_field = arcpy.ListFields(parameters[1].value, "Exemplare")
            if len(exemplare_field) < 1:
                parameters[1].setErrorMessage("No Exemplare field could be found.")
            else:
                parameters[1].clearMessage()

        return

    def execute(self, parameters, messages):
        #function to get center point of layer
        #def layerCenter(lyr):
            #lyrex = arcpy.Describe(lyr).extent
            #cpX = lyrex.XMin + (lyrex.XMax - lyrex.XMin)/2
            #cpY = lyrex.YMin + (lyrex.YMax - lyrex.YMin)/2
            #return cpX, cpY

        ##function for polygon corner coords
        #def polyExtent(xrange, yrange, cpx, cpy):
            #pXMin = cpx - xrange/2
            #pYMin = cpy - yrange/2
            #pXMax = cpx + xrange/2
            #pYMax = cpy + yrange/2
            #return arcpy.Extent(pXMin, pYMin, pXMax, pYMax)

        ##function to create polygon
        #def createPolygon(cornercoords):
            #polyArray = arcpy.Array()
            #polyArray.add(cornercoords.lowerLeft)
            #polyArray.add(cornercoords.lowerRight)
            #polyArray.add(cornercoords.upperRight)
            #polyArray.add(cornercoords.upperLeft)
            #polyArray.add(cornercoords.lowerLeft)
            #return arcpy.Polygon(polyArray)

        #def uniqueValues(table, field):
            #with arcpy.da.SearchCursor(table, field) as cursor:
                #return sorted({row[0] for row in cursor})

        #layer style for rna categories
        rnacategories = r"V:\Vorlagen_CAD_GIS\GIS\styles_aktuell\RNA_raster.lyr"
                
        def is_odd(num):
            return num & 0x1

        def createExtent(xmin, ymin, xmax, ymax):
            tmp = arcpy.Array()
            tmp.add(arcpy.Point(xmin, ymin))
            tmp.add(arcpy.Point(xmax, ymin))
            tmp.add(arcpy.Point(xmax, ymax))
            tmp.add(arcpy.Point(xmin, ymax))
            tmp.add(arcpy.Point(xmin, ymin))
            tmppoly = arcpy.Polygon(tmp)
            return tmppoly.extent

        #clean in memory workspace
        arcpy.Delete_management("in_memory")
        arcpy.env.overwriteOutput = True
        #Input
        layer = parameters[0].valueAsText
        flugLayer = parameters[1].valueAsText
        outputLayer = parameters[2].valueAsText
        #threshold_scheme = parameters[3].valueAsText
        
        #parameter definitions
        thpercentage = 0.75
        thpercentage2upper = 0.70
        thpercentage2lower = 0.20

        uraum = 6000

        #beginning of script
        mxd = arcpy.mapping.MapDocument("current")
        df = arcpy.mapping.ListDataFrames(mxd)[0]
        df_coord = df.spatialReference.PCSCode
        layerPCS = arcpy.Describe(flugLayer).spatialReference.PCSCode

        #get extent of input layer and calculate coordinates for alignment of fishnet
        #with dtk5 raster
        #DHDN_to_ETRS_1989_8_NTv2
        #GK3 31467
        #GK4 31468
        #utmn32 5652
        #utmn33 5653
        gt = "DHDN_To_ETRS_1989_8_NTv2"
        #gt = "DHDN_to_WGS_1984_4_NTv2 + ETRS_1989_to_WGS_1984"
        templateExtent = arcpy.Describe(layer).extent
        projection = df_coord
        if str(df_coord) == "5652":
            projection = 31467
            templateExtent = templateExtent.projectAs("31467", gt)
        if str(df_coord) == "5653":
            projection = 31468
            templateExtent = templateExtent.projectAs("31468", gt)

        extentXMin = templateExtent.XMin - uraum
        extentYMin = templateExtent.YMin - uraum
        extentXMax = templateExtent.XMax + uraum
        extentYMax = templateExtent.YMax + uraum

        fishnet_originXMin = np.floor(extentXMin/1000)
        fishnet_originYMin = np.floor(extentYMin/1000)
        fishnet_originXMax = np.ceil(extentXMax/1000)
        fishnet_originYMax = np.ceil(extentYMax/1000)
        #calculate lower left coordinates
        if is_odd(int(fishnet_originXMin)):
            fishnet_originXMin = fishnet_originXMin * 1000
        else:
            fishnet_originXMin = (fishnet_originXMin - 1) * 1000

        if is_odd(int(fishnet_originYMin)):
            fishnet_originYMin = (fishnet_originYMin - 1) * 1000
        else:
            fishnet_originYMin = fishnet_originYMin * 1000

        #calculate upper right coordinates
        if is_odd(int(fishnet_originXMax)):
            fishnet_originXMax = fishnet_originXMax * 1000
        else:
            fishnet_originXMax = (fishnet_originXMax + 1) * 1000

        if is_odd(int(fishnet_originYMax)):
            fishnet_originYMax = (fishnet_originYMax + 1) * 1000
        else:
            fishnet_originYMax = fishnet_originYMax * 1000

        
        #transform extent back to utm
        newExtent = createExtent(fishnet_originXMin, fishnet_originYMin, fishnet_originXMax, fishnet_originYMax)
        #newExtent = newExtent.projectAs(str(layerPCS))

        #arcpy.AddMessage("New Extent")
        #arcpy.AddMessage(newExtent.lowerLeft)
        #arcpy.AddMessage(newExtent.upperRight)

        lowerLeft = str(newExtent.XMin) + " " + str(newExtent.YMin)
        ycoord = str(newExtent.XMin) + " " + str(newExtent.YMin + 10)
        upperRight = str(newExtent.XMax) + " " + str(newExtent.YMax)

        arcpy.AddMessage("Creating fishnet...")
        arcpy.env.outputCoordinateSystem = arcpy.SpatialReference(projection)
        fishnettmp = arcpy.CreateFishnet_management("in_memory/fishnet", lowerLeft, ycoord, "250", "250", "0", "0", upperRight, "NO_LABELS", "#", "POLYGON") 
        arcpy.DefineProjection_management(fishnettmp, str(projection))

        fishnet = arcpy.Project_management(fishnettmp, outputLayer, str(layerPCS), gt)
        #reset output coordinate system 
        arcpy.env.outputCoordinateSystem = arcpy.SpatialReference(layerPCS)

        arcpy.AddMessage("Intersecting fishnet with data...")
        fishIntersect = arcpy.Intersect_analysis([fishnet, flugLayer], "in_memory\intersect", "ALL", "", "LINE")
        #arcpy.AddMessage("Exploding multipart features...")
        #fishIntersect2 = arcpy.MultipartToSinglepart_management(fishIntersect, "in_memory\intersect2")
        arcpy.AddMessage("Calculating statistics for fishnet cells...")

        #create field name to be dissolved by (depends on name of output feature class)
        dissField = "FID_" + arcpy.Describe(outputLayer).baseName
        #arcpy.AddMessage(dissField)
        dissolve = arcpy.Dissolve_management(fishIntersect, "in_memory\dissolve", dissField, [["Exemplare", "SUM"]], "MULTI_PART", "DISSOLVE_LINES")

        arcpy.AddMessage("Calculating threshold for RNA category...")
        table_as_array = arcpy.da.FeatureClassToNumPyArray(dissolve, ["SUM_Exemplare"])
        #percentile1 = np.percentile(table_as_array["SUM_Exempl"], 70)
        
        #sort in ascending/descending order and build cumulative sum
        #threshold2 for ascending (lower boundary) in three categorie scheme
        exemplare_sorted_asc = np.sort(table_as_array["SUM_Exemplare"])
        exemplare_sorted = exemplare_sorted_asc[::-1]
        
        cumsum = np.cumsum(exemplare_sorted)
        cumsum_asc = np.cumsum(exemplare_sorted_asc)
        #threshhold value
        cumsum_max = np.amax(cumsum)
        threshold = cumsum_max * thpercentage
        threshold2upper = cumsum_max * thpercentage2upper
        threshold2lower = cumsum_max * thpercentage2lower
        #calculate difference between cumsum array and threshold value
        #then get index of minimum value in order to extract kategorie threshold
        #from exemplare array
        diff = np.abs(cumsum - threshold)
        diff2upper = np.abs(cumsum - threshold2upper)
        diff2lower = np.abs(cumsum_asc - threshold2lower)
        minindex = np.argmin(diff)
        minindex2upper = np.argmin(diff2upper)
        minindex2lower = np.argmin(diff2lower)
        katthreshold = exemplare_sorted[minindex]
        katthreshold2upper = exemplare_sorted[minindex2upper]
        katthreshold2lower = exemplare_sorted_asc[minindex2lower]
        
                
        arcpy.AddMessage("Updating fishnet layer with statistics information...")
        #add field for ddp page name
        arcpy.AddField_management(fishnet, "EXEMPLARE", "SHORT")
        arcpy.AddField_management(fishnet, "KAT2", "TEXT", 50)
        arcpy.AddField_management(fishnet, "KAT3", "TEXT", 50)
                                          
        #update new fields  
        path_dict = {}  
                  
        #Create Dictionary  
        join_values = [dissField, "SUM_Exemplare"]
        with arcpy.da.SearchCursor(dissolve, join_values) as srows:  
            for srow in srows:  
                path_dict[srow[0]] = tuple(srow[i] for i in range(1,len(join_values)))  

        #function to convert number of exemplare to category based on threshold
        def addCategory(exemplare, threshold):
            if exemplare >= threshold:
                return "Kategorie II"
            else:
                return "Kategorie I"
                
        def addCategory2(exemplare, threshold, threshold2):
            #ausschlussempfehlung
            if exemplare >= threshold:
                return "Kategorie II"
            #eignungsbereiche
            elif exemplare <= threshold2:
                return "Kategorie I"
            #mit Nebenbestimmung
            else:
                return "Kategorie III"

        #Update Cursor  
        update_fields = ["EXEMPLARE", "KAT2", "KAT3"]
        in_field = "FID"

        update_fields.insert(0, in_field)  
        with arcpy.da.UpdateCursor(fishnet, update_fields) as urows:  
            for row in urows:  
                if row[0] in path_dict:  
                    row[1] = path_dict[row[0]][0]
                    row[2] = addCategory(row[1], katthreshold)
                    row[3] = addCategory2(row[1], katthreshold2upper, katthreshold2lower)
                else:
                    row[1] = 0
                    row[2] = 0
                    row[3] = 0
                    
                urows.updateRow(row)  
        
        #add shape with result to mxd
        shppath = os.path.split(outputLayer)
        result = arcpy.mapping.Layer(outputLayer)
        #lyr = result.getOutput(0)
        arcpy.mapping.AddLayer(df, result, "AUTO_ARRANGE")
        updatelayer = arcpy.mapping.ListLayers(mxd, result.name)[0]
        
        #apply layer style
        arcpy.ApplySymbologyFromLayer_management(updatelayer, rnacategories)
        arcpy.RefreshActiveView()
        arcpy.RefreshTOC()
        return
