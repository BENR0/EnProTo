import arcpy

def fieldExists(inFeature, fieldName):
    fieldList = arcpy.ListFields(inFeature)
    for iField in fieldList:
        if iField.name.lower() == fieldName.name.lower():
            return True
    return False
