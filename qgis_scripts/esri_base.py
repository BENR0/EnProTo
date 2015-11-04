#http://gis.stackexchange.com/questions/93404/programmatically-change-layer-position-in-the-table-of-contents-qgis

from qgis.core import *

def run_script(iface):
	root = QgsProject.instance().layerTreeRoot()
	esri_base = QgsRasterLayer("http://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer?f=json&pretty=true","ESRI_Basemap")
	QgsMapLayerRegistry.instance().addMapLayer(esri_base, False)
	root.addLayer(esri_base)