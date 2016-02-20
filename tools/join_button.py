import arcpy
import pythonaddins
import pandas as pd
import os
import sys  
  
def Message(msg):  
    print str(msg)  
    arcpy.AddMessage(str(msg))  
    return  
  
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
  
    # field list  
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
    fieldlist = arcpy.ListFields(source_table)  
    for field in fieldlist:
        name = field.name  
        for f in join_values:  
            #if field name exists create new name
            if f == name:  
                #newname = create_field_name(source_table, fldb)  
                newname = "J" + f
            newname = f
            arcpy.AddField_management(source_table,newname,ftype,length)  
            #Message("Added '%s' field to \"%s\"" %(name, os.path.basename(source_table)))  
            update_fields.insert(join_values.index(f), newname.encode('utf-8'))  
                                          

    #Update Cursor  
    update_index = list(range(len(update_fields)))  
    row_index = list(x+1 for x in update_index)  
    update_fields.insert(0, in_field)  
    with arcpy.da.UpdateCursor(source_table, update_fields) as urows:  
        for row in urows:  
            if row[0] in join_dict:
                try:  
                    allVals =[join_dict[row[0]][i] for i in update_index]  
                    for r,v in zip(row_index, allVals):  
                        row[r] = v  
                    urows.updateRow(row)  
                except: pass  
          
    #Message('Fields in "%s" updated successfully' %(os.path.basename(source_table)))  
    return  
  

#function to delete value of join key from list wenn converting dictionary
def delkey(x, key):
    tmp = x[key]
    tmplist = list(x.values())
    tmplist.remove(tmp)
    return tuple(tmplist)

########
#pathes to join tables
#path for each list which can be used for joins
birds = r"birds.csv"
#btt
########
tables = [birds]

mxd = arcpy.mapping.MapDocument("current")
toclayer = pythonaddins.GetSelectedTOCLayerOrDataFrame()
#list fields for selected toc layer. but only text fields
fieldlist = arcpy.ListFields(toclayer)  
#init row number
r = 0
#check first two rows of attribute table
with arcpy.da.SearchCursor(toclayer, fieldlist) as cursor:
    for row in cursor:
        #search tables until a match between any field of the first row of
        #the toclayer and table columns is found
        match = False
        for table in tables:
            #read from excel file using pandas
            try:
                df = pd.read_excel(table, "SHEETNAME?!?!?!")
            except:
                arcpy.AddMessage("No Excel file found at: {}".format(table))
            #convert pandas dataframe to dictionary
            tabledict = df.to_dict()

            #init field list for update cursor 
            updatefields = []
            for key in tabledict.keys():
                updatefields.append(key)
                #intersect value list with column to find joinkey and join field
                intersection = set(row) & set(tabledict[key].values())
                if len(intersection) == 1:
                    match = True
                    #set join key to column name (key) where value was found as well as join field
                    joinkey = key
                    joinfield = fieldlist[row.index(intersection)]
                    #remove key from update fields list and insert joinfield at beginning
                    updatefields.remove(key)
                    #updatefields.insert(0, joinfield)
                    #create dictionary with found key
                    trtabledict = df.transpose().to_dict()
                    joindict = {trtabledict[r][joinkey]: delkey(v, joinkey) for r, v in trtabledict.items()}
                    #stop iterating keys
                    break
            #if a match was found stop iterating tables
            if match:
                break
        #count rows of cursor stop comparing if row > two or when match is found
        r += 1
        if match:
            break
        elif r >= 2:
            arcpy.AddMessage("Join failed. No matching values found in tables.")
            break


CopyFields(toclayer, joinfield, joindict, updatefields)  



#validate join => check if there are rows without match and list unmatched joinfield values


