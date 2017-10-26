import arcpy
import os
from aa_arcobjects import *

class TableFromAttributes(object):
    def __init__(self):
        self.label = "TableFromAttributes"
        self.description = "Create a text field table from attributes."
        self.canRunInBackground = False

    def getParameterInfo(self):
       #Input feature layer
        in_features = arcpy.Parameter(
                displayName="Input feature layer",
                datatype="GPFeatureLayer",
                name="in_features",
                parameterType="Required",
                direction="Input")
                
        #in_features.filter.list = ["Point","Line","Polygon"]
        
        #Field to use for sorting to unique values
        abk = arcpy.Parameter(
                displayName="Abkürzung",
                name="abkürzung",
                datatype="Field",
                parameterType="Required",
                direction="Input")
        
        abk.parameterDependencies = [in_features.name]

        #name deutsch
        namedt = arcpy.Parameter(
                displayName="Deutscher Name",
                name="deutscher_name",
                datatype="Field",
                parameterType="Required",
                direction="Input")

        namedt.parameterDependencies = [in_features.name]

       #name wiss
        namewiss = arcpy.Parameter(
                displayName="Wissenschaftlicher Name",
                name="name_wiss",
                datatype="Field",
                parameterType="Required",
                direction="Input")

        namewiss.parameterDependencies = [in_features.name]

        #Fields to use for description
        # description_fields = arcpy.Parameter(
        #         displayName="Attribute table fields to be used as description",
        #         name="description_fields",
        #         datatype="GPValueTable",
        #         parameterType="Required",
        #         direction="Input")
        #
        # description_fields.parameterDependencies = [in_features.name]
        # #description_fields.columns = ([["Field", "Field"], ["GPBoolean", "Bold"], ["GPBoolean",
        #  #   "Italics"], ["GPBoolean", "Underlined"], ["GPBoolean", "Newline"]])
        #
        # description_fields.columns = ([["Field", "Field"], ["GPBoolean", "Bold"], ["GPBoolean",
        #     "Italics"], ["GPBoolean", "Underlined"]])
        #
        # description_fields.filters[1].type = "ValueList"
        # description_fields.filters[1].list = ["True", "False"]
        # description_fields.filters[2].type = "ValueList"
        # description_fields.filters[2].list = ["True", "False"]
        # description_fields.filters[3].type = "ValueList"
        # description_fields.filters[3].list = ["True", "False"]
        # #description_fields.filters[4].type = "ValueList"
        # #description_fields.filters[4].list = ["True", "False"]
        
	
        parameters = [in_features,abk,namedt,namewiss]

        return parameters

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        # #mxd = arcpy.mapping.MapDocument("current")
        # lyr = parameters[0].valueAsText
        # if parameters[0].value:
        #     if parameters[0].value.symbologyType == "UNIQUE_VALUES":
        #         parameters[1].value = parameters[0].value.symbology.valueField
        #     else:
        #         parameters[1].value = ""
        return

    def updateMessages(self, parameters):
        # if parameters[0].value:
        #     if parameters[0].value.symbologyType != "UNIQUE_VALUES":
        #         parameters[0].setErrorMessage("This layers symbology is not of type \"unique values\".")
        return

    def execute(self, parameters, messages):
		
        features = parameters[0].valueAsText
        abkfield = parameters[1].valueAsText
        namedtfield = parameters[2].valueAsText
        namewissfield = parameters[3].valueAsText

        # #d_field = parameters[2].value
        # #valuetable column names
        # #vtcolumns = ["Field", "Bold", "Italics", "Underlined", "Newline"]
        # vtcolumns = ["Field", "Bold", "Italics", "Underlined"]
        # #init empty dictionary for valuetable
        # dict_valuetable = {}
        # #read valuetable to dictionary
        # for row in d_field:
        #     dict_valuetable[str(row[0])] = dict(zip(vtcolumns, row))
        # arcpy.AddMessage(dict_valuetable)


        mxd = arcpy.mapping.MapDocument("current")
        #arcpy.AddMessage(arcpy.mapping.ListLayers(mxd, features))
        lyr = arcpy.mapping.ListLayers(mxd, features)[0]

        #init vars
        #positioncounter
        #iPosition = [10.0, 25.0]
        #distances of and between elements
        txtElemWidth = 6.0
        #font characteristics
        fontName = "Arial"
        headingFontSize = 14.0
        itemFontSize = 12.0

        #Get/set information about the table
        rowHeight = 0.4
        fieldNames = [abkfield, namedtfield, namewissfield]
        colWidth = 4.0
        smallColWidth = 1.5
        col1width = 0
        col2width = 0


        #Add initial text element
        AddTextElement(position = (0.0, 0.0), txtstring = "txtElemTemplate",
                        tag = "txtElemTemplate", txtsize = itemFontSize)
        #get created text element
        mxd = arcpy.mapping.MapDocument("current")
        tableText = arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT")[0]

        #start coords for elements
        pageWidth = mxd.pageSize.width
        upperX = pageWidth + 3.0
        upperY = 25.0

        #get data from attribute table and store rows as tuples in list
        tabledata = []
        with arcpy.da.SearchCursor(features, fieldNames) as cursor:
            for row in cursor:
               # if len(row[0]) > col1width:
                #    col1width = len(row[0])
               #if len(row[1]) > col2width:
                #    col2width = len(row[1])

                rowtuple = tuple(row)
                if rowtuple not in tabledata:
                    tabledata.append(rowtuple)

        #sort list with data
        #data = sorted(set(data), key=lambda tup: tup[1])
        #or inplace
        tabledata.sort(key=lambda tup: tup[1])

        #Place starting text element
        tableText.elementPositionX = upperX + 0.05 #slight offset
        tableText.elementPositionY = upperY

        #Create text elements based on values from the table
        y = upperY - rowHeight
        for row in tabledata:
            x = upperX + 0.05 #slight offset
            try:
                y = y - rowHeight
                for field in row:
                    newCellTxt = tableText.clone("_clone")
                    #make last field with latin name italic
                    if row.index(field) == 2:
                        field = "<ITA>" + field + "</ITA>"
                    newCellTxt.text = field
                    newCellTxt.elementPositionX = x
                    newCellTxt.elementPositionY = y
                    #make first column width smaller
                    if row.index(field) == 0:
                        curColWidth = smallColWidth
                    else:
                        curColWidth = colWidth
                    x = x + curColWidth
            except:
                print("Invalid value assignment")

        for elm in arcpy.mapping.ListLayoutElements(mxd, wildcard="txtElemTemplate"):
            elm.delete()



        ##################################################################
        
        # #function to read attribute table to dictionary based on a key field
        # def make_attribute_dict(fc, key_field, attr_list=['*']):
        #     attdict = {}
        #     fc_field_objects = arcpy.ListFields(fc)
        #     fc_fields = [field.name for field in fc_field_objects if field.type != 'Geometry']
        #     if attr_list == ['*']:
        #         valid_fields = fc_fields
        #     else:
        #         valid_fields = [field for field in attr_list if field in fc_fields]
        #     #Ensure that key_field is always the first field in the field list
        #     cursor_fields = [key_field] + list(set(valid_fields) - set([key_field]))
        #     with arcpy.da.SearchCursor(fc, cursor_fields) as cursor:
        #         for row in set(cursor):
        #             #get length of all row items
        #             rowitemlen = [len(i) for i in row]
        #             attdict[row[0]] = dict(zip(cursor.fields, zip(row, rowitemlen)))
        #     return attdict
        #
        # #create dictionary from table with selected fields
        # attrdict = make_attribute_dict(features, keyfield, dict_valuetable.keys())
        # arcpy.AddMessage(attrdict)
        # #init empty description list
        # class_descriptions = []
        #
        # #extract all length items from dictionary
        # lenarr = [[j[1] for j in i.values()] for i in attrdict.values()]
        # #get maximum length for each field name
        # maxlen = [max(i) for i in zip(*lenarr)]
        #
        # cols = True
        # for i in lyr.symbology.classValues:
        #     tmp = ""
        #     colcounter = 0
        #     for f in dict_valuetable.keys():
        #         otag = ""
        #         ctag = ""
        #         #if dict_valuetable[f]["Newline"]:
        #         #   otag = otag + chr(13) + chr(10) #"\r\n"
        #         if dict_valuetable[f]["Bold"]:
        #             otag = otag + "<BOL>"
        #             ctag = "</BOL>" + ctag
        #         elif dict_valuetable[f]["Italics"]:
        #             otag = otag + "<ITA>"
        #             ctag = "</ITA>" + ctag
        #         elif dict_valuetable[f]["Underlined"]:
        #             otag = otag + "<UND>"
        #             ctag = "</UND>" + ctag
        #
        #         if cols:
        #             txt = otag + attrdict[i][f][0] + ctag
        #             shift = str(maxlen[colcounter] + 10)
        #             tmpformat = "{:{shift}}".format(txt, shift=shift)
        #             tmp = tmp + tmpformat
        #             colcounter += 1
        #         else:
        #             tmp = tmp + otag + attrdict[i][f][0] + ctag + " "
        #     class_descriptions.append(tmp)


        return
