import arcpy
import os

class KartenserieToPng(object):
    def __init__(self):
        self.label = "KartenSerieToPng"
        self.description = "Export Kartenserie to PNG"
        self.canRunInBackground = False

    def getParameterInfo(self):
    
	#output path
	out_path = arcpy.Parameter(
		displayName="Output Path",
		name="out_path",
		datatype="DEFile",
		parameterType="Required",
		direction="Output")
	
	parameters = [out_path]
        
	return parameters

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):

        return

    def updateMessages(self, parameters):
        
        return

    def execute(self, parameters, messages):
        out = parameters[0].valueAsText
        
        mxd = arcpy.mapping.MapDocument("CURRENT")

        for pageNum in range(1, mxd.dataDrivenPages.pageCount + 1):
           mxd.dataDrivenPages.currentPageID = pageNum
           arcpy.mapping.ExportToPNG(mxd, out + str(pageNum) + ".png")
        del mxd

	return
