# -*- coding: utf-8 -*-
import arcpy
import pythonaddins
import subprocess
import os
import glob
import _winreg
import re
import csv
import time
import datetime as dt

############################
#helper functions
############################

def ListLocks(shp_path):
    pattern = shp_path + "*.sr.lock"
    matches = glob.glob(pattern)

    lockslist = []
    locks = ""
    for item in matches:
        split_pattern = "shp."
        tmp = re.split(split_pattern, item)[1]
        tmp = re.split(".[0-9]+.[0-9]+.sr.lock", tmp)[0]
        
        node_name = os.environ["COMPUTERNAME"]
        if tmp == node_name:
            tmp = tmp + "(Eigener Rechner)"

        lockslist.append(tmp)
        locks += tmp + "\n"

    return locks, lockslist

#############################
#definitions for buttons start
#############################
class ChangeBrowsePath(object):
    """Implementation for ChangeBrowsePath.extension2 (Extension)"""
    def __init__(self):
        # For performance considerations, please remove all unused methods in this class.
        self.enabled = True
    def openDocument(self):
	    #get file path of currrent project
		mxd = arcpy.mapping.MapDocument("current")
		mxdpath = mxd.filePath

		#split path by GIS directory, keep first part and add GIS folder again
		rootpath = re.split('05_GIS',mxdpath)[0] + "05_GIS"
		#rootpath = rootpath + r'05_GIS\'

		#create different path for last export/ save/ browse directory
		lastexport = rootpath + "\\plotfiles"
		lastsave = rootpath + "\\av_daten"
		#last browse is same path as last path

		#write registry
		registrykey = _winreg.OpenKey(_winreg.HKEY_CURRENT_USER, r"Software\ESRI\Desktop10.3\ArcCatalog\Settings", 0,_winreg.KEY_WRITE)
		#write LastLocation
		_winreg.SetValueEx(registrykey,"LastLocation",0,_winreg.REG_SZ,rootpath)
		#write LastBrowse
		_winreg.SetValueEx(registrykey,"LastBrowseLocation",0,_winreg.REG_SZ,rootpath)
		#write LastExport
		_winreg.SetValueEx(registrykey,"LastExportToLocation",0,_winreg.REG_SZ,lastexport)
		#write LastSave
		_winreg.SetValueEx(registrykey,"LastSaveToLocation",0,_winreg.REG_SZ,lastsave)
		_winreg.CloseKey(registrykey)
        
        
class OpenPathForSelectedLayer(object):
    """Implementation for OpenPathForSelectedLayer.button (Button)"""
    def __init__(self):
        self.enabled = True
        self.checked = False
    def onClick(self):
        mxd = arcpy.mapping.MapDocument("CURRENT")
        toclayer = pythonaddins.GetSelectedTOCLayerOrDataFrame()
        desc = arcpy.Describe(toclayer)
        path = desc.path
        mxdpath = mxd.filePath
       
        subprocess.Popen('explorer /select, "{0}"'.format(path))
        pass
        
        
class OpenPathForCurrentMXD(object):
    """Implementation for OpenPathForCurrentMXD.button (Button)"""
    def __init__(self):
        self.enabled = True
        self.checked = False
    def onClick(self):
        mxd = arcpy.mapping.MapDocument("CURRENT")
        mxdpath = mxd.filePath
       
        subprocess.Popen('explorer /select, "{0}"'.format(mxdpath))
        pass
        
        
class FindDefinitionQuerys(object):
    """Implementation for FindDefinitionQuerys.button (Button)"""
    def __init__(self):
        self.enabled = True
        self.checked = False
    def onClick(self):
        mxd = arcpy.mapping.MapDocument("CURRENT")

        lyrs = arcpy.mapping.ListLayers(mxd)
        out_msg = ""
        
        for lyr in lyrs:
            if lyr.supports("DEFINITIONQUERY") and lyr.definitionQuery != "":
                out_msg += ">>" + str(lyr) + ": " + str(lyr.definitionQuery) + "\n"
        
        if out_msg == "":
            out_msg = "No definition querys set in project."
        
        result = pythonaddins.MessageBox(out_msg, "Ergebnis", 0)
        print(result)
        pass
        
        
