class ListAllLocksForLayers(object):
    """Implementation for ListAllLocksForLayers.button (Button)"""
    def __init__(self):
        self.enabled = True
        self.checked = False
    def onClick(self):
        import logging

        #usage logging
        log_use(str(self.__class__.__name__))

        mxd = arcpy.mapping.MapDocument("CURRENT")

        lyrs = arcpy.mapping.ListLayers(mxd)
        out_msg = ""

        #HUNB20: Isgard
        #HUNB10: Benjamin
        #HUPC28: Maren
        #HUPC24: Yvonne
        #HUPC07: Jann
        #HUPC30: Andi
        for lyr in lyrs:
            if not lyr.isGroupLayer:                      #Is layer a group layer
                # print(lyr.isGroupLayer)
                # for glyr in arcpy.mapping.ListLayers(lyr): #loop layer in group layer
                #     if glyr != lyr:
                #         out_msg += str(lyr) + " is locked by user(s):\n"
                #         #get lyr path
                #         desc = arcpy.Describe(lyr)
                #         lyr_path = desc.path + "\\" + str(lyr) +  ".shp"
                #         #get all locks for this layer and append to msg string
                #         strlocks, listlocks = ListLocks(lyr_path)
                #         out_msg += strlocks + "\n"
           # else:
                out_msg += str(lyr) + " is locked by user(s):\n"
                #get lyr path
                try:
                    desc = arcpy.Describe(lyr)
                    lyr_path = desc.path + "\\" + str(lyr) +  ".shp"
                    #get all locks for this layer and append to msg string
                    strlocks, listlocks = ListLocks(lyr_path)
                except:
                    pass

                out_msg += strlocks + "\n"
        
        if out_msg == "":
            out_msg = "No lock on any layer found."
        
        result = pythonaddins.MessageBox(out_msg, "Ergebnis", 0)
        print(result)
        pass
        
