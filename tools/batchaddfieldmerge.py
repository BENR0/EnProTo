import arcpy

class BatchAddFieldMerge(object):
    def __init__(self):
        self.label = "BatchAddFieldMerge"
        self.description = "Adds field to multiple shapefiles with optional default value"
        "and optional following merge"
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
        field_name = field_name.upper()
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

        for lyr in in_features:
            #get list with fields of selected layer
            existfield = arcpy.ListFields(lyr, field_name)
            #existfield2 = arcpy.ListFields(toclayer, "AREA_QM")
            print(str(lyr))

            #add fields to table of shapefile if not already existant
            if len(existfield) != 1:
                arcpy.AddMessage("Adding field to layer: " + str(lyr))
                arcpy.AddField_management(lyr, field_name, fieldtype, fieldPrecision) #for floats
                #use layer name as default value?
                #if default_val_bool == "True":
                arcpy.CalculateField_management(lyr, field_name, '"{0}"'.format(lyr), "PYTHON")
                #else:
                 #   arcpy.CalculateField_management(lyr, field_name, '"{0}"'.format(default_val_txt), "PYTHON")
                #add fieldScale
            else:
                arcpy.AddMessage("A field with the choosen name already exists in layer: " + str(lyr))

        #except Exception, e:
        ##if error occurs, print line number and error message
        #import traceback, sys
        #tb = sys.exc_info()[2]
        #print("Line %i" % tb.tb_lineno)
        #print(e.message)


        #merge layers if in_features checkbox is set to true
       # if merge_chkbox == "True":
        arcpy.AddMessage("Merging input layers...")
        arcpy.Merge_management(in_features, out_features)

        arcpy.AddMessage("Done")

        #create new layer from output
        #arcpy.AddMessage(out_features)
        #new_layer = arcpy.mapping.Layer(out_features)
        ##adding layer to project
        #arcpy.mapping.AddLayer(df, new_layer, "TOP")
        ##refresh view and toc
        #arcpy.RefreshActiveView()
        #arcpy.RefreshTOC()

        #clear up in_memory workspace
        #arcpy.Delete_management("in_memory")
        #clean up variables
        del mxd, df  #,new_layer


        #TODO
        #- add button in toolbar
        #- automatically add layer to project

	return

