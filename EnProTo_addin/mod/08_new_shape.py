class NewShapeFromStandardShape(object):
    """Implementation for NewShapeFromStandardShape.combobox (ComboBox)"""
    def __init__(self):
        self.editable = True
        self.enabled = True
        self.dropdownWidth = 'WWWWWWW'
        self.width = ''
    def onSelChange(self, selection):
        import logging

        #usage logging
        log_use(str(self.__class__.__name__))


        #standard shapefile path
        templatedir = r"V:\Vorlagen_CAD_GIS\GIS\Shape_Standard"
        #file names of template shapes
        name_btt_poly = "Biotoptyp_PNL_Projektnummer.shp"
        name_btt_point = "Biotoptyp_Punkte_Projektnummer_PNL.shp"
        name_rna_bird = "RNA_Vogelart_Projektname_Datum.shp"
        name_rast = "Rastvoegel_Projektname_Datum.shp"
        name_horste = "Horste_Projektname_Datum.shp"

        #get properties of map document
        mxd = arcpy.mapping.MapDocument("CURRENT")
        #get first data frame of map document
        df = arcpy.mapping.ListDataFrames(mxd)[0]
        #get coordinate system of data frame
        df_coord = df.spatialReference.PCSCode

        #get directory of map document
        mxdpath = mxd.filePath
        #split path by GIS directory, keep first part and add GIS folder again
        base = re.split('05_GIS',mxdpath)[0]
        startpath = os.path.join(base, "05_GIS/av_daten")

        #create filename
        #construct date
        today = dt.date.today()
        strdate = date.strftime("%Y%m%d")
        print(strdate)
        #get projectname
        project = base.split("\\")[-2]
        #create content block string and path to template file
        if selection == "BTT_poly":
            #create full path of template shape
            templatepath = os.path.join(templatedir,name_btt_poly)
            #create content block string
            contstr = "BTT_" + project + "_" + strdate + "_" + "poly"
        elif selection == "BTT_point":
            templatepath = os.path.join(templatedir,name_btt_point)
            contstr = "BTT_" + project + "_" + strdate + "_" + "point"
        elif selection == "RNA_Voegel":
            templatepath = os.path.join(templatedir,name_rna_bird)
            contstr = "RNA_" + project + "_" + strdate + "_" + "line"
        elif selection == "Rastvoegel":
            templatepath = os.path.join(templatedir,name_rast)
            contstr = "Rastvoegel_" + project + "_" + strdate + "_" + "point"
        elif selection == "Horste":
            templatepath = os.path.join(templatedir,name_horste)
            contstr = "Horste_" + project + "_" + strdate + "_" + "point"
        else:
            notemplate = pythonaddins.MessageBox("No template file found!", "Error", 0)
            print(notemplate)
            #templatepath = ""            #present option to create new shape with specified fields?

        templatepath = templatepath # + ".shp"
        #append shp extension to filename
        constr = constr + ".shp"

        #get path where to save shp from user
        #function for "filter" argument in SaveDialog
        def save_shp(filename):
            if not filename:
                return False
            if os.path.splitext(filename)[1].lower() == ".shp":
                return True
            return False

        savepath = pythonaddins.SaveDialog("Speichern unter", contstr, startpath, save_shp, "Shapefile (*.shp)")
        print(savepath)
        #catch if save dialog is exited with cancel
        if savepath != None:
            print("copy features")
            #copy shape to user specified path
            #TODO:
            # - check if target file exists and throw message
            arcpy.CopyFeatures_management(templatepath, savepath)
            print("define projection")
            #define projection for copied shape
            #create full path with extension first
            filepath = savepath + ".shp"
            arcpy.DefineProjection_management(filepath, df_coord)
            #add layer to document => not needed since define projection already adds shape to project
            #newlayer = arcpy.mapping.Layer(filepath)
            #arcpy.mapping.AddLayer(df, newlayer)
        pass
    def onEditChange(self, text):
        pass
    def onFocus(self, focused):
        self.items = ["BTT_poly", "BTT_point", "RNA_Voegel", "Rastvoegel", "Horste"]
        pass
    def onEnter(self):
        pass
    def refresh(self):
        pass
        