class ListAllLocksForLayers(object):
    """Implementation for ListAllLocksForLayers.button (Button)"""
    def __init__(self):
        self.enabled = True
        self.checked = False
    def onClick(self):

        mxd = arcpy.mapping.MapDocument("CURRENT")

        lyrs = arcpy.mapping.ListLayers(mxd)
        out_msg = ""
        
        for lyr in lyrs:
            out_msg += str(lyr) + " is locked by user(s):\n"
            #get lyr path
            desc = arcpy.Describe(lyr)
            lyr_path = desc.path + "\\" + str(lyr) +  ".shp"
            #get all locks for this layer and append to msg string
            strlocks, listlocks = ListLocks(lyr_path)
            out_msg += strlocks + "\n"
        
        if out_msg == "":
            out_msg = "No lock on any layer found."
        
        result = pythonaddins.MessageBox(out_msg, "Ergebnis", 0)
        print(result)
        pass


class CalculateArea(object):
    """Implementation for CalculateArea.button (Button)"""
    def __init__(self):
        self.enabled = True
        self.checked = False
    def onClick(self):
        try:
            #local vars
            fieldName1 = "AREA_HA"
            fieldName2 = "AREA_QM"
            fieldPrecision = 15 #length of field over all
            fieldScale = 2      #number of decimal places

            mxd = arcpy.mapping.MapDocument("CURRENT")
            toclayer = pythonaddins.GetSelectedTOCLayerOrDataFrame()
            #get list with kields of selected layer
            existfield1 = arcpy.ListFields(toclayer, "AREA_HA")
            existfield2 = arcpy.ListFields(toclayer, "AREA_QM")

            #get computer name
            node_name = os.environ["COMPUTERNAME"]
            #get shape file path
            desc = arcpy.Describe(toclayer)
            shp_path = desc.path
            #check if shape file is locked by other node than the one of the user
            strlocks, listlocks = ListLocks(shp_path)

            #isnotlockedbool = arcpy.TestSchemaLock(toclayer)
            islockedmessage = "Could not add field. Layer: " + str(toclayer) + " is locked by the\
            user(s):\n" + strlocks

            #add fields to table of shapefile if not already existant
            if len(listlocks) > 1:  #isnotlockedbool:
               lockedmessage = pythonaddins.MessageBox(islockedmessage, "Locked", 0)
               print(lockedmessage)
            else:
                if len(existfield1) != 1:
                    arcpy.AddField_management(toclayer, fieldName1, "FLOAT", fieldPrecision, fieldScale)
                else:
                    fieldexistsmsg1 = "Field: " + fieldName1 + " already exists."
                if len(existfield2) != 1:
                     arcpy.AddField_management(toclayer, fieldName2, "FLOAT", fieldPrecision, fieldScale)
                else:
                    fieldexistsmsg2 = "Field: " + fieldName2 + " already exists."

            #calculate geometry
            arcpy.CalculateField_management(toclayer, fieldName1, "!SHAPE.AREA@HECTARES!", "PYTHON")
            arcpy.CalculateField_management(toclayer, fieldName2, "round(!SHAPE.AREA@SQUAREMETERS!, 0)", "PYTHON")

        except Exception, e:
            #if error occurs, print line number and error message
            import traceback, sys
            tb = sys.exc_info()[2]
            print("Line %i" % tb.tb_lineno)
            print(e.message)

        pass
        
        
