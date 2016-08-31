# coding: utf8
import arcpy
import numpy as np
#import openpyxl
import xlwt
import pandas as pd
import os
import matplotlib.pyplot as plt


def create_field_name(fc, new_field):
    '''Return a valid field name that does not exist in fc and
    that is based on new_field.

    fc: feature class, feature layer, table, or table view
    new_field: new field name, will be altered if field already exists

    Example:
    >>> fc = 'c:\\testing.gdb\\ne_110m_admin_0_countries'
    >>> createFieldName(fc, 'NEWCOL') # NEWCOL
    >>> createFieldName(fc, 'Shape') # Shape_1
    '''

    # if fc is a table view or a feature layer, some fields may be hidden;
    # grab the data source to make sure all columns are examined
    fc = arcpy.Describe(fc).catalogPath
    new_field = arcpy.ValidateFieldName(new_field, fc)

    # maximum length of the new field name
    maxlen = 64
    dtype = arcpy.Describe(fc).dataType
    if dtype.lower() in ('dbasetable', 'shapefile'):
        maxlen = 10
    fields = [f.name.lower() for f in arcpy.ListFields(fc)]

    # see if field already exists
    if new_field.lower() in fields:
        count = 1
        while new_field.lower() in fields:

            if count > 1000:
                raise bmiError('Maximum number of iterations reached in uniqueFieldName.')

            if len(new_field) > maxlen:
                ind = maxlen - (1 + len(str(count)))
                new_field = '{0}_{1}'.format(new_field[:ind], count)
                count += 1
            else:
                new_field = '{0}_{1}'.format(new_field, count)
                count += 1

    return new_field

def CopyFields(source_table, in_field, join_dict, join_values):
    '''
    Copies field(s) from one table to another

    source_table: table in which to add new fields
    in_field: a field that has common values to a field in the join_table.
              think of this as a "join_field"
    join_dict: dictionary created from the join table
    join_values: fields to add to source_table (list)
    '''

    # Find out if source table is NULLABLE
    #if not os.path.splitext(cat_path)[1] in ['.dbf','.shp']:
    #nullable = 'NULLABLE'
    #else:
    #nullable = 'NON_NULLABLE'

    #get field data types from joindict
    ftype = "TEXT"
    length = 200
    #pres = field.precision
    #scale = field.scale
    #alias = field.aliasName
    #domain = field.domain

    #Add fields to be copied
    update_fields = []
    fieldlist = [f.name for f in arcpy.ListFields(source_table, "")]
    for f in join_values:
        #if field name exists create new name
        if f in fieldlist:
            #newname = create_field_name(source_table, fldb)
            newname = "J" + f
            arcpy.AddField_management(source_table,newname,ftype,length)
            #Message("Added '%s' field to \"%s\"" %(name, os.path.basename(source_table)))
            update_fields.insert(join_values.index(f), newname.encode('utf-8'))
        else:
            newname = f
            arcpy.AddField_management(source_table,newname,ftype,length)
            #Message("Added '%s' field to \"%s\"" %(name, os.path.basename(source_table)))
            update_fields.insert(join_values.index(f), newname.encode('utf-8'))


            #Update Cursor  
    print("updating fields")
    update_index = list(range(len(update_fields)))
    row_index = list(x+1 for x in update_index)
    update_fields.insert(0, in_field)
    nomatchfound = []
    with arcpy.da.UpdateCursor(source_table, update_fields) as urows:
        for row in urows:
            if row[0] in join_dict:
                try:
                    allVals =[join_dict[row[0]][i] for i in update_index]
                    for r,v in zip(row_index, allVals):
                        row[r] = v
                    urows.updateRow(row)
                except:
                    pass
            elif row[0] not in join_dict:
                nomatchfound.append(row[0])

    #Message('Fields in "%s" updated successfully' %(os.path.basename(source_table)))
    print("no matches found for the following values:")
    print(nomatchfound)
    return

