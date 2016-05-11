class CalculateArea(object):
    """Implementation for CalculateArea.button (Button)"""
    def __init__(self):
        self.enabled = True
        self.checked = False
    def onClick(self):
        try:
            #local vars
            fieldName1 = "AREA_HA"
            fieldName2 = "AREA_QM"
            fieldPrecision = 15 #length of field over all
            fieldScale = 2      #number of decimal places

            mxd = arcpy.mapping.MapDocument("CURRENT")
            toclayer = pythonaddins.GetSelectedTOCLayerOrDataFrame()
            #get list with kields of selected layer
            existfield1 = arcpy.ListFields(toclayer, "AREA_HA")
            existfield2 = arcpy.ListFields(toclayer, "AREA_QM")

            #get computer name
            node_name = os.environ["COMPUTERNAME"]
            #get shape file path
            desc = arcpy.Describe(toclayer)
            shp_path = desc.path
            #check if shape file is locked by other node than the one of the user
            strlocks, listlocks = ListLocks(shp_path)

            #isnotlockedbool = arcpy.TestSchemaLock(toclayer)
            islockedmessage = "Could not add field. Layer: " + str(toclayer) + " is locked by the\
            user(s):\n" + strlocks

            #add fields to table of shapefile if not already existant
            if len(listlocks) > 1:  #isnotlockedbool:
               lockedmessage = pythonaddins.MessageBox(islockedmessage, "Locked", 0)
               print(lockedmessage)
            else:
                if len(existfield1) != 1:
                    arcpy.AddField_management(toclayer, fieldName1, "FLOAT", fieldPrecision, fieldScale)
                else:
                    fieldexistsmsg1 = "Field: " + fieldName1 + " already exists."
                if len(existfield2) != 1:
                     arcpy.AddField_management(toclayer, fieldName2, "FLOAT", fieldPrecision, fieldScale)
                else:
                    fieldexistsmsg2 = "Field: " + fieldName2 + " already exists."

            #calculate geometry
            arcpy.CalculateField_management(toclayer, fieldName1, "!SHAPE.AREA@HECTARES!", "PYTHON")
            arcpy.CalculateField_management(toclayer, fieldName2, "round(!SHAPE.AREA@SQUAREMETERS!, 2)", "PYTHON")

        except Exception, e:
            #if error occurs, print line number and error message
            import traceback, sys
            tb = sys.exc_info()[2]
            print("Line %i" % tb.tb_lineno)
            print(e.message)

        pass
        
