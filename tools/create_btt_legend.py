import arcpy
import os
import comtypes
import colorsys
from aa_arcobjects import *
from fieldexistsfunction import fieldExists


################################################
#beginn of toolbox class
################################################

class CreateBttLegend(object):
    def __init__(self):
        self.label = "Create BTT legend"
        self.description = "Creates a legend with text fields from BTT layer."
        self.canRunInBackground = False

    def getParameterInfo(self):
       #Input feature layer
        in_features = arcpy.Parameter(
                displayName="Input feature layer",
                datatype="GPFeatureLayer",
                name="in_features",
                parameterType="Required",
                direction="Input")

        in_features.filter.list = ["Polygon"]

        #Field to use for sorting to unique values
        code_nr_field = arcpy.Parameter(
                displayName="Attribute table field with code nr (defaults to \"CODE_NR\")",
                name="code_nr_field",
                datatype="Field",
                parameterType="Required",
                direction="Input")

        code_nr_field.parameterDependencies = [in_features.name]

        code_name_field = arcpy.Parameter(
                displayName="Attribute table field with code name (defaults \"to CODE_NAME\")",
                name="code_name_field",
                datatype="Field",
                parameterType="Required",
                direction="Input")

        code_name_field.parameterDependencies = [in_features.name]

        code_group_field = arcpy.Parameter(
                displayName="Attribute table field with code group (defaults to \"BTTGROUP\")",
                name="code_group_field",
                datatype="Field",
                parameterType="Required",
                direction="Input")

        code_group_field.parameterDependencies = [in_features.name]

        #igcolor_field = arcpy.Parameter(
        #      displayName="Attribute table field with signature color (defaults to \"SIGCOLOR\")",
        #       name="sigcolor_field",
        #       datatype="Field",
        #       parameterType="Required",
        #       direction="Input")

        #sigcolor_field.parameterDependencies = [in_features.name]

        #parameters = [in_features, code_nr_field, code_name_field, code_group_field, sigcolor_field]
        parameters = [in_features, code_nr_field, code_name_field, code_group_field]

        return parameters

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        #mxd = arcpy.mapping.MapDocument("current")
        lyr = parameters[0].valueAsText

        fieldlist = ["CODE_NR", "CODE_NAME", "BTTGROUP"]#, "SIGCOLOR"]

        if parameters[0].value:
            i = 1
            for fieldname in fieldlist:
                if fieldname.lower() in [n.name.lower() for n in arcpy.ListFields(lyr)]:
                    parameters[i].value = fieldlist[i-1]
                #else:
                 #   parameters[i].value = " "
                i += 1
        return

    def updateMessages(self, parameters):

        return

    def execute(self, parameters, messages):

        toclayer = parameters[0].valueAsText
        fieldlist1 = parameters[1].valueAsText
        fieldlist2 = parameters[2].valueAsText
        fieldlist3 = parameters[3].valueAsText

        fieldlist = [fieldlist1] + [fieldlist2] + [fieldlist3]

        #################
        #constants
        #################
        #positioncounter
        iPosition = [10.0, 25.0]
        #distances of and between elements
        sigwidth = 1.0
        txtElemWidth = 6.0
        sigheight = 0.5
        sig2group = 0.5
        group2item = 0.6
        item2item = 0.1
        group2group = 0.8
        #font characteristics
        fontName = "Arial"
        headingFontSize = 14.0
        itemFontSize = 12.0

        #helper functions
        #function to create signature with heading
        def createHeader(position, sigcolor, transparency, txtstring, txtElem):
            #AddRectangleElement(position = position, bgcolor = sigcolor, bgtransparency = transparency, tag = "sig")
            heading = txtElem.clone("_clone")
            heading.elementPositionX = position[0] + sigwidth + sig2group
            heading.elementPositionY = position[1]
            #heading.text = '<FNT name = "' + fontName + '" size = "' + str(headingFontSize) + '">' + txtstring + '</FNT>'
            heading.text = txtstring
            #increase iPosition
            position[1] = position[1] - group2item
            return position

        #function to list all items per group
        def listItems(position, groupitems, txtElem):
            nitem = 0
            for nitem in range(len(groupitems)):
                txtitem = txtElem.clone("_clone")
                txtitem.elementPositionX = position[0] + sigwidth + sig2group
                txtitem.elementPositionY = position[1] - nitem * (txtitem.elementHeight + item2item)
                #txtitem.elementWidth = txtElemWidth
                #txtitem.text = '<FNT name = "' + fontName + '" size = "' + str(itemFontSize) + '">' + groupitems[nitem] + '</FNT>'
                txtitem.text = groupitems[nitem]
            position[1] = position[1] - nitem * (txtitem.elementHeight + item2item) - group2group
            return position

        ################
        #begin of script
        ################
        #add initial text element
        AddTextElement(position = (0.0, 0.0), txtstring = "txtElemTemplate")
        AddTextElement(position = (0.0, 0.0), txtstring = "txtElemTemplate2", tag = "txtElemTemplate2", txtsize = headingFontSize)
        #get created text element
        mxd = arcpy.mapping.MapDocument("current")
        txtElemTemplate = arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT")[1]
        txtElemTemplate2 = arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT")[0]

        #get layer transparency
        #toclayertrans = toclayer.transparency
        #print(toclayertrans)
        toclayertrans = 0.0
        #get data from attribute table and create dictionary
        #fieldlist = ["CODE_NR", "CODE_NAME", "BTTGROUP", "SIGCOLOR"]
        #init dict
        legendDict = dict()
        with arcpy.da.SearchCursor(toclayer, fieldlist) as cursor:
            for row in set(cursor):
                item = row[0] + ": " + row[1]
                if row[2] in legendDict:
                    legendDict[row[2]]["items"].append(item)
                else:
                    legendDict[row[2]] = {"items" : [item]} #, "color" : tuple(row[3].split(","))}

        #create legend
        for key in legendDict.keys():
            print("create item")
            #iPosition = createHeader(iPosition, legendDict[key]["color"],toclayertrans, key, txtElemTemplate2)
            iPosition = createHeader(iPosition, (0,0,0),toclayertrans, key, txtElemTemplate2)
            iPosition = listItems(iPosition, legendDict[key]["items"], txtElemTemplate)

        #clean uo
        #del legendDict, iPosition
        pass