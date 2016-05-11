import arcpy

mxd = arcpy.mapping.MapDocument("current")
layer = arcpy.mapping.ListLayers(mxd)[0]
layer2 = arcpy.mapping.ListLayers(mxd)[1]
mastlayer = arcpy.mapping.ListLayers(mxd)[2]
fieldlist1 = ["FID"]
fieldlist2 = ["FID", "MA1", "MA2"]

with arcpy.da.SearchCursor(layer, fieldlist1) as cursor:
    for row in cursor:
         print(row[0])
         arcpy.SelectLayerByAttribute_management (layer,
                                           "NEW_SELECTION",
                                           "FID = {}".format(row[0]))
         # select by location CROSSED_BY_THE_OUTLINE_O
         arcpy.SelectLayerByLocation_management(mastlayer,
                                               "INTERSECT",
                                               layer,
                                               "0.02 kilometers",
                                               "NEW_SELECTION")
         where = "FID = " + str(row[0])
         #statt * masnummer spalte
         i = 0


         with arcpy.da.SearchCursor(mastlayer, ["TxtMemo"]) as cursor2:
            for row2 in cursor2:
                print(row2)
                with arcpy.da.UpdateCursor(layer2, fieldlist2, where) as cursor3:
                    for row3 in cursor3:
                        while i <= 1:
                            row3[i+1] = row2[0]
                            cursor3.updateRow(row3)
                            i+=1