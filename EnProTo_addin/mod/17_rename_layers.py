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
            if not lyr.isGroupLayer:
                lyrname = os.path.basename(lyr.dataSource).split(".")[0]
                lyr.name = lyrname

        pass

