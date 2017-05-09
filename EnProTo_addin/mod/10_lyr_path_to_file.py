class WritePathOfLayersToFile(object):
    """Implementation for WritePathOfLayersToFile.button (Button)"""
    def __init__(self):
        self.enabled = True
        self.checked = False
    def onClick(self):
        import logging

        #usage logging
        user = os.environ.get("USERNAME")
        logger.info('%s, %s', "Layer paths to file", user)


        mxd = arcpy.mapping.MapDocument("CURRENT")

        lyrs = arcpy.mapping.ListLayers(mxd)
        
        startpath = "L:\Ablage_Mitarbeiter"
        outfile = pythonaddins.SaveDialog("Speichern unter", "layers.txt", startpath)
        tfile = open(outfile, 'w') #open('L:\Ablage_Mitarbeiter\Benjamin\dokumente\layers.txt', 'w')
        #outfile = csv.writer(tfile)
        
        for lyr in lyrs:
            if lyr.supports('visible'):
                if lyr.isFeatureLayer:
                    path = lyr.dataSource.encode("utf-8") + "\n"
                #elif lyr.isGroupLayer:
                 #   path = lyr.name.encode("utf-8") + "\n"

                    tfile.write(path)

        tfile.close()
        pass
        
