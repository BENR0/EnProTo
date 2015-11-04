from qgis.core import *
import os

#class Loader:
#http://gis.stackexchange.com/questions/95402/how-to-open-a-shapefile-using-python-in-qgis
 #   def __init__(self, iface)
  #      self.iface = iface

def run_script(iface):
 #def load_shapefiles(self, filelist)
    with open("L:\Ablage_Mitarbeiter\Benjamin\dokumente\layers.txt", "r") as f:
        for line in f:
            shpdir, shpfile  = os.path.split(line)
            print(shpfile)
            print(str(line))
            layer = iface.addVectorLayer("\\FIL-01\Projekte$\Arbeiten_Projekte\Energie\Energie_WEA_RegPlan_Mitte_VSG_Vogelsberg\05_GIS\av_daten\02_Abgrenzungen\KFFHGEB.shp", "test", "ogr")
            print(str(layer))
            QgsMessageLog.logMessage("message", "name")
            QgsMapLayerRegistry.instance().addMapLayer(layer)