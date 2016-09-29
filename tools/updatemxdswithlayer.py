import arcpy
import os
import glob
import re

class UpdateMXDswithLayer(object):
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

        in_mxd = arcpy.Parameter(
            displayName="Input mxds",
            name="in_mxd",
            datatype="DEMapDocument",
            parameterType="Required",
            direction="Input",
            multiValue=True)

        # #field name to append to shapefiles attribute table
        # field_name = arcpy.Parameter(
        #     name="field_text",
        #     displayName="Field Name",
        #     datatype="GPString",
        #     parameterType="Required",
        #     direction="Input")
        #
        # default_val_bool = arcpy.Parameter(
        #         displayName="Use shapefile name as default value for new field?",
        #         name="default_val_bool",
        #         datatype="GPBoolean",
        #         parameterType="optional",
        #         direction="Input")
        #
        # default_val_bool.value = "True"
        #
        # default_val_txt = arcpy.Parameter(
        #         displayName="Default value to be used instead of layer name.",
        #         name="default_val_txt",
        #         datatype="GPString",
        #         parameterType="optional",
        #         enabled="False",
        #         direction="Input")
        #
        # merge_chkbox = arcpy.Parameter(
        #         displayName="Merge shapefiles after appending field?",
        #         name="merge_bool",
        #         datatype="GPBoolean",
        #         parameterType="optional",
        #         direction="Input")
        #
        # merge_chkbox.value = "True"

        #out_features = arcpy.Parameter(
        #    displayName="Buffer Output Feature",
        #    name="buffer_out",
        #    datatype="GPFeatureLayer",
        #    parameterType="optional",
        #    direction="Output")
        

        parameters = [in_features, in_mxd]
            
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
        in_mxd = parameters[1].valueAsText
        in_mxd = in_mxd.split(";")

        def make_dir(path):
            try:
                os.makedirs(path)
            except OSError:
                if not os.path.isdir(path):
                    raise

        #remove files by pattern
        def del_files(dir, pattern):
            for f in os.listdir(dir):
    	        if re.search(pattern, f):
    		        os.remove(os.path.join(dir, f))



        user = os.environ.get("USERNAME")

        basepath = "C:\\Users\\" + user + "\\Documents\\ArcGIS\\scratch\\"

        for nmxd in in_mxd:
            arcpy.AddMessage("Adding layer(s) to project :" + str(nmxd))
            mapdoc = arcpy.mapping.MapDocument(nmxd)
            df = arcpy.mapping.ListDataFrames(mapdoc, "Layers")[0]
            #loop through all layer
            for lyr in in_features:
                lyr_path = basepath + lyr + ".lyr"
                if not os.path.isfile(lyr_path):
                    arcpy.SaveToLayerFile_management(lyr, lyr_path, "RELATIVE")

                new_layer = arcpy.mapping.Layer(lyr_path)
                #adding layer to project
                arcpy.mapping.AddLayer(df, new_layer, "TOP")

            mapdoc.save()

        del nmxd, new_layer, mapdoc

        # clean up lyr files
        #del_files(basepath, "*.lyr")
        delfiles = basepath + "*.lyr"
        for f in glob.glob(delfiles):
            os.remove(f)
       #
        arcpy.AddMessage("Done")
       #
       #  del mxd, df  #,new_layer

	return

