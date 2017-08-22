class BatchReproject(object):
    """Implementation for BatchReproject.button (Button)"""
    def __init__(self):
        self.enabled = True
        self.checked = False
    def onClick(self):
        #logging
        log_use(str(self.__class__.__name__))


        mxd = arcpy.mapping.MapDocument("current")
        df = arcpy.mapping.ListDataFrames(mxd)[0]

        #pop up message box to query for archiving of old layers
        archive = pythonaddins.MessageBox('Move old layers to archive after reprojecting?', 'INFO', 4)
        print(archive)

        #data frame projection
        try:
            outcscode = df.spatialReference.PCSCode
            outcs = df.spatialReference
        except:
            err_dfcs = pythonaddin.MessageBox("Data frame has no coordinate system assigned.", "Error", 0)
            print(err_dfcs)

        GK2 = "31466"
        GK3 = "31467"
        GK4 = "31468"
        GK5 = "31469"
        #NZ-E EPSG Codes
        utmn31NZ = "5651"
        utmn32NZ = "5652"
        utmn33NZ = "5653"
        # "normal" UTM Codes
        utmn31 = "25831"
        utmn32 = "25832"
        utmn33 = "25833"
        wgs = "4326"
        gt = "DHDN_To_ETRS_1989_8_NTv2"
        gt1 = "ETRS_1989_To_WGS_1984"
        gt2 = "DHDN_To_WGS_1984_4_NTv2"
        #gt = "DHDN_to_WGS_1984_4_NTv2 + ETRS_1989_to_WGS_1984"
        trafoDict = {GK2: gt2, GK3: gt2, GK4: gt2, GK5: gt2, utmn31NZ: gt1, utmn32NZ: gt1, utmn33NZ: gt1, utmn31: gt1, utmn32: gt1, utmn33:gt1}


        if str(outcscode) in [utmn31, utmn32, utmn33, utmn31NZ, utmn32NZ, utmn33NZ]:
            coordtag = "_UTM"
        elif str(outcscode) in [GK2, GK3, GK4, GK5]:
            coordtag = "_GK"
        else:
            outcs_msg = "Please choose one of the following coordinate systems for the data frame: " + trafoDict.keys()
            err_outcs = pythonaddin.MessageBox(outcs_msg, "Error", 0)
            print(err_outcs)

        mxdpath = os.path.splitext(mxd.filePath)[0]
        logfile = mxdpath + "_trafo.log"
        #iterate over all layers in toc
        try:
            tfile = open(logfile, 'w')
            for infc in arcpy.mapping.ListLayers(mxd): #arcpy.ListFeatureClasses(mxd):
                # Determine if the input has a defined coordinate system,
                # can't project it if it does not
                indesc = arcpy.Describe(infc)
                insc = indesc.spatialReference
                #log trafos
                log = str(infc) + str(insc.PCSCode) + " ->"
                if indesc.spatialReference.Name == "Unknown":
                    print ("Skipped this fc due to undefined coordinate system: " + infc)
                    log = log + " skipped\n"
                    #write log
                    logfile.write(log)
                    continue
                elif insc == outcs:
                    log = log + " no need for reprojection (coordinate systems are the same.\n"
                    #write log
                    logfile.write(log)
                    continue
                else:
                    # Determine the new output feature class path and name
                    #get path of current feature class and append coord system
                    infcpath = infc.dataSource
                    #split path from extension
                    infcpath = os.path.splitext(infcpath)
                    #create coordsystem and extension
                    extension = coordtag + ".shp"
                    outfc = infcpath[0] + extension
                    #get list of possible transformations
                    trafolist = arcpy.ListTransformations(insc, outcs)
                    print(outfc)

                    if len(trafolist) > 0:
                        #run project tool with projection of data frame and apply transformation
                        #Project_management (in_dataset, out_dataset, out_coor_system, {transform_method},
                        #{in_coor_system}, {preserve_shape}, {max_deviation})
                        newlayerpath = arcpy.Project_management(infc, outfc, outcs, trafolist[0])
                        log = log + " " + str(outfc) + " " + "(" + trafolist[0] + ")\n"
                    else:
                        newlayerpath = arcpy.Project_management(infc, outfc, outcs)
                        log = log + " " + str(outfc) + " " + "(No transformation used)\n"


                    #apply style of old layer to new layer
                    newlayername = os.path.splitext(os.path.basename(str(newlayerpath)))[0]
                    newlayer = arcpy.mapping.ListLayers(mxd, newlayername)[0]
                    arcpy.ApplySymbologyFromLayer_management(newlayer, infc)

                    #write log
                    tfile.write(log)

                    #remove old layer from project
                    arcpy.mapping.RemoveLayer(df, infc)

                    #check messages
                    print(arcpy.GetMessages())

            tfile.close()

        except arcpy.ExecuteError:
            print(arcpy.GetMessages(2))

        except Exception as ex:
            print(ex.args[0])

        pass
        
