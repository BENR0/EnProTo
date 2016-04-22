import arcpy
from arcpy import env
import urllib
import urllib2
import os
import os
import errno

def make_dir(path):
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise

# load the OpenStreetMap specific toolbox
#arcpy.ImportToolbox(r'd:\projects\OSMEditor\WheelChairMap\OpenStreetMap Toolbox.tbx')

#assign drop down choice
amenity = "churches"

#get path to project
mxd = arcpy.mapping.MapDocument("current")
mxdpath = mxd.filePath

#create path to GIS data directory in project directory
rootpath = re.split("05_GIS",mxdpath)[0]
OSMdir = os.path.join(rootpath, "05_GIS", "av_daten", "10_OSM", amenity)

#create osm dir if not existent
make_dir(OSMdir)

#create temp directory for storing osm xml data
OSMtmp = os.path.join(OSMdir, "ztmp")
make_dir(OSMtmp)

#get bounding box of current viewing extent or (largest) layer?
bboxtuple = arcpy.Describe(lyr).extent
#bboxtuple = (41.88269405444917,12.48070478439331,41.89730998384814,12.503278255462645)
overpassurl = "https://overpass-api.de/api/interpreter?data=[out:xml];"

######## queries #########
churches = """
(
  node["amenity"="place_of_worship"]["religion"="christian"]{0};
  way["amenity"="place_of_worship"]["religion"="christian"]{0};
  relation["amenity"="place_of_worship"]["religion"="christian"]{0};
);
out body;
>;
out skel qt;""".format(bboxtuple)

#fetch data from Overpass
requesturl = overpassurl + urllib.quote_plus(churches)

myRequest = urllib2.Request(requesturl)
#file path for temporary osm data
OSMdata = os.path.join(OSMtmp, "osm.xml")
try:
    OSMurlHandle = urllib2.urlopen(myRequest, timeout=60)
    OSMfile = file(OSMdata, 'wb')
    OSMfile.write(OSMurlHandle.read())
    OSMfile.close()
except urllib2.URLError, e:
    if hasattr(e, 'reason'):
        AddMsgAndPrint('Unable to reach the server.', 2)
        AddMsgAndPrint(e.reason, 2)
    elif hasattr(e, 'code'):
        AddMsgAndPrint('The server was unable to fulfill the request.', 2)
        AddMsgAndPrint(e.code, 2)

# define the names for the feature dataset and the feature classes
inputName = amenity
#set workspace to scratch workspace
wspace = env.scratchWorkspace

validatedTableName = arcpy.ValidateTableName(inputName, wspace)
nameOfTargetDataset = arcpy.os.path.join(wspace, validatedTableName)

fcpoint = os.path.join(validatedTableName, validatedTableName + r"_osm_pt")
fcline = os.path.join(validatedTableName, validatedTableName + r"_osm_ln")
fcpoly = os.path.join(validatedTableName, validatedTableName + r"_osm_ply")

nameOfPointFeatureClass = arcpy.os.path.join(wspace, fcpoint)
nameOfLineFeatureClass = arcpy.os.path.join(wspace, fcline)
nameOfPolygonFeatureClass = arcpy.os.path.join(wspace, fcpoly)

#import downloaded osm.xml into default database and get attributes
arcpy.OSMGPFileLoader_osmtools(OSMdata, 'CONSERVE_MEMORY', nameOfTargetDataset, nameOfPointFeatureClass, nameOfLineFeatureClass, nameOfPolygonFeatureClass)

#loop through all feature classes in database and get attributes.
# extract the name tag for all line features
arcpy.OSMGPAttributeSelector_osmtools(fcpoint, 'name')

# filter the points to only process the attribute carrying nodes
#filteredPointLayer = 'Only attributed nodes'
#arcpy.MakeFeatureLayer_management(r'stuttgart\stuttgart_osm_pt', filteredPointLayer, "osmSupportingElement = 'no'")

# extract the name tag for the filtered point features
#arcpy.OSMGPAttributeSelector_osmtools(filteredPointLayer, 'name,note')

#loop reproject feature classes to coord of project dataframe
#arcpy.Project_management(in_layer, outlayer, PCS, transformation)
#!?copy transformations from rna analyse tool

#add shapes to project (create group layer?)

