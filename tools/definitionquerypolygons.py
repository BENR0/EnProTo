import arcpy
import pythonaddins

#function to get center point of layer
def layerCenter(lyr):
    lyrex = arcpy.Describe(lyr).extent
    cpX = lyrex.XMin + (lyrex.XMax - lyrex.XMin)/2
    cpY = lyrex.YMin + (lyrex.YMax - lyrex.YMin)/2
    return cpX, cpY

#function for polygon corner coords
def polyExtent(xrange, yrange, cpx, cpy):
    pXMin = cpx - xrange/2
    pYMin = cpy - yrange/2
    pXMax = cpx + xrange/2
    pYMax = cpy + yrange/2
    return arcpy.Extent(pXMin, pYMin, pXMax, pYMax)

#function to create polygon
def createPolgon(cornercoords):
    polyArray = arcpy.Array()
    polyArray.add(cornercoords.lowerLeft)
    polyArray.add(cornercoords.lowerRight)
    polyArray.add(cornercoords.upperRight)
    polyArray.add(cornercoords.upperLeft)
    polyArray.add(cornercoords.lowerLeft)
    return polygon = arcpy.Polygon(polyArray)

def uniqueValues(table, field):
    with arcpy.da.SearchCursor(table, field1) as cursor:
        return sorted({row[0] for row in cursor})

#Input
layer = pythonaddins.GetSelectedTOCLayerOrDataFrame()
scale = 2500
mapField = 
blattschnitt = pythonAddins.SaveDialog

#beginning of script
mxd = arcpy.mapping.MapDocument("current")
df = arcpy.mapping.ListDataframes(mxd)[0]
#get dataframe dimensions
dfX, dfY = df.elementWidth, df.elementHeight

#calculate polygon length in map units
polyX, polY = dfX * scale, dfY * scale

#create polygon
centerX, centerY = layerCenter(layer)
polygon = createPolygon(polyExtent(dfX, dfY, centerX, centerY))
#get values to map from attribute table
values = uniqueValues(layer, mapField)
#init list for polys
polys = []
for i in length(values):
    polys.append(polygon)

blattschnitte = arcpy.CopyFeatures_management(polys, blattschnitt)

#add field for ddp page name
arcpy.AddField_management(blattschnitte, mapField, "TEXT", 100)

i = 0
#populate field with items from value list
with arcpy.da.UpdateCursor(blattschnitte, mapField) as cursor:
    for row in cursor:
        row[0] = values[i]
        i += 1