class BatchReproject(object):
    """Implementation for BatchReproject.button (Button)"""
    def __init__(self):
        self.enabled = True
        self.checked = False
    def onClick(self):

        mxd = arcpy.mapping.MapDocument("current")
        df = arcpy.mapping.ListDataFrames(mxd)[0]

        #data frame projection
        try:
            outcs = df.spatialReference
        except:
            err_dfcs = pythonaddin.MessageBox("Data frame has no coordinate system assigned.", "Error", 0)
            print(err_dfcs)

        #check which coordsystem df uses and create tag for filename
        if "UTM" in outcs.name:
            coordtag = "UTM"
        elif "Gauss_Zone" in outcs.name:
            coordtag = "GK"
        else:
            coordtag = outcs.PCSCode

            #iterate over all layers in toc
        try:
            for infc in arcpy.mapping.ListLayers(mxd): #arcpy.ListFeatureClasses(mxd):
                # Determine if the input has a defined coordinate system,
                # can't project it if it does not
                indesc = arcpy.Describe(infc)
                insc = indesc.spatialReference

                if indesc.spatialReference.Name == "Unknown":
                    print ("skipped this fc due to undefined coordinate system: " + infc)
                else:
                    # Determine the new output feature class path and name
                    #get path of current feature class and append coord system
                    infcpath = infc.dataSource
                    #split path from extension
                    infcpath = os.path.splitext(infcpath)
                    #create coordsystem and extension
                    extension = coordtag + ".shp"
                    outfc = os.path.join(infcpath[0], extension)
                    #get list of possible transformations

                    trafolist = arcpy.ListTransformations(insc, outcs)
                    if len(trafolist) > 0:
                        #run project tool with projection of data frame and apply transformation
                        #Project_management (in_dataset, out_dataset, out_coor_system, {transform_method},
                        #{in_coor_system}, {preserve_shape}, {max_deviation})
                        arcpy.Project_management(infc, outfc, outcs, trafolist[0])
                    else:
                        arcpy.Project_management(infc, outfc, outcs) 
                    
                    # check messages
                    print(arcpy.GetMessages())
                    
        except arcpy.ExecuteError:
            print(arcpy.GetMessages(2))
            
        except Exception as ex:
            print(ex.args[0])

        pass


class NewShapeFromStandardShape(object):
    """Implementation for NewShapeFromStandardShape.combobox (ComboBox)"""
    def __init__(self):
        self.editable = True
        self.enabled = True
        self.dropdownWidth = 'WWWWWWW'
        self.width = ''
    def onSelChange(self, selection):
        #standard shapefile path
        templatedir = "V:\Vorlagen_CAD_GIS\GIS\Shape_Standard"
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
        startpath = re.split('05_GIS',mxdpath)[0] + "05_GIS/av_daten"

        #create filename
        #construct date
        today = dt.date.today()
        strdate = str(today.year) + str(today.month) + str(today.day)
        #get projectname
        project = mxdpath.split("/")[3]
        #create content block string and path to template file
        if selection == "BTT_poly":
            #create full path of template shape
            templatepath = os.path.join(templatedir,name_btt_poly)
            #create content block string
            contstr = "BTT" + project + strdate + "poly"
        elif selection == "BTT_point":
            templatepath = os.path.join(templatedir,name_btt_point)
            contstr = "BTT" + project + strdate + "point"
        elif selection == "RNA_Voegel":
            templatepath = os.path.join(templatedir,name_rna_bird)
            contstr = "RNA" + project + strdate + "line"
        elif selection == "Rastvoegel":
            templatepath = os.path.join(templatedir,name_rast)
            contstr = "Rastvoegel" + project + strdate + "point"
        elif selection == "Horste":
            templatepath = os.path.join(templatedir,name_horste)
            contstr = "Horste" + project + strdate + "point"
        else:
            notemplate = pythonaddins.MessageBox("No template file found!", "Error", 0)
            print(notemplate)
            #templatepath = ""            #present option to create new shape with specified fields?

        #get path where to save shp from user
        savepath = pythonaddins.SaveDialog("Speichern unter", contstr, startpath, "Shapefile (*.shp)")
        
        #copy shape to user specified path
        arcpy.CopyFeatures_management(templatepath, savepath)
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


