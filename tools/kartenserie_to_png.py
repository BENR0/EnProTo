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

#set default resolution
        resolution = arcpy.Parameter(
                 displayName="Resolution",
                 name="resolution",
                 datatype="DEString",
                 parameterType="Optional",
                 direction="Input"
                )

#check if field name exists and if so use it, then no input parameter is needed
        field_in_name = arcpy.Parameter(
                displayName="Use information of f_suffix field in file name",
                name="field_in_name",
                datatype="DEBoolean",
                parameterType="Optional",
                direction="Input"
                )
#add option to export to JPEG default to PNG
	
	parameters = [out_path, resolution, field_in_name]
        
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
        res = parameters[1].valueAsText
        file_suffix = parameters[2].valueAsText
        
        attrtable_field = "f_suffix"
        mxd = arcpy.mapping.MapDocument("CURRENT")

        for pageNum in range(1, mxd.dataDrivenPages.pageCount + 1):
            if not field_in_name:
                mxd.dataDrivenPages.currentPageID = pageNum
                final_path = out + "_" + str(pageNum) + ".png"
            else:
                cur = str(mxd.dataDrivenPages.pageRow.getValue(attrtable_field))
                final_path = out + "_" + cur + ".png")
            
            arcpy.mapping.ExportToPNG(mxd, final_path)

        del mxd

	return
