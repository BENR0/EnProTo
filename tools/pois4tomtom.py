import arcpy
import os
import sys
import struct

#OV2 Format extract from: http://lists.gnumonks.org/pipermail/opentom/2005-November/000083.html
#Author:  Tor Arntsen tor at spacetec.no 

# Overview of OV2 Format:
#Byte zero is 2  (this indicates that the record is of "type 2" format)
#Next 4 bytes is the size of the (poi) record, in little endian format. 
# It shall include the length of this and the previous and following 
# fields. *)
#Next 4 bytes is longitude, little endian int, east-positive, divide by
# _LATLONG_MULTIPLIER.0 to get decimal format (e.g. 18.12345E is encoded as 1812345)
#Next 4 bytes is ditto for latitude north.
#Next follows a null-terminated string with the address (e.g. Gatwick Airport\0)

# Other type formats found in the TomTom SDK Manual

_CHARSET = 'cp1252'
_LATLONG_MULTIPLIER = 100000

def writeOV2(data, filename):
    file = open(filename, 'wb')

    typeBuf = struct.pack("<B",2)
    count = 0
    for poiset in data:
        uName = poiset[0] + '\0'
        name = uName.encode(_CHARSET)
        lat = poiset[1]
        long = poiset[2]
        
        latBuf = struct.pack("<i",int(lat*_LATLONG_MULTIPLIER))
        longBuf = struct.pack("<i",int(long*_LATLONG_MULTIPLIER))
        nameBuf = struct.pack("<%ss"%len(uName),name)
        nameLength = struct.calcsize("<%ss"%len(name))
        sizeBuf = struct.pack("<I",nameLength+13)
        
        file.write(typeBuf)
        file.write(sizeBuf)
        file.write(latBuf)
        file.write(longBuf)
        file.write(nameBuf)

        count += 1

    file.close()
    return count


class POIS4TomTom(object):
    def __init__(self):
        self.label = "POIS4TomTom"
        self.description = "Generates POIS for TomTom navi from point shape"
        self.canRunInBackground = False

    def getParameterInfo(self):
       #Input feature layer
        in_features = arcpy.Parameter(
                displayName="Input feature layer",
                datatype="GPFeatureLayer",
                name="in_features",
                parameterType="Required",
                direction="Input")
                
        in_features.filter.list = ["Point"] #,"Line","Polygon"]
        
        #Field to use for sorting to unique values
        description_field = arcpy.Parameter(
                displayName="Attribute table field to be used as description for POI",
                name="description_field",
                datatype="Field",
                parameterType="Required",
                direction="Input")
        
        description_field.parameterDependencies = [in_features.name]

        filename = arcpy.Parameter(
                displayName="Output filename",
                name="output_filename",
                datatype="DEFile",
                parameterType="Required",
                direction="Output")


        parameters = [in_features, description_field, filename]

        return parameters

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):

        return

    def updateMessages(self, parameters):

        return

    def execute(self, parameters, messages):
		
        features = parameters[0].valueAsText
        d_field = parameters[1].valueAsText
        fname = parameters[2].valueAsText

        fname = fname + ".ov2"

        mxd = arcpy.mapping.MapDocument("current")
        arcpy.AddMessage(arcpy.mapping.ListLayers(mxd, features))
        lyr = arcpy.mapping.ListLayers(mxd, features)[0]
        
        #define spatial reference with WGS84
        sr = arcpy.SpatialReference(4326)

        poidata = []
        cursor_fields = [d_field, "SHAPE@X", "SHAPE@Y"]
        with arcpy.da.SearchCursor(lyr, cursor_fields, "", sr) as cursor:
            for row in cursor:
                poidata.append(row)


        writeOV2(poidata, fname)


        return
