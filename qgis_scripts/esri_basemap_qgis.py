def run_script(iface):
    iface.addRasterLayer("http://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer?f=json&pretty=true","ESRI_Basemap")