#function to delete value of join key from list wenn converting dictionary
def delkey(x, key):
    tmp = x[key]
    tmplist = list(x.values())
    tmplist.remove(tmp)
    return tuple(tmplist)

class WEAangebot(object):
    def __init__(self):
        self.label = "WEAangebot"
        self.description = "Creates pivot table and appropiate layers for WEA Angebote."
        self.canRunInBackground = False

    def getParameterInfo(self):
        #Input feature layer
        in_features = arcpy.Parameter(
            displayName="Input feature layers",
            name="in_features",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Input",
            multiValue=True)

        out_buffer = arcpy.Parameter(
            displayName="Buffer Output Feature",
            name="buffer_out",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Output")
            
        out_buffer.filter.list = ["shp"]
        
        #buffer ranges list
        buffer_ranges = arcpy.Parameter(
            name="buffer_ranges",
            displayName="Puffer Radien",
            datatype="GPString",
            parameterType="Required",
            direction="Input",
            multiValue=True)
            
        buffer_ranges.filter.type = "ValueList"
        buffer_ranges.filter.list = [100,200,250,300,500,1000,1500,2000,2500,3000,4000,5000,6000,7000,8000,9000,10000]
        
        out_intersected = arcpy.Parameter(
            displayName="Intersected Corine output",
            name="intersected_out",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Output")
            
        out_intersected.filter.list = ["shp"]
            
        out_table = arcpy.Parameter(
             displayName="Pivot table output",
             name="pivot_table_out",
             datatype="DEFile",
             parameterType="Required",
             direction="Output")
             
        out_table.filter.list = ["xls"]
        

        parameters = [in_features, out_buffer, buffer_ranges, out_intersected, out_table]
            
        return parameters

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):

        return

    def updateMessages(self, parameters):
        
        return

    def execute(self, parameters, messages):
        arcpy.Delete_management("in_memory")
        arcpy.env.overwriteOutput = True
        mxd = arcpy.mapping.MapDocument("current")
        df = arcpy.mapping.ListDataFrames(mxd)[0]
		
    	in_features = parameters[0].valueAsText
        in_features = in_features.split(";")
    	out_buffers = parameters[1].valueAsText
    	buffer_ranges = parameters[2].valueAsText
        buffer_ranges = buffer_ranges.split(";")
        out_intersected = parameters[3].valueAsText
        out_table = parameters[4].valueAsText
        
        #Ausgabe-Feature-Class__Alle_Puffer_mit_Flchenberechnung_in_ha_ = arcpy.GetParameterAsText(2)
        #Ausgabe-Feature-Class__Alle_Puffer_mit_Corine-Daten_verschnitten_ = arcpy.GetParameterAsText(3)
        #Ausgabe-Excel-Datei = arcpy.GetParameterAsText(4)
        
        #corine data
        corine_data = "V:\\Vorlagen_CAD_GIS\\Daten_Corine\\clc2006_shapes-zipped\\DE_utm32\\clc2006_DE_utm32\\clc06_de_wald_u32.shp"
        #lyr styles
        intersect_lyr_style = "V:\\Vorlagen_CAD_GIS\\GIS\\styles_aktuell\\WEA_corine_wald_colors.lyr"
        buffer_lyr_style = "V:\\Vorlagen_CAD_GIS\\GIS\\styles_aktuell\\WEA_puffer_colors.lyr"
        
        #function to add fields and calculate area
        def AddArea(shp, fieldnames = ["AREA_HA", "AREA_QM"], fprecision = 15, fscale = 2):
            #fprecission: length of field over all
            #fscale: number of decimale places
            shp = shp
            fieldName1 = fieldnames[0]
            fieldName2 = fieldnames[1]
            fieldPrecision = fprecision #length of field over all
            fieldScale = fscale         #number of decimal places

            #get list with fields of selected layer
            existfield1 = arcpy.ListFields(shp, fieldName1)
            #existfield2 = arcpy.ListFields(shp, fieldName2)

            #add fields to table of shapefile if not already existant
            if len(existfield1) != 1:
                arcpy.AddField_management(shp, fieldName1, "FLOAT", fieldPrecision, fieldScale)

            #if len(existfield2) != 1:
               # arcpy.AddField_management(shp, fieldName2, "FLOAT", fieldPrecision, fieldScale)

            #calculate geometry
            arcpy.CalculateField_management(shp, fieldName1, "!SHAPE.AREA@HECTARES!", "PYTHON")
            #arcpy.CalculateField_management(shp, fieldName2, "round(!SHAPE.AREA@SQUAREMETERS!, 0)", "PYTHON")
            
            return
        
        #merge layers if in_features list > 1
        if len(in_features) > 1:
            arcpy.AddMessage("Merging input layers...")
            mem_merge = arcpy.Merge_management(in_features, "in_memory\merge")
        else:
            mem_merge = in_features[0]

        #init list for storing buffer for each range
        tmp_buffers = []
        iter = 0
        #create buffer for each range
        for range in buffer_ranges:
            arcpy.AddMessage("Creating buffer with range " + range)
            tmp_memory_path = r"in_memory\buffer_" + range
            tmp_buffers.append(arcpy.Buffer_analysis(mem_merge, tmp_memory_path, range, "FULL", "ROUND", "ALL"))
            arcpy.AddField_management(tmp_buffers[iter], "DISTANCE", "LONG", 10)
            arcpy.CalculateField_management(tmp_buffers[iter], "DISTANCE", range, "PYTHON")
            iter += 1

        arcpy.AddMessage("Merging buffers...")
        merged_buffers = arcpy.Merge_management(tmp_buffers, out_buffers)[0]
        #merged_buffers = merged_buffers.getOutput(0)
        #while merged_buffers.status < 4:
           # time.sleep(0.2)
        #arcpy.AddMessage(merged_buffers) 
        #test = os.path.join(merged_buffers, ".shp")
        #arcpy.AddMessage(test)
        
        arcpy.AddMessage("Calculating area for merged buffers...")
        #calculate area
        AddArea(merged_buffers)
        
        #select only forest in corine data
        corine_selected = arcpy.Select_analysis(corine_data, "in_memory\corine_selected", "\"CODE_06\"='311' OR \"CODE_06\"='312' OR \"CODE_06\"='313'")
        
        arcpy.AddMessage("Intersecting Corine data with buffers...")
        #intersect buffers with corine data
        buffer_intersected = arcpy.Intersect_analysis([merged_buffers, corine_selected], out_intersected, "ALL", "")[0]

        arcpy.AddMessage("Calculating area for intersected data...")
        #calculate area of intersected shapefile
        AddArea(buffer_intersected, ["HA_Wald", "QM_Wald"])
        
        # create layer in TOC and reference it in a variable for possible other actions
        newlayer1 = arcpy.mapping.Layer(buffer_intersected)
        arcpy.mapping.AddLayer(df, newlayer1,"BOTTOM")
        newlayer2 = arcpy.mapping.Layer(merged_buffers)
        arcpy.mapping.AddLayer(df, newlayer2,"BOTTOM")
        
        buffer_layer = arcpy.mapping.ListLayers(mxd, newlayer2)[0]
        corine_layer = arcpy.mapping.ListLayers(mxd, newlayer1)[0]
        

        #newLyr_forest = arcpy.MakeFeatureLayer_management(buffer_intersected, "test1")

        #newLyr_buffers = arcpy.MakeFeatureLayer_management(merged_buffers, "test2")
        #apply style
        arcpy.ApplySymbologyFromLayer_management(corine_layer, intersect_lyr_style)
        arcpy.ApplySymbologyFromLayer_management(buffer_layer, buffer_lyr_style)

        # Process: Tabelle in Excel
        # arcpy.env.scratchWorkspace = "C:\\Users\\benjamin.roesner\\Documents\\ArcGIS\\Default.gdb"
        # arcpy.TableToExcel_conversion(Ausgabe-Feature-Class__9_, Ausgabe-Excel-Datei, "NAME", "CODE")
        # arcpy.env.scratchWorkspace = tempEnvironment0
        
        #extract specified fields to numpy array
        fnames = ["DISTANCE", "AREA_HA", "CODE_06", "WA_ART", "HA_Wald"]
        table_as_nparray = arcpy.da.FeatureClassToNumPyArray(newlayer1, fnames)
        
        #create pandas data frame
        corine_data_frame = pd.DataFrame(table_as_nparray)

        #create pivot table with col and row totals (margins = True)
        pivot = pd.pivot_table(corine_data_frame, values = "HA_Wald", index = "DISTANCE", columns = "WA_ART", aggfunc = np.sum, margins = True)
        pivot = pivot.fillna(0)

        #add percentages in new columns
        if "Laubwald" in pivot.columns:
            pivot["Laubwald [%]"] = np.round((pivot.Laubwald / (pivot.All)) * 100, 2)
        
        if "Nadelwald" in pivot.columns:
            pivot["Nadelwald [%]"] = np.round((pivot.Nadelwald / (pivot.All)) * 100, 2)
            
        if "Mischwald" in pivot.columns:
            pivot["Mischwald [%]"] = np.round((pivot.Mischwald / (pivot.All)) * 100, 2)

        #group data frame by distance and aggregate with sum (total area in each buffer)
        groupforest = corine_data_frame.groupby("DISTANCE", as_index = False)
        groupforestagg = groupforest.aggregate({"AREA_HA": "max", "HA_Wald": "sum"})
        
        #add percentages column of forest at total area of buffer
        groupforestagg["Waldanteil_prozent"] = np.round((groupforestagg.HA_Wald / groupforestagg.AREA_HA) * 100, 2)

        arcpy.AddMessage("Joining aggregated data to buffer shape...")
        #convert pandas df to dictionary for joining values to buffer shape
        groupforestaggdict = groupforestagg.transpose().to_dict()
        joindict = {groupforestaggdict[r]["DISTANCE"]: delkey(v, "DISTANCE") for r,v in groupforestaggdict.items()}

        CopyFields(buffer_layer, "DISTANCE", joindict, ["AREA_HA", "HA_Wald"])

        arcpy.AddMessage("Adding information do layer descriptions...")
        class_descriptions = []
        arcpy.AddMessage(joindict)
        for i in buffer_layer.symbology.classValues:
            i = float(i)
            if i in joindict.keys():
                class_descriptions.append(str(int(round(joindict[i][0], 0))) + " ha / davon ca." + str(int(round(joindict[i][2], 0))) + " ha Wald")
            else:
                class_descriptions.append(" ")

        buffer_layer.symbology.classDescriptions = class_descriptions

        #rename columns
        groupforestagg.columns = ["Puffer", "Flaeche [ha]", "Waldanteil [ha]", "Waldanteil [%]"]
        arcpy.AddMessage("Writing Data to Excel spreadsheet...")
        #write tables to Excel (each table to one sheet)
        ###### ADD VARIABLE TO WRITE FILE #######
        writer = pd.ExcelWriter(out_table)
        pivot.to_excel(writer, sheet_name = "Waldartenanteile")
        groupforestagg.to_excel(writer, sheet_name = "Pufferwaldanteile")
        writer.save()

        #refresh view and toc
        #arcpy.RefreshActiveView()
        #arcpy.RefreshTOC()
 
        arcpy.AddMessage("Done")
        
        #clear up in_memory workspace
        arcpy.Delete_management("in_memory")
        #clean up variables
        del mxd, df, tmp_buffers, buffer_intersected, corine_selected, merged_buffers, groupforest, groupforestagg, pivot, table_as_nparray
        
        return

