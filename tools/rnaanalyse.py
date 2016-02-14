import arcpy
import numpy as np

class RNAanalyse(object):
    def __init__(self):
        self.label = "RNAanalyse"
        self.description = "RNA anylse tool"
        self.canRunInBackground = False

    def getParameterInfo(self):
        in_lyr = arcpy.Parameter(
            displayName="Layer with WEA points.",
            name="in_lyr",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Input")

        #in_lyr.filter.list = ["POINT"]
            
        out_lyr = arcpy.Parameter(
            displayName="Output Layer",
            name="out_lyr",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Output")

        parameters = [in_lyr, out_lyr]
            
        return parameters

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):

        return

    def updateMessages(self, parameters):
        
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

        #clean in memory workspace
        arcpy.Delete_management("in_memory")
        arcpy.env.overwriteOutput = True
        #Input
        layer = parameters[0].valueAsText
        outputLayer = parameters[1].valueAsText
        thpercentage = 0.75

        #beginning of script
        mxd = arcpy.mapping.MapDocument("current")
        df = arcpy.mapping.ListDataFrames(mxd)[0]
        df_coord = df.spatialReference.PCSCode
        #get dataframe dimensions
        dfX, dfY = df.elementWidth * 0.01, df.elementHeight * 0.01

        #calculate polygon length in map units
        #polyX, polyY = dfX * scale, dfY * scale
        #arcpy.AddMessage(polyX)

        #create polygon
        #centerX, centerY = layerCenter(layer)
        #polygon = createPolygon(polyExtent(polyX, polyY, centerX, centerY))

        templateExtent = arcpy.Describe(layer).extent
        lowerLeft = str(templateExtent.lowerLeft)
        ycoord = str(templateExtent.XMin) + " " + str(templateExtent.YMin + 10) 

        arcpy.AddMessage("Creating fishnet...")
        fishnet = arcpy.CreateFishnet_management(outputLayer, lowerLeft, ycoord, "250", "250", "0", "0", "", "NO_LABELS", templateExtent, "POLYGON") 

        arcpy.AddMessage("Intersecting fishnet with data...")
        fishIntersect = arcpy.Intersect_analysis([fishnet, layer], "in_memory\intersect", "ALL", "", "LINE")
        arcpy.AddMessage("Exploding multipart features...")
        fishIntersect2 = arcpy.MultipartToSinglepart_management(fishIntersect, "in_memory\intersect2")
        arcpy.AddMessage("Calculating statistics for fishnet cells...")
        #create field name to be dissolved by (depends on name of output feature class)
        dissField = "FID_" + arcpy.Describe(outputLayer).baseName
        dissolve = arcpy.Dissolve_management(fishIntersect2, "in_memory\dissolve", dissField, [["Exemplare", "SUM"]], "SINGLE_PART", "DISSOLVE_LINES")

        arcpy.AddMessage("Calculating threshold for RNA category...")
        table_as_array = arcpy.da.FeatureClassToNumPyArray(dissolve, ["SUM_Exemplare"])
        #percentile1 = np.percentile(table_as_array["SUM_Exempl"], 70)
        
        #sort in descending order and build cumulative sum
        exemplare_sorted = np.sort(table_as_array["SUM_Exemplare"])[::-1]
        cumsum = np.cumsum(exemplare_sorted)
        #threshhold value
        threshold = np.amax(cumsum) * thpercentage
        #calculate difference between cumsum array and threshold value
        #then get index of minimum value in order to extract kategorie threshold
        #from exemplare array
        diff = np.abs(cumsum - threshold)
        minindex = np.argmin(diff)
        katthreshold = exemplare_sorted[minindex]
        
                
        arcpy.AddMessage("Updating fishnet layer with statistics information...")
        #add field for ddp page name
        arcpy.AddField_management(fishnet, "EXEMPLARE", "SHORT")
        arcpy.AddField_management(fishnet, "KATEGORIE", "TEXT", 50)
                                          
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
                return 1
            else:
                return 0

        #Update Cursor  
        update_fields = ["EXEMPLARE", "KATEGORIE"]
        in_field = "FID"

        update_fields.insert(0, in_field)  
        with arcpy.da.UpdateCursor(fishnet, update_fields) as urows:  
            for row in urows:  
                if row[0] in path_dict:  
                    row[1] = path_dict[row[0]][0]
                    row[2] = addCategory(row[1], katthreshold)
                else:
                    row[1] = 0
                    row[2] = 0
                    
                urows.updateRow(row)  
          
        return
