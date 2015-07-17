import arcpy
import os

class Legen_WaitForIt_Dary(object):
    def __init__(self):
        self.label = "Legen_WaitForIt_Dary"
        self.description = "Usefull features for things the Legend Wizard can not do"
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
	features = arcpy.Parameter(
		displayName="Other Input",
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
	
	return	
        
