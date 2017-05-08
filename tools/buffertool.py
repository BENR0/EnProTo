import arcpy

class MultiPurposeBufferTool(object):
    def __init__(self):
        self.label = "MultiPurposeBufferTool"
        self.description = "Creates multiple buffers around (multiple) feature layers selects" + \
        "features from species layer(s) contained in these buffers and exports" + \
        "attribute tables of these"
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

        out_features = arcpy.Parameter(
            displayName="Buffer Output Feature",
            name="buffer_out",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Output")
        
        #buffer ranges list
        buffer_ranges = arcpy.Parameter(
            name="buffer_ranges",
            displayName="Puffer Radien",
            datatype="GPString",
            parameterType="Required",
            direction="Input",
            multiValue=True)
            
        buffer_ranges.filter.type = "ValueList"
        buffer_ranges.filter.list = [100,200,250,300,500,1000,1500,2000,2500,3000,4000,5000,6000,7000,8000,9000,10000]
        

        parameters = [in_features,out_features,buffer_ranges]
            
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
        df = arcpy.mapping.ListDataFrames(mxd)[0]
		
    	in_features = parameters[0].valueAsText
        in_features = in_features.split(";")
    	out_features = parameters[1].valueAsText
    	buffer_ranges = parameters[2].valueAsText
        buffer_ranges = buffer_ranges.split(";")
        
        #merge layers if in_features list > 1
        if len(in_features) > 1:
            arcpy.AddMessage("Merging input layers...")
            mem_merge = arcpy.Merge_management(in_features, "in_memory\merge")

        #init list for storing buffer for each range
        tmp_buffers = []
        iter = 0
        #create buffer for each range
        for range in buffer_ranges:
            arcpy.AddMessage("Creating buffer with range " + range)
            tmp_memory_path = r"in_memory\buffer_" + range
            tmp_buffers.append(arcpy.Buffer_analysis(mem_merge, tmp_memory_path, range, "FULL", "ROUND", "ALL"))
            arcpy.AddField_management(tmp_buffers[iter], "DISTANCE", "LONG", 10)
            arcpy.CalculateField_management(tmp_buffers[iter], "DISTANCE", range, "PYTHON")
            #increment counter
            iter += 1


        #lst = arcpy.ListFiles("*.shp")
        arcpy.AddMessage("Merging buffers...")
        arcpy.Merge_management(tmp_buffers, out_features)
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
        arcpy.Delete_management("in_memory")
        #clean up variables
        del mxd, df, tmp_buffers #,new_layer


        #TODO
        #- add button in toolbar
        #- automatically add layer to project
        #- add style to layer




       # for dist in buffer_ranges:
            #Buffer_analysis (in_features, out_feature_class, buffer_distance_or_field, {line_side}, {line_end_type}, {dissolve_option}, {dissolve_field})
        #    arcpy.Buffer_analysis("roads", "C:/output/majorrdsBuffered", dist, "FULL", "ROUND", dissolve, dissolve_field}
        

	return

