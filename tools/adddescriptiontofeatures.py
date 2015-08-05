import arcpy
import os

class AddDescriptionToFeatures(object):
    def __init__(self):
        self.label = "AddDescriptionToFeatures"
        self.description = "Adds description to features based on Column of "+ \
		"Attribute Table (e.g. lat. names to fauna features)"
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
	description_field = arcpy.Parameter(
		displayName="Attribute Table Field to be used as Description",
		name="description_field",
		datatype="Field",
		parameterType="Required",
		direction="Input")
		
        description_field.parameterDependencies = [in_features.name]
		
	#Field to use for sorting to unique values
	sorting_field = arcpy.Parameter(
		displayName="Attribute Table Field to be used for sorting",
		name="sorting_field",
		datatype="Field",
		parameterType="Required",
		direction="Input")
	
        sorting_field.parameterDependencies = [in_features.name]
	
	parameters = [in_features,description_field,sorting_field]
        
	return parameters

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):

        return

    def updateMessages(self, parameters):
        
        return

    def execute(self, parameters, messages):
        from itertools import chain
		
        features = parameters[0].valueAsText
        s_field = parameters[2].valueAsText
        d_field = parameters[1].valueAsText

        ##snippets from standalone script
        mxd = arcpy.mapping.MapDocument("current")
        lyr = arcpy.mapping.ListLayers(mxd,features)[0]

	def unique_values(table, field1,field2):
		with arcpy.da.SearchCursor(table, [field1,field2]) as cursor:
			return sorted({(row[0],row[1]) for row in cursor})
		
		
        desc_list = unique_values(lyr,s_field,d_field)
    	desc_list = map(list,desc_list)
    	desc_list = list(chain.from_iterable(desc_list))

        #print desc_list 

    	if lyr.symbologyType == "UNIQUE_VALUES":
			#lyr.symbology.valueField = s_field
			lyr.symbology.classDescriptions = desc_list[1::2]
			lyr.symbology.showOtherValues = False

        return
