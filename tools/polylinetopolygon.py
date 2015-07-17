import arcpy
import os

class PolylineToPolygon(object):
    def __init__(self):
        self.label = "PolylineToPolygon"
        self.description = "Polyline to Polygon conversion using shaply"
        self.canRunInBackground = False

    def getParameterInfo(self):
    
	#Input feature layer
	in_features = arcpy.Parameter(
		displayName="Input Feature Layer",
		name="in_features",
		datatype="GPFeatureLayer",
		parameterType="Required",
		direction="Input")
		
	in_features.filter.list = ["Line"]
	
	#Field to use for description
	out_features = arcpy.Parameter(
		displayName="Output Feature Layer",
		name="pf_features",
		datatype="GPFeatureLayer",
		parameterType="Required",
		direction="Input")
	
	parameters = [in_features,out_features]
        
	return parameters

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):

        return

    def updateMessages(self, parameters):
        
        return

    def execute(self, parameters, messages):
	
	return
