# -*- coding: utf-8 -*-
import arcpy
import os
import colorsys
import pyodbc
import pandas as pd
import numpy as np
from fieldexistsfunction import fieldExists


################################################
#beginn of toolbox class
################################################

class JoinASK(object):
    def __init__(self):
        self.label = "JoinASK"
        self.description = "Join ASK data to shape files."
        self.canRunInBackground = False

    def getParameterInfo(self):
        #Input feature layer
        in_features = arcpy.Parameter(
                displayName = "Layer to join the data to",
                datatype = "GPFeatureLayer",
                name = "in_features",
                parameterType = "Required",
                direction = "Input")

        mdbfile = arcpy.Parameter(
                displayName = "Database",
                name = "mdbfile",
                datatype = "DeFile",
                parameterType = "Required",
                direction = "Input")

        out_features = arcpy.Parameter(
                displayName = "Output Layer",
                name = "out_features",
                datatype = "GPFeatureLayer",
                parameterType = "Required",
                direction = "Output")


        parameters = [in_features, mdbfile, out_features]

        return parameters

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):

        return

    def updateMessages(self, parameters):

        return

    def execute(self, parameters, messages):

        layer = parameters[0].valueAsText
        mdbFile = parameters[1].valueAsText
        outfeatures = parameters[2].valueAsText

        #layer = r"\\VBOXSVR\virtualbox\ASK_Wurmloh\ASK_PUNKTE.shp"
        #mdbFile = r"\\VBOXSVR\virtualbox\ASK_wurmloh\ASK.mdb"
        #outfeatures = r"\\VBOXSVR\virtualbox\delete\ask_join.shp"

        #spatialRef = arcpy.Describe(layer).spatialReference
        spatialRef = arcpy.SpatialReference(31468)

        features = arcpy.da.FeatureClassToNumPyArray(layer,["id", "SHAPE@X", "SHAPE@Y"])
        dffeatures = pd.DataFrame(features)

        # legendDict = dict()
        # with arcpy.da.SearchCursor(toclayer, fieldlist) as cursor:
        #     for row in cursor:
        #         item = row[0] + ": " + row[1]
        #         if row[2] in legendDict:
        #             legendDict[row[2]]["items"].append(item)
        #         else:
        #             legendDict[row[2]] = {"items" : [item]} #, "color" : tuple(row[3].split(","))}



        #mdbFile = r"K:\TNL_E\Radweg\Selb\05_GIS\av_daten\04_Bestandsdaten\ASK_Selb\ASK.mdb"
        connectionString = "Driver={Microsoft Access Driver (*.mdb)};Dbq=%s" % mdbFile
        dbConnection = pyodbc.connect(connectionString, charset = "utf8")
        sql = "select * from ask_art"
        ################################################
        #cursor.execute(sql)
        #rows = cursor.fetchall()
        # for row in cursor.columns(table="ask_art"):
        #     print "Field name: " + str(row.column_name)
        #     print "Type: " + str(row.type_name)
        #     print "Width: " + str(row.column_size)
        ################################################


        #read sql query as pandas data frame
        dfmdb = pd.read_sql(sql, dbConnection)

        mergedData = pd.merge(dfmdb, dffeatures, on = "id", how = "inner")
        mergedData.fillna(0, inplace = True)
        #mergedData.to_csv("test.csv", encoding = "utf-8")
        #arcpy.AddMessage(mergedData)
        print(mergedData)
        #arcpy.AddMessage(pd.merge(dfmdb, dffeatures, on = "id", how = "inner"))



        x = np.array(np.rec.fromrecords(mergedData.values))
        names = mergedData.dtypes.index.tolist()
        strnames = [str(i) for i in names]
        x.dtype.names = tuple(strnames)
        #arcpy.da.NumPyArrayToTable(x, r'E:\Workspace\testData.gdb\testTable')
        arcpy.da.NumPyArrayToFeatureClass(x, outfeatures, ("SHAPE@X", "SHAPE@Y"), spatialRef)

        pass


if __name__ == "__main__":

    tool = JoinASK()
    tool.execute(tool.getParameterInfo(), None)


