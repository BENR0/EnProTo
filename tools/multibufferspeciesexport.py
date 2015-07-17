import arcpy
import os

class MultiBufferSpeciesExport(object):
    def __init__(self):
        self.label = "MultiBufferSpeciesExport"
        self.description = "Creates multiple buffers around feature selects" + \
        "features from species layer contained in these buffers and exports" + \
        "attribute tables of these"
        self.canRunInBackground = False

    def getParameterInfo(self):
    
	#Input feature layer
	vorhaben = arcpy.Parameter(
		displayName="Vorhaben Feature Layer",
		name="in_features",
		datatype="GPFeatureLayer",
		parameterType="Required",
		direction="Input")
		
	buffer = arcpy.Parameter(
		displayName="Buffer Output Feature",
		name="buffer_out",
		datatype="GPFeatureLayer",
		parameterType="Required",
		direction="Output")
		
	vorhaben.filter.list = ["Polygon"]
	
	species = arcpy.Parameter(
		displayName="Arten Feature Layer",
		name="in_features",
		datatype="GPFeatureLayer",
		parameterType="Required",
		direction="Input")
		
	species.filter.list = ["Point"]

    #buffer ranges list
	buffer_ranges = arcpy.Parameter(
		displayName="Puffer Radien",
		name="buffer_ranges",
		datatype="GPTable",
		parametertype="Required",
		direction="Input")
		
	buffer_ranges.fiter.type = "ValueList"
	buffer_ranges.filter.list = [100,200,250,300,500,1000,1500,2000,2500,3000,4000,5000,6000,7000,8000,9000,10000]
	
	species_table = arcpy.Parameter(
		displayName="Arten Tabelle Ausgabe",
		name="species_table",
		datatype="DETable",
		parameterType="Required",
		direction="Output")

	parameters = [vorhaben,buffer,species,buffer_ranges,species_table]
        
	return parameters

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):

        return

    def updateMessages(self, parameters):
        
        return

    def execute(self, parameters, messages):
		mxd = arcpy.mapping.MapDocument("current")
		
		vorhaben = parameters[0].valueAsText
		buffer = parameters[1].valueAsText
		species = parameters[2].valueAsText
		buffer_ranges = parameters[3].valueAsText
		species_table = parameters[4].valueAsText
		
		#calculate buffers
		arcpy.MultipleRingBuffer_analysis(vorhaben,buffer,buffer_ranges,"meters", "","ALL")
		#apply distances layer style 
		#arcpy.ApplySymbologyFromLayer_management(buffer, "style source layer.lyr")
		
		#calculate field geometry (area)
		arcpy.AddField_management(buffer,"area_sm","DOUBLE") #add field with name "area_sm" to attribute table
		CursorFieldNames = ["SHAPE@AREA","area_sm"] #read are token from shape
		cursor = arcpy.da.UpdateCursor(buffer,CursorFieldNames)
		for row in cursor:
			AreaValue = row[0].area #read area value as double
			row[1] = AreaValue #write area value to field
			cursor.updateRow(row)
		del row,cursor #clean up cursor objects
		
		#select species in each buffer and output table
		#for feature make feature layermanagement
		#add field with largest buffer selected feature is contained in??
		#maketableview/ createtablemanagement
		
		
		
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

