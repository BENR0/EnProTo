import arcpy
import pythonaddins
import subprocess
import os
import _winreg
import re

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
       
        subprocess.Popen('explorer /select, "{0}"'.format(path))
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
        
        result = pythonaddins.MessageBox(out_msg, "Ergebnis", 1)
        print(result)
        pass
        

class NewShapeFromStandardShape(object):
    """Implementation for NewShapeFromStandardShape.combobox (ComboBox)"""
    def __init__(self):
        self.items = ["BTT_poly", "BTT_point", "bird"]
        self.editable = False
        self.enabled = True
        self.dropdownWidth = 'WWWWWW'
        self.width = 'WWWWWW'
    def onSelChange(self, selection):
        #standard shapefile path
        templatedir = ""
        #file names of template shapes
        name_btt_poly = ""
        name_btt_point = ""
        name_bird = ""

        #get properties of map document
        mxd = arcpy.mapping.MapDocument("CURRENT")
        #get first data frame of map document
        df = arcpy.mapping.ListDataFrames(mxd)[0]
        #get coordinate system of data frame
        df_coord = df.spatialReference

        #get directory of map document
        mxdpath = mxd.filePath
        #split path by GIS directory, keep first part and add GIS folder again
        startpath = re.split('05_GIS',mxdpath)[0] + "05_GIS/av_daten"

        #get path where to save shp from user
        savepath = SaveDialog("Speichern unter", "name dataset", startpath)
        
        if selection == "BTT_poly":
            #create full path of template shape
            templatepath = os.path.join(templatedir,name_btt_poly)
        elif selection == "BTT_point":
            templatepath = os.path.join(templatedir,name_btt_point)
        elif selection == "bird":
            templatepath = os.path.join(templatedir,name_bird)
        else:
            #present option to create new shape with specified fields?

        #copy shape to user specified path
        arcpy.CopyFeatures_management(templatepath, savepath)
        #define projection for copied shape
        arcpy.DefineProjection_management(savepath, df_coord)
        #add layer to document
        newlayer = arcpy.mapping.Layer(savepath)
        arcpy.mapping.AddLayer(df, newlayer)
        pass
    def onEditChange(self, text):
        pass
    def onFocus(self, focused):
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
        
        tfile = open('L:\Ablage_Mitarbeiter\Benjamin\dokumente\layers.txt', 'w')
        #outfile = csv.writer(tfile)
        
        for lyr in lyrs:
            if lyr.isFeatureLayer:
                path = lyr.dataSource.encode("utf-8") + "\n"
                tfile.write(path)

        tfile.close()
        pass
