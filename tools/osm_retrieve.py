import arcpy
import urllib
import urllib2
import os

#create path to directory where to store osm data
mxd = arcpy.mapping.MapDocument("current")
mxdpath = mxd.filePath

#split path at GIS directory and add GIS/av_data again
rootpath = re.split("05_GIS",mxdpath)[0]
OSMdir = os.path.join(rootpath, "05_GIS", "av_daten", "10_OSM")
#create osm dir if not existent

#create subdirs for data sets


#create temp directory for storing osm xml data

#bboxdict = {"xmin": 41.88269405444917, "ymin": 12.48070478439331, "xmax": 41.89730998384814, "ymax": 12.503278255462645}
bboxtuple = arcpy.Describe(lyr).extent
#bboxtuple = (41.88269405444917,12.48070478439331,41.89730998384814,12.503278255462645)
dataurl = "https://overpass-api.de/api/interpreter?data=[out:xml];"
query = """
(
  node["amenity"="place_of_worship"]["religion"="christian"]{0};
  way["amenity"="place_of_worship"]["religion"="christian"]{0};
  relation["amenity"="place_of_worship"]["religion"="christian"]{0};
);
out body;
>;
out skel qt;""".format(bboxtuple)


requesturl = dataurl + urllib.quote_plus(query)


myRequest = urllib2.Request(requesturl)
try:
    OSMurlHandle = urllib2.urlopen(myRequest, timeout=60)
    OSMfile = file('osm.xml', 'wb')
    OSMfile.write(OSMurlHandle.read())
    OSMfile.close()
except urllib2.URLError:
        raise




