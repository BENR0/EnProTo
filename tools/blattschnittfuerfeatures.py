import arcpy
import pythonaddins

class BlattschnittFuerFeatures(object):
    def __init__(self):
        self.label = "blattschnittfuerfeatures"
        self.description = "Create Blattschnitte based on features."
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
        #centerX, centerY = layerCenter(layer)


        #get values to map from attribute table
        #values = uniqueValues(layer, mapField)
        values = []
        #init list for polys
        polys = []


        with arcpy.da.SearchCursor(layer,[mapField,"SHAPE@XY"]) as cursor:
            for row in cursor:
                values.append(row[0])
                #create polygon with center at centroid of feature polygon
                polygon = createPolygon(polyExtent(polyX, polyY, row[1][0], row[1][1]))
                polys.append(polygon)

        blattschnitte = arcpy.CopyFeatures_management(polys, blattschnitt)
        #set projection for new shape file
        arcpy.DefineProjection_management(blattschnitte, df_coord)
        #add field for ddp page name
        arcpy.AddField_management(blattschnitte, mapField, "TEXT", 100)
        arcpy.AddField_management(blattschnitte, "SCALE", "TEXT", 20)

        i = 0
        #populate field with items from value list
        with arcpy.da.UpdateCursor(blattschnitte, [Id, mapField, "SCALE"]) as cursor:
            for row in cursor:
                row[0] = i + 1
                row[1] = values[i]
                row[2] = str(scale)
                i += 1
                cursor.updateRow(row)

                
        result = arcpy.mapping.Layer(blattschnitt)
        #lyr = result.getOutput(0)
        arcpy.mapping.AddLayer(df, result, "AUTO_ARRANGE")

        # # ---------------------------------------------------------------------------
        # # PAGE MAKER
        # # http://gis.stackexchange.com/questions/154975/minimising-number-of-dynamic-pages-to-map-scattered-points-using-arcgis-desktop/168058#168058
        # # ---------------------------------------------------------------------------
        # # Import arcpy module
        # import arcpy, traceback, os, sys
        # from arcpy import env
        #
        # width=650
        # height=500
        #
        # try:
        #     def showPyMessage():
        #             arcpy.AddMessage(str(time.ctime()) + " - " + message)
        #     mxd = arcpy.mapping.MapDocument("CURRENT")
        #     points = arcpy.mapping.ListLayers(mxd,"points")[0]
        #     pgons = arcpy.mapping.ListLayers(mxd,"pages")[0]
        #
        #     g=arcpy.Geometry()
        #     geometryList=arcpy.CopyFeatures_management(points,g)
        #     geometryList=[p.firstPoint for p in geometryList]
        #     curT = arcpy.da.InsertCursor(pgons,"SHAPE@")
        #     while True:
        #         nPoints=len(geometryList)
        #         small=[geometryList.pop(0)]
        #         for p in geometryList:
        #             small.append(p)
        #             mPoint=arcpy.Multipoint(arcpy.Array(small))
        #             ext=mPoint.extent
        #             cHeight=ext.height
        #             cWidth=ext.width
        #             if cHeight>height or cWidth>width:
        #                 small.remove(p)
        #         mPoint=arcpy.Multipoint(arcpy.Array(small))
        #         ext=mPoint.extent
        #         xC=(ext.XMin+ext.XMax)/2
        #         yC=(ext.YMin+ext.YMax)/2
        #         LL=arcpy.Point (xC-width/2,yC-height/2)
        #         UL=arcpy.Point (xC-width/2,yC+height/2)
        #         UR=arcpy.Point (xC+width/2,yC+height/2)
        #         LR=arcpy.Point (xC+width/2,yC-height/2)
        #         pgon=arcpy.Polygon(arcpy.Array([LL,UL,UR,LR]))
        #         curT.insertRow((pgon,))
        #         short=filter(lambda x: x not in small,geometryList)
        #         arcpy.AddMessage('Grabbed %i points, %i to go' %(len(small),len(short)))
        #         if len(short)==0: break
        #         geometryList=short[:]
        #     del mxd
        # except:
        #     message = "\n*** PYTHON ERRORS *** "; showPyMessage()
        #     message = "Python Traceback Info: " + traceback.format_tb(sys.exc_info()[2])[0]; showPyMessage()
        #     message = "Python Error Info: " +  str(sys.exc_type)+ ": " + str(sys.exc_value) + "\n"; showPyMessage()


        return


