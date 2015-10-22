import arcpy
import os

class BatchConvertPDFToTif(object):
    def __init__(self):
        self.label = "BatchConvertPDFToTif"
        self.description = "Convert all pdf files in directory to tif files."
        self.canRunInBackground = False

    def getParameterInfo(self):
        #Input directory
        in_dir = arcpy.Parameter(
			displayName="Input directory",
			name="in_dir",
			datatype="DEFolder",
			parameterType="Required",
			direction="Output")
            
        #Output directory
        out_dir = arcpy.Parameter(
			displayName="Output directory",
			name="out_dir",
			datatype="DEFolder",
			parameterType="Required",
			direction="Output")
        
        #set default resolution
        resolution = arcpy.Parameter(
            displayName="Resolution",
            name="resolution",
            datatype="GPString",
            parameterType="Optional",
            direction="Input")
        
        resolution.value = "250"
        
        #set default resolution
        page_number = arcpy.Parameter(
            displayName="Page number",
            name="page_number",
            datatype="GPString",
            parameterType="Optional",
            direction="Input")
        
        page_number.value = "1"

        parameters = [in_dir, out_dir, resolution, page_number]
            
        return parameters

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):

        return

    def updateMessages(self, parameters):
        
        return

    def execute(self, parameters, messages):
        in_d = parameters[0].valueAsText
        out_d = parameters[1].valueAsText
        res = parameters[2].valueAsText
        pnumber = parameters[3].valueAsText

        files += [each for each in os.listdir(in_d) if each.endswith('.pdf')]

        for file in files:
            arcpy.PDFToTIFF_conversion(in_pdf_file=in_d + "/" + str(file), 
                                       out_tiff_file=out_d + "/" + str(file) + ".tif", 
                                       pdf_password="", 
                                       pdf_page_number=pnumber, 
                                       clip_option="NO_CLIP", 
                                       resolution=res,
                                       color_mode="RGB_TRUE_COLOR",
                                       tiff_compression="LZW", 
                                       geotiff_tags="GEOTIFF_TAGS")

        return

