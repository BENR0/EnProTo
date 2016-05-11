class BatchReproject(object):
    """Implementation for BatchReproject.button (Button)"""
    def __init__(self):
        self.enabled = True
        self.checked = False
    def onClick(self):

        mxd = arcpy.mapping.MapDocument("current")
        df = arcpy.mapping.ListDataFrames(mxd)[0]

        #data frame projection
        try:
            outcs = df.spatialReference
        except:
            err_dfcs = pythonaddin.MessageBox("Data frame has no coordinate system assigned.", "Error", 0)
            print(err_dfcs)

        #check which coordsystem df uses and create tag for filename
        if "UTM" in outcs.name:
            coordtag = "UTM"
        elif "Gauss_Zone" in outcs.name:
            coordtag = "GK"
        else:
            coordtag = outcs.PCSCode

            #iterate over all layers in toc
        try:
            for infc in arcpy.mapping.ListLayers(mxd): #arcpy.ListFeatureClasses(mxd):
                # Determine if the input has a defined coordinate system,
                # can't project it if it does not
                indesc = arcpy.Describe(infc)
                insc = indesc.spatialReference

                if indesc.spatialReference.Name == "Unknown":
                    print ("skipped this fc due to undefined coordinate system: " + infc)
                else:
                    # Determine the new output feature class path and name
                    #get path of current feature class and append coord system
                    infcpath = infc.dataSource
                    #split path from extension
                    infcpath = os.path.splitext(infcpath)
                    #create coordsystem and extension
                    extension = coordtag + ".shp"
                    outfc = os.path.join(infcpath[0], extension)
                    #get list of possible transformations

                    trafolist = arcpy.ListTransformations(insc, outcs)
                    if len(trafolist) > 0:
                        #run project tool with projection of data frame and apply transformation
                        #Project_management (in_dataset, out_dataset, out_coor_system, {transform_method},
                        #{in_coor_system}, {preserve_shape}, {max_deviation})
                        arcpy.Project_management(infc, outfc, outcs, trafolist[0])
                    else:
                        arcpy.Project_management(infc, outfc, outcs) 
                    
                    # check messages
                    print(arcpy.GetMessages())
                    
        except arcpy.ExecuteError:
            print(arcpy.GetMessages(2))
            
        except Exception as ex:
            print(ex.args[0])

        pass
        
