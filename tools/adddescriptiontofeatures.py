import arcpy
import os

class AddDescriptionToFeatures(object):
    def __init__(self):
        self.label = "AddDescriptionToFeatures"
        self.description = "Adds description to features based on Column of "+ \
		"Attribute Table (e.g. lat. names to fauna features)"
        self.canRunInBackground = False

    def getParameterInfo(self):
       #Input feature layer
        in_features = arcpy.Parameter(
                displayName="Input feature layer",
                datatype="GPFeatureLayer",
                name="in_features",
                parameterType="Required",
                direction="Input")
                
        in_features.filter.list = ["Point","Line","Polygon"]
        
        #Field to use for sorting to unique values
        sorting_field = arcpy.Parameter(
                displayName="Attribute table field to be used for sorting",
                name="sorting_field",
                datatype="Field",
                parameterType="Required",
                direction="Input")
        
        #sorting_field.parameterDependencies = [in_features.name]

        #Fields to use for description
        description_fields = arcpy.Parameter(
                displayName="Attribute table fields to be used as description",
                name="description_fields",
                datatype="GPValueTable",
                parameterType="Required",
                direction="Input")
        
        description_fields.parameterDependencies = [in_features.name]
        #description_fields.columns = ([["Field", "Field"], ["GPBoolean", "Bold"], ["GPBoolean",
         #   "Italics"], ["GPBoolean", "Underlined"], ["GPBoolean", "Newline"]])
            
        description_fields.columns = ([["Field", "Field"], ["GPBoolean", "Bold"], ["GPBoolean",
            "Italics"], ["GPBoolean", "Underlined"]])
                
        description_fields.filters[1].type = "ValueList"
        description_fields.filters[1].list = ["True", "False"]
        description_fields.filters[2].type = "ValueList"
        description_fields.filters[2].list = ["True", "False"]
        description_fields.filters[3].type = "ValueList"
        description_fields.filters[3].list = ["True", "False"]
        #description_fields.filters[4].type = "ValueList"
        #description_fields.filters[4].list = ["True", "False"]
        
	
        parameters = [in_features,sorting_field, description_fields]

        return parameters

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        #mxd = arcpy.mapping.MapDocument("current")
        lyr = parameters[0].valueAsText
        if parameters[0].value:
            if parameters[0].value.symbologyType == "UNIQUE_VALUES":
                parameters[1].value = parameters[0].value.symbology.valueField
            else:
                parameters[1].value = ""
        return

    def updateMessages(self, parameters):
        if parameters[0].value:
            if parameters[0].value.symbologyType != "UNIQUE_VALUES":
                parameters[0].setErrorMessage("This layers symbology is not of type \"unique values\".")
        return

    def execute(self, parameters, messages):
		
        features = parameters[0].valueAsText
        keyfield = parameters[1].valueAsText
        d_field = parameters[2].value
        #valuetable column names
        #vtcolumns = ["Field", "Bold", "Italics", "Underlined", "Newline"]
        vtcolumns = ["Field", "Bold", "Italics", "Underlined"]
        #init empty dictionary for valuetable
        dict_valuetable = {}
        #read valuetable to dictionary
        for row in d_field:
            dict_valuetable[str(row[0])] = dict(zip(vtcolumns, row))

        arcpy.AddMessage(dict_valuetable)

        mxd = arcpy.mapping.MapDocument("current")
        arcpy.AddMessage(arcpy.mapping.ListLayers(mxd, features))
        lyr = arcpy.mapping.ListLayers(mxd, features)[0]
        
        #function to read attribute table to dictionary based on a key field
        def make_attribute_dict(fc, key_field, attr_list=['*']):
            attdict = {}
            fc_field_objects = arcpy.ListFields(fc)
            fc_fields = [field.name for field in fc_field_objects if field.type != 'Geometry']
            if attr_list == ['*']:
                valid_fields = fc_fields
            else:
                valid_fields = [field for field in attr_list if field in fc_fields]
            #Ensure that key_field is always the first field in the field list
            cursor_fields = [key_field] + list(set(valid_fields) - set([key_field]))
            with arcpy.da.SearchCursor(fc, cursor_fields) as cursor:
                for row in set(cursor):
                    attdict[row[0]] = dict(zip(cursor.fields,row))
            return attdict

        #create dictionary from table with selected fields
        attrdict = make_attribute_dict(features, keyfield, dict_valuetable.keys())
        #init empty description list
        class_descriptions = []

        for i in lyr.symbology.classValues:
            tmp = ""
            for f in dict_valuetable.keys():
                otag = ""
                ctag = ""
                #if dict_valuetable[f]["Newline"]:
                #   otag = otag + chr(13) + chr(10) #"\r\n"
                if dict_valuetable[f]["Bold"]:
                    otag = otag + "<BOL>"
                    ctag = "</BOL>" + ctag 
                elif dict_valuetable[f]["Italics"]:
                    otag = otag + "<ITA>"
                    ctag = "</ITA>" + ctag
                elif dict_valuetable[f]["Underlined"]:
                    otag = otag + "<UND>"
                    ctag = "</UND>" + ctag

                tmp = tmp + otag + attrdict[i][f] + ctag
            class_descriptions.append(tmp)

        lyr.symbology.classDescriptions = class_descriptions
        lyr.symbology.showOtherValues = False

        return
