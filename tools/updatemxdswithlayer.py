import arcpy
import re

class updatemxdswithlayer(object):
    def __init__(self):
        self.label = "UpdateMXDswithLayer"
        self.description = "Adds layer to multiple mxds"
        self.canRunInBackground = False

    def getParameterInfo(self):
        #Input feature layer
        in_features = arcpy.Parameter(
            displayName="Input feature layers",
            name="in_features",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Input",
            multiValue=True)

        #field name to append to shapefiles attribute table
        field_name = arcpy.Parameter(
            name="field_text",
            displayName="Field Name",
            datatype="GPString",
            parameterType="Required",
            direction="Input")

        default_val_bool = arcpy.Parameter(
                displayName="Use shapefile name as default value for new field?",
                name="default_val_bool",
                datatype="GPBoolean",
                parameterType="optional",
                direction="Input")

        default_val_bool.value = "True"

        default_val_txt = arcpy.Parameter(
                displayName="Default value to be used instead of layer name.",
                name="default_val_txt",
                datatype="GPString",
                parameterType="optional",
                enabled="False",
                direction="Input")

        merge_chkbox = arcpy.Parameter(
                displayName="Merge shapefiles after appending field?",
                name="merge_bool",
                datatype="GPBoolean",
                parameterType="optional",
                direction="Input")

        merge_chkbox.value = "True"

        out_features = arcpy.Parameter(
            displayName="Buffer Output Feature",
            name="buffer_out",
            datatype="GPFeatureLayer",
            parameterType="optional",
            direction="Output")
        

        parameters = [in_features, field_name, default_val_bool, default_val_txt, merge_chkbox, out_features]
            
        return parameters

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        # if parameters[3].valueAsText:
            # if parameters[3].value == True:
                # parameters[4].enabled = False
            # else:
                # parameters[4].enabled = True

        return

    def updateMessages(self, parameters):
        
        return

    def execute(self, parameters, messages):
        mxd = arcpy.mapping.MapDocument("current")
        df = arcpy.mapping.ListDataFrames(mxd)[0]
		
        in_features = parameters[0].valueAsText
        in_features = in_features.split(";")
        field_name = parameters[1].valueAsText
        #change field name to upper case
        field_name_upper = field_name.upper()
        default_val_bool = parameters[2].valueAsText
        default_val_txt = parameters[3].valueAsText
        merge_chkbox = parameters[4].valueAsText
        out_features = parameters[5].valueAsText

        #local vars
        #fieldName1 = "AREA_HA"
        #fieldName2 = "AREA_QM"
        fieldPrecision = 200 #length of field over all
        #fieldScale = 2      #number of decimal places
        fieldtype = "TEXT"

        #init list for layers to be merged
        merge_layers = []
        



        import arcpy
        import arcpy.mapping
        import os
        import sys
        from arcpy import env
        import string

        env.workspace = r"M:\projects\mcag\Project_Site_Packet"
        for mxd in arcpy.ListFiles("*.mxd"):
            mapdoc = arcpy.mapping.MapDocument(r"M:\projects\mcag\Project_Site_Packet\\" + mxd)
            df = arcpy.mapping.ListDataFrames(mapdoc, "Layers")[0]
            addLayer = arcpy.mapping.Layer(r"M:\projects\mcag\Project_Site_Packet\Subject Property.lyr")
            arcpy.mapping.AddLayer(df ,addLayer ,"TOP")
            mapdoc.save()
        del mxd, addLayer, mapdoc






        #merge layers if in_features checkbox is set to true
       # if merge_chkbox == "True":
        arcpy.AddMessage("Merging input layers...")
        arcpy.Merge_management(merge_layers, out_features)

        arcpy.AddMessage("Done")

        del mxd, df  #,new_layer


        #TODO
        #- add button in toolbar
        #- automatically add layer to project

	return

