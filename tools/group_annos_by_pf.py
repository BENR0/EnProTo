import arcpy
import os

class GroupAnnosByPF(object):
    def __init__(self):
        self.label = "GroupAnnosByPF"
        self.description = "Creates and groups Annotations by PF"
        self.canRunInBackground = False

    def getParameterInfo(self):
    
	#Input feature layer
	in_features = arcpy.Parameter(
		displayName="Input Feature Layer",
		name="in_features",
		datatype="GPFeatureLayer",
		parameterType="Required",
		direction="Input")
		
	in_features.filter.list = ["Point"]
	
	#Field to use for description
	pf_features = arcpy.Parameter(
		displayName="Probeflächen Feature",
		name="pf_features",
		datatype="GPFeatureLayer",
		parameterType="Required",
		direction="Input")
	
	parameters = [in_features,pf_features]
        
	return parameters

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):

        return

    def updateMessages(self, parameters):
        
        return

    def execute(self, parameters, messages):
	
		in_features = parameters[0].valueAsText
		pf_features = parameters[1].valueAsText
		
		mxd = arcpy.mapping.MapDocument("current")
		lyr = arcpy.mapping.ListLayers(mxd,in_features)[0]
		pf = arcpy.mapping.ListLayers(mxd,pf_features)[0]
		
		
        #lyr = arcpy.mapping.ListLayers(mxd,"Rommelsbach_PF_Rept_Tagf")
        #point_lyr = arcpy.mapping.ListLayers(mxd,"Tagfalter_Projektnummer")
        #field1 = ""
        #field2 = ""
        #new_text = ""

        #add field to species attribute table
		arcpy.AddField_management(lyr,"Annotation","TEXT")

		with arcpy.da.UpdateCursor(lyr,("Abk","Annotation")) as cursor:
			for row in cursor:
				print(row[0])
				SQL = "Abk == %s"%str(row[0])
				arcpy.MakeFeatureLayer_management(lyr,"tmp_lyr",SQL)
				arcpy.SelectLayerByLocation_management(point_lyr,"intersect",tmp_lyr)
				with arcpy.da.SearchCursor(point_lyr,[field1,field2]) as cursor2:
					for row2 in cursor2:
						new_text = new_text + str(row2[0]) + " (" + "<ITA>" + str(row2[1]) + "</ITA>" + ")\n"
						row[1] = new_text
						cursor.updateRow(row)
					del tmp_lyr

		return
