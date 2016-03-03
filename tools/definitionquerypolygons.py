import arcpy
import pythonaddins

class DefinitionQueryPolygons(object):
    def __init__(self):
        self.label = "DefinitionQueryPolygons"
        self.description = "Create Polygons based on a field in selected layer for\
                use in data driven pages and definition query."
        self.canRunInBackground = False

    def getParameterInfo(self):
        in_lyr = arcpy.Parameter(
            displayName="Layer to which definition query will be applied",
            name="in_lyr",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Input")
            
        mapfield = arcpy.Parameter(
            displayName="Field on which definition query will be based",
            name="mapfield",
            datatype="Field",
            parameterType="Required",
            direction="Input")
        
        mapfield.parameterDependencies = [in_lyr.name]

        out_shp = arcpy.Parameter(
            displayName="Output Shapefile",
            name="out_shp",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Output")
        
        scale = arcpy.Parameter(
            displayName="Desired scale for map",
            name="scale",
            datatype="GPLong",
            parameterType="Required",
            direction="Input")
        

        parameters = [in_lyr, mapfield, out_shp, scale]
            
        return parameters

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        mxd = arcpy.mapping.MapDocument("current")
        df = arcpy.mapping.ListDataFrames(mxd)[0]
        #lyrs = arcpy.mapping.ListLayers(mxd)

        #vilayers = []
        #for lyr in lyrs:
            #if lyr.visible:
                #vilayers.append(lyr)

        #parameters[0].filter.list = vilayers

        parameters[3].value = df.scale

        return

    def updateMessages(self, parameters):
        
        return

    def execute(self, parameters, messages):
        #function to get center point of layer
        def layerCenter(lyr):
            lyrex = arcpy.Describe(lyr).extent
            cpX = lyrex.XMin + (lyrex.XMax - lyrex.XMin)/2
            cpY = lyrex.YMin + (lyrex.YMax - lyrex.YMin)/2
            return cpX, cpY

        #function for polygon corner coords
        def polyExtent(xrange, yrange, cpx, cpy):
            pXMin = cpx - xrange/2
            pYMin = cpy - yrange/2
            pXMax = cpx + xrange/2
            pYMax = cpy + yrange/2
            return arcpy.Extent(pXMin, pYMin, pXMax, pYMax)

        #function to create polygon
        def createPolygon(cornercoords):
            polyArray = arcpy.Array()
            polyArray.add(cornercoords.lowerLeft)
            polyArray.add(cornercoords.lowerRight)
            polyArray.add(cornercoords.upperRight)
            polyArray.add(cornercoords.upperLeft)
            polyArray.add(cornercoords.lowerLeft)
            return arcpy.Polygon(polyArray)

        def uniqueValues(table, field):
            with arcpy.da.SearchCursor(table, field) as cursor:
                return sorted({row[0] for row in cursor})

        #Input
        layer = parameters[0].valueAsText
        mapField = parameters[1].valueAsText
        blattschnitt = parameters[2].valueAsText
        scale = parameters[3].value

        #beginning of script
        mxd = arcpy.mapping.MapDocument("current")
        df = arcpy.mapping.ListDataFrames(mxd)[0]
        df_coord = df.spatialReference.PCSCode
        #get dataframe dimensions
        dfX, dfY = df.elementWidth * 0.01, df.elementHeight * 0.01
        arcpy.AddMessage(dfX)

        #calculate polygon length in map units
        polyX, polyY = dfX * scale, dfY * scale
        arcpy.AddMessage(polyX)

        #create polygon
        centerX, centerY = layerCenter(layer)
        polygon = createPolygon(polyExtent(polyX, polyY, centerX, centerY))

        #get values to map from attribute table
        values = uniqueValues(layer, mapField)
        #init list for polys
        polys = []
        for i in range(len(values)):
            polys.append(polygon)

        blattschnitte = arcpy.CopyFeatures_management(polys, blattschnitt)
        #set projection for new shape file
        arcpy.DefineProjection_management(blattschnitte, df_coord)
        #add field for ddp page name
        arcpy.AddField_management(blattschnitte, mapField, "TEXT", 100)
        arcpy.AddField_management(blattschnitte, "SCALE", "TEXT", 20)

        i = 0
        #populate field with items from value list
        with arcpy.da.UpdateCursor(blattschnitte, [mapField, "SCALE"]) as cursor:
            for row in cursor:
                row[0] = values[i]
                row[1] = str(scale)
                i += 1
                cursor.updateRow(row)

                
        result = arcpy.mapping.Layer(blattschnitt)
        #lyr = result.getOutput(0)
        arcpy.mapping.AddLayer(df, result, "AUTO_ARRANGE")
        return


