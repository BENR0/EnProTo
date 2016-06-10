"""Load all shapefiles in a given textfile. """
from glob import glob
from os import path

from qgis.core import *
from qgis.gui import *
import qgis.utils


class Loader:
    def __init__(self, iface):
        """Initialize using the qgis.utils.iface
        object passed from the console.
        """

        self.iface = qgis.utils.iface

    def load_shapefiles(self, path):
        """Load all shapefiles found in shp_path"""
        #print "Loading shapes from %s" % path.join(shp_path, "*.shp")
        #shps = glob(path.join(shp_path, "*.shp"))
        layersfile = path
        with open(layersfile, "r") as f:
            for line in f:
                (shpdir, shpfile) = path.split(line)
                #print "Loading %s" % shpfile
                lyr = QgsVectorLayer(line, shpfile, 'ogr')
                QgsMapLayerRegistry.instance().addMapLayer(lyr)


def run_script(iface, listfile):
    ldr = Loader(iface)
    #print "Loading all shapefiles from file %s" % listfile
    ldr.load_shapefiles(listfile)