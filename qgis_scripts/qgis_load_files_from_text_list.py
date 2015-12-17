from qgis.core import *
from glob import glob
from qgis.gui import *
import os

#class Loader:
#http://gis.stackexchange.com/questions/95402/how-to-open-a-shapefile-using-python-in-qgis
 #   def __init__(self, iface)
  #      self.iface = iface

def run_script(iface, **args):
 #def load_shapefiles(self, filelist)
    layersfile = args["path"]
    print(layersfile)
    with open(layersfile, "r") as f:
        for line in f:
            line = str.strip(line)
            shpdir, shpfile  = os.path.split(line)
            filepath = os.path.join(shpdir, shpfile)
            print("Adding File: " + filepath)
            layer = iface.addVectorLayer(filepath, shpfile, "ogr")
            #layer = QgsVectorLayer(r"K:\Arbeiten_Projekte\Energie\Energie_WEA_Lahnau\05_GIS\av_daten\04_Bestandsdaten\BP_Grossvoegel_20150415.shp", "test", "ogr")
            #print(str(layer))
            #print(type(os.path.join(line,"")))
            QgsMessageLog.logMessage("message", "name")
            QgsMapLayerRegistry.instance().addMapLayer(layer)