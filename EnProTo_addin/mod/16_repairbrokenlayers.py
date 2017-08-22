class RepairBrokenLayers(object):
    """Implementation for RepairBrokenLayers.button (Button)"""
    def __init__(self):
        self.enabled = True
        self.checked = False
    def onClick(self):
        import logging

        #usage logging
        log_use(str(self.__class__.__name__))

        #function to split given path up to gis folder of project
        def pathuptogisdir(path):
            #split path by GIS directory, keep first part and add GIS folder again
            base = re.split('05_GIS',path)[0]
            startpath = os.path.join(base, "05_GIS")

            return startpath

        #get properties of map document
        mxd = arcpy.mapping.MapDocument("CURRENT")
        #get directory of map document
        mxdpath = mxd.filePath

        #get new path
        newpath = pathuptogisdir(mxdpath)
        print(newpath)

        #get old path from broken layer
        brkLyrpath = arcpy.mapping.ListBrokenDataSources(mxd)[0].dataSource
        oldpath = pathuptogisdir(brkLyrpath)
        print(oldpath)

        #fix all broken layers
        mxd.findAndReplaceWorkspacePaths(oldpath, newpath)

        pass