class ChangePlankopf(object):
    """Implementation for ChangePlankopf.combobox (ComboBox)"""
    def __init__(self):
        self.editable = True
        self.enabled = True
        self.dropdownWidth = 'WWWWWWWWWWWWWWWWWW'
        self.width = ''
    def onSelChange(self, selection):
        mxd = arcpy.mapping.MapDocument("CURRENT")
        #get text and image boxes of mxd
        try:
            txt_comp_name = arcpy.mapping.ListLayoutElements(mxd,"TEXT_ELEMENT","comp_name")[0]
            txt_comp_address = arcpy.mapping.ListLayoutElements(mxd,"TEXT_ELEMENT","comp_adress")[0]
            txt_zeichner = arcpy.mapping.ListLayoutElements(mxd,"TEXT_ELEMENT","zeichner")[0]
            img_logo = arcpy.mapping.ListLayoutElements(mxd,"PICTURE_ELEMENT","comp_logo")[0]
        except:
            element.error = pythonaddins.MessageBox("Check if text and graphic elements exist.",
                    "Error", 0)
            print(element.error)
        
        auftr_csv = csv.DictReader(open(r"V:\Vorlagen_CAD_GIS\GIS\Toolboxes\auftraggeber.csv","r"))
        logodir = "V:\Vorlagen_Logo\extern"

        #populate variable with appropiate auftraggeber data from dictionary
        for row in auftr_csv:
            print(row["name"])
            if selection == row["name"]:
                comp_name = row["name"]
                comp_address = row["adresse"] + "\r\n" + row["plz"] + " " + row["ort"]
                img_src = os.path.join(logodir,row["src"])
        
        #zeichnerl = ["zeichner1", "zeichner1", "zeichner13", u"B. Sc. Benjamin Rösner"]
        zeichnerl = [u"Dipl. Geo. Julia Krimkowski",u"M.Sc. Geoökol. Isgard Rudloff",u"M.Sc. Landsch.-Ökol. Andreas Menzel",u"B.Sc. Geo. Benjamin Rösner",u"Dipl. Geo. Thorsten Knies",u"Dipl. Geo. Sandra Kiessling"]
        #get username from system and set zeichner variable acordingly
        user = os.environ.get("USERNAME")
        if user == "Julia.Krimkowski":
            zeichner = zeichnerl[0]
        elif user == "Isgard.Rudloff":
            zeichner = zeichnerl[1]
        elif user == "Andreas.Menzel":
            zeichner == zeichnerl[2]
        elif user == "Benjamin.Roesner":
            zeichner = zeichnerl[3]
        elif user == "Thorsten.Knies":
            zeichner = zeichnerl[4]
        elif user == "Sandra.Kiessling":
            zeichner = zeichnerl[5]
        else:
            zeichner = txt_zeichner.text
            
        img_logo.sourceImage = img_src
        
        txt_comp_name.text = comp_name
        txt_comp_address.text = comp_address
        txt_zeichner.text = zeichner

        #refresh to see changes
        arcpy.RefreshActiveView()
        pass
    def onFocus(self, focused):
        if focused:
            #read auftraggeber liste as dictionary
            auftr_csv = csv.DictReader(open(r"V:\Vorlagen_CAD_GIS\GIS\Toolboxes\auftraggeber.csv","r"))
        
            #init item list
            self.items = []
            #populate variable with appropiate auftraggeber data from dictionary
            for row in auftr_csv:
                self.items.append(row["name"])
                    #parameters[1].value = row["adresse"] + "\r\n" + row["plz"] + " " + row["ort"]
                    #parameters[2].value = "V:\\Vorlagen_Logo\\extern\\" + row["src"]
        pass
    def onEditChange(self, text):
        pass
    def onEnter(self):
        pass
    def refresh(self):
        pass


class WritePathOfLayersToFile(object):
    """Implementation for WritePathOfLayersToFile.button (Button)"""
    def __init__(self):
        self.enabled = True
        self.checked = False
    def onClick(self):
        mxd = arcpy.mapping.MapDocument("CURRENT")

        lyrs = arcpy.mapping.ListLayers(mxd)
        
        startpath = "L:\Ablage_Mitarbeiter"
        outfile = pythonaddins.SaveDialog("Speichern unter", "layers.txt", startpath)
        tfile = open(outfile, 'w') #open('L:\Ablage_Mitarbeiter\Benjamin\dokumente\layers.txt', 'w')
        #outfile = csv.writer(tfile)
        
        for lyr in lyrs:
            if lyr.isFeatureLayer:
                path = lyr.dataSource.encode("utf-8") + "\n"
                tfile.write(path)

        tfile.close()
        pass
