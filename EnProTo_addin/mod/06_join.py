class Join(object):
    """Implementation for Join.button (Button)"""
    def __init__(self):
        self.enabled = True
        self.checked = False
    def onClick(self):
        import logging

        #usage logging
        user = os.environ.get("USERNAME")
        logger.info('%s, %s', "Join", user)
          
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
            fieldlist = [f.name for f in arcpy.ListFields(source_table, "", "String")]
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

        ########
        #pathes to join tables
        #path for each list which can be used for joins
        birds = r"V:\Vorlagen_CAD_GIS\Vorlagen_Kartierungen\Fauna\Voegel\Artenliste_Voegel\Index_deutscher_Vogelnamen_gis.xlsx"
        btt_hessen = r"V:\Vorlagen_CAD_GIS\Vorlagen_Kartierungen\Biotope_Erfassung_Bewertung\Hessen\Biotopschluessel\TNL_Kartierschluessel\TNL_Biotoptypenschluessel_Basis_KV_GIS.xlsx"
        #btt_nrw = r
        btt_nieder = r"V:\Vorlagen_CAD_GIS\Vorlagen_Kartierungen\Biotope_Erfassung_Bewertung\Niedersachsen\Biotopschluessel_Niedersachsen\Schluessel_Tab_fuer_GIS\Tabelle_GIS_BTT_NI_bearb_benjamin_GIS.xls"
        btt_bayern = r"V:\Vorlagen_CAD_GIS\Vorlagen_Kartierungen\Biotope_Erfassung_Bewertung\Bayern\Biotopschluessel\Biotopwertliste_BayKompV\Biotopwertliste_neu_GIS.xlsx"
        #btt_bawu = r
        #fleder = r
        #btt
        ########
        tables = [birds, btt_hessen, btt_bayern, btt_nieder]

        mxd = arcpy.mapping.MapDocument("current")
        toclayer = pythonaddins.GetSelectedTOCLayerOrDataFrame()
        #list fields for selected toc layer. but only text fields
        fieldlist = [f.name for f in arcpy.ListFields(toclayer, "", "String")]

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
                    #try:
                        #df = pd.read_excel(table)
                    #except:
                        #arcpy.AddMessage("No Excel file found at: {}".format(table))
                    #convert pandas dataframe to dictionary
                    #get first sheet of excel file -> 0
                    tabledf = pd.read_excel(table, 0)
                    tabledf = tabledf.fillna("0")
                    tabledict = tabledf.to_dict()

                    #init field list for update cursor 
                    updatefields = []
                    for key in tabledict.keys():
                        updatefields = tabledict.keys()
                        #intersect value list with column to find joinkey and join field
                        intersection = set(row) & set(tabledict[key].values())
                        if len(intersection) == 1:
                            match = True
                            #set join key to column name (key) where value was found as well as join field
                            joinkey = key
                            intersection = list(intersection)[0]
                            joinfield = fieldlist[row.index(intersection)]
                            #remove key from update fields list and insert joinfield at beginning
                            updatefields.remove(key)
                            #updatefields.insert(0, joinfield)
                            #create dictionary with found key
                            trtabledict = tabledf.transpose().to_dict()
                            joindict = {trtabledict[r][joinkey]: delkey(v, joinkey) for r, v in trtabledict.items()}
                            print("created join dict")
                            print(joinkey,joinfield)
                            #print(joindict)
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
        pass
        
