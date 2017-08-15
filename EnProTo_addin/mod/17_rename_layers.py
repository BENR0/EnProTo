class RenameLayers(object):
    """Implementation for RenameLayers.button (Button)"""

    def __init__(self):
        self.enabled = True
        self.checked = False

    def onClick(self):
        import os
        import logging

        # usage logging
        user = os.environ.get("USERNAME")
        logging.info('%s, %s', "Open path for layer", user)

        mxd = arcpy.mapping.MapDocument("CURRENT")
        layers = arcpy.mapping.ListLayers(mxd)

        for lyr in layers:
            if lyr.isFeatureLayer:
                #lyrpath = arcpy.Describe(lyr).path
                #if [any(ext) for ext in ('.gdb', '.mdb', '.sde') if ext in os.path.splitext(lyrpath)]:
                #    continue
                #elif not lyr.isGroupLayer:
                lyrname = os.path.basename(lyr.dataSource).split(".")[0]
                lyr.name = lyrname

        arcpy.RefreshTOC()

        pass

