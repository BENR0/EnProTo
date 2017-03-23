# -*- coding: utf-8 -*-
import arcpy
import pythonaddins
import logging
import pandas as pd
import subprocess
import urllib
import os
import glob
import _winreg
import re
import pyperclip
import csv
import time
import datetime as dt
import colorsys
import comtypes
import zipfile

#from Tkinter import Tk
#import json
#from mod.FeaturesToGPX import *


#logging
#logging.basicConfig(filename=r"L:\Ablage_Mitarbeiter\Benjamin\dokumente\enproto.log", level=logging.INFO)
#logging.basicConfig(format='%(asctime)s %(message)s', datefmt="%Y%d%m %H%M%S")

# create logger
logger = logging.getLogger('EnProTo_user_stats')
logger.setLevel(logging.INFO)

handler = logging.FileHandler(r"L:\Ablage_Mitarbeiter\Benjamin\dokumente\enproto.log")
handler.setLevel(logging.INFO)

# create formatter
#formatter = logging.Formatter(format='%(asctime)s %(message)s', datefmt="%Y%d%m %H%M%S")
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', "%Y%d%m %H%M%S")

# add formatter to ch
handler.setFormatter(formatter)

# add ch to logger
logger.addHandler(handler)



############################
#helper functions
############################
def ListLocks(shp_path):
    pattern = shp_path + "*.sr.lock"
    matches = glob.glob(pattern)

    nodeDict = {"HUNB20": "Isgard", "HUNB10": "Benjamin", "HUPC28": "Maren", "HUPC24": "Yvonne", "HUPC30": "Andi", "HUPC07": "Jann"}
    lockslist = []
    locks = ""
    for item in matches:
        split_pattern = "shp."
        tmp = re.split(split_pattern, item)[1]
        tmp = re.split(".[0-9]+.[0-9]+.sr.lock", tmp)[0]
        print(tmp)
        node_name = os.environ["COMPUTERNAME"]
        if tmp == node_name:
            tmp = tmp + " (Eigener Rechner)"

        lockslist.append(tmp)
        ##locks += tmp + nodeDict[tmp] + "\n"
        locks += tmp + "\n"

    return locks, lockslist

# Snippets.py
# ************************************************
# Updated for ArcGIS 10.3
# ************************************************
# Requires installation of the comtypes package
# Available at: http://sourceforge.net/projects/comtypes/
# Once comtypes is installed, the following modifications
# need to be made for compatibility with ArcGIS 10.2:
# 1) Delete automation.pyc, automation.pyo, safearray.pyc, safearray.pyo
# 2) Edit automation.py
# 3) Add the following entry to the _ctype_to_vartype dictionary (line 794):
#    POINTER(BSTR): VT_BYREF|VT_BSTR,
# ************************************************

#**** Initialization ****

def GetLibPath():
    """Return location of ArcGIS type libraries as string"""
    # This will still work on 64-bit machines because Python runs in 32 bit mode
    import _winreg
    keyESRI = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, "SOFTWARE\\ESRI\\Desktop10.4")
    return _winreg.QueryValueEx(keyESRI, "InstallDir")[0] + "com\\"

def GetModule(sModuleName):
    """Import ArcGIS module"""
    from comtypes.client import GetModule
    sLibPath = GetLibPath()
    GetModule(sLibPath + sModuleName)

def GetStandaloneModules():
    """Import commonly used ArcGIS libraries for standalone scripts"""
    GetModule("esriSystem.olb")
    GetModule("esriGeometry.olb")
    GetModule("esriCarto.olb")
    GetModule("esriDisplay.olb")
    GetModule("esriGeoDatabase.olb")
    GetModule("esriDataSourcesGDB.olb")
    GetModule("esriDataSourcesFile.olb")
    GetModule("esriOutput.olb")

def GetDesktopModules():
    """Import basic ArcGIS Desktop libraries"""
    GetModule("esriFramework.olb")
    GetModule("esriArcMapUI.olb")
    GetModule("esriArcCatalogUI.olb")

#**** Helper Functions ****

def NewObj(MyClass, MyInterface):
    """Creates a new comtypes POINTER object where\n\
    MyClass is the class to be instantiated,\n\
    MyInterface is the interface to be assigned"""
    from comtypes.client import CreateObject
    try:
        ptr = CreateObject(MyClass, interface=MyInterface)
        return ptr
    except:
        return None

def CType(obj, interface):
    """Casts obj to interface and returns comtypes POINTER or None"""
    try:
        newobj = obj.QueryInterface(interface)
        return newobj
    except:
        return None

def CLSID(MyClass):
    """Return CLSID of MyClass as string"""
    return str(MyClass._reg_clsid_)

def InitStandalone():
    """Init standalone ArcGIS license"""
    # Set ArcObjects version
    import comtypes
    from comtypes.client import GetModule
    g = comtypes.GUID("{6FCCEDE0-179D-4D12-B586-58C88D26CA78}")
    GetModule((g, 1, 0))
    import comtypes.gen.ArcGISVersionLib as esriVersion
    import comtypes.gen.esriSystem as esriSystem
    pVM = NewObj(esriVersion.VersionManager, esriVersion.IArcGISVersion)
    if not pVM.LoadVersion(esriVersion.esriArcGISDesktop, "10.2"):
        return False
    # Get license
    pInit = NewObj(esriSystem.AoInitialize, esriSystem.IAoInitialize)
    ProductList = [esriSystem.esriLicenseProductCodeAdvanced, \
                   esriSystem.esriLicenseProductCodeStandard, \
                   esriSystem.esriLicenseProductCodeBasic]
    for eProduct in ProductList:
        licenseStatus = pInit.IsProductCodeAvailable(eProduct)
        if licenseStatus != esriSystem.esriLicenseAvailable:
            continue
        licenseStatus = pInit.Initialize(eProduct)
        return (licenseStatus == esriSystem.esriLicenseCheckedOut)
    return False

def GetApp(app="ArcMap"):
    """In a standalone script, retrieves the first app session found.\n\
    app must be 'ArcMap' (default) or 'ArcCatalog'\n\
    Execute GetDesktopModules() first"""
    if not (app == "ArcMap" or app == "ArcCatalog"):
        print "app must be 'ArcMap' or 'ArcCatalog'"
        return None
    import comtypes.gen.esriFramework as esriFramework
    import comtypes.gen.esriArcMapUI as esriArcMapUI
    import comtypes.gen.esriCatalogUI as esriCatalogUI
    pAppROT = NewObj(esriFramework.AppROT, esriFramework.IAppROT)
    iCount = pAppROT.Count
    if iCount == 0:
        return None
    for i in range(iCount):
        pApp = pAppROT.Item(i)
        if app == "ArcCatalog":
            if CType(pApp, esriCatalogUI.IGxApplication):
                return pApp
            continue
        if CType(pApp, esriArcMapUI.IMxApplication):
            return pApp
    return None

def GetCurrentApp():
    """Gets an IApplication handle to the current app.\n\
    Must be run inside the app's Python window.\n\
    Execute GetDesktopModules() first"""
    import comtypes.gen.esriFramework as esriFramework
    return NewObj(esriFramework.AppRef, esriFramework.IApplication)

def Msg(message="Hello world", title="PythonDemo"):
    from ctypes import c_int, WINFUNCTYPE, windll
    from ctypes.wintypes import HWND, LPCSTR, UINT
    prototype = WINFUNCTYPE(c_int, HWND, LPCSTR, LPCSTR, UINT)
    fn = prototype(("MessageBoxA", windll.user32))
    return fn(0, message, title, 0)


def AddRectangleElement(position = (10.0, 25.0), bgcolor = (255,0,0), bgtransparency = 0,
        sigwidth = 1.0, sigheight = 0.5, tag = "test"):

    '''
    position: where to place text box
    bgcolor: background color of text. Default no background at all.
    tag: string to attach to the element to be able to identify it later.
    '''

    GetDesktopModules()
    import comtypes.gen.esriFramework as esriFramework
    pApp = GetCurrentApp()
    import comtypes.gen.esriArcMapUI as esriArcMapUI
    import comtypes.gen.esriSystem as esriSystem
    import comtypes.gen.esriGeometry as esriGeometry
    import comtypes.gen.esriCarto as esriCarto
    import comtypes.gen.esriDisplay as esriDisplay
    import comtypes.gen.stdole as stdole

    # Get midpoint of page layout
    #
    pDoc = pApp.Document
    pMxDoc = CType(pDoc, esriArcMapUI.IMxDocument)
    pMap = pMxDoc.PageLayout
    pAV = CType(pMap, esriCarto.IActiveView)
    #pSD = pAV.ScreenDisplay
    #pEnv = pAV.Extent
    #dX = pEnv.XMax - position[0] #(pEnv.XMin + pEnv.XMax) / 2
    #dY = pEnv.YMax + position[1] #(pEnv.YMin + pEnv.YMax) / 2
    dX = position[0]
    dY = position[1]

    #lower left point of rectangle envelope
    pRecLowerLeft = NewObj(esriGeometry.Point, esriGeometry.IPoint)
    pRecLowerLeft.PutCoords(dX, dY)
    #upper right point of rectangle envelope
    pRecUpperRight = NewObj(esriGeometry.Point, esriGeometry.IPoint)
    pRecUpperRight.PutCoords(dX + sigwidth, dY + sigheight)

    #create rectangle envelope
    pRecEnv = NewObj(esriGeometry.Envelope, esriGeometry.IEnvelope)
    pRecEnv.LowerLeft = pRecLowerLeft
    pRecEnv.UpperRight = pRecUpperRight

    #transform RGB color to HSV colorspace
    print(bgcolor)
    bgcolor = colorsys.rgb_to_hsv(int(bgcolor[0])/255.0, int(bgcolor[1])/255.0, int(bgcolor[2])/255.0)
    print(bgcolor)
    #bgcolor = (bgcolor[0], bgcolor[2] * (1.0 - bgtransparency), bgcolor[1])
    #create color object for background
    pbgColor = NewObj(esriDisplay.HsvColor, esriDisplay.IHsvColor)
    #pbgColor = NewObj(esriDisplay.RgbColor, esriDisplay.IRgbColor)
    pbgColor.Hue = int(bgcolor[0]*100)
    pbgColor.Saturation = int(bgcolor[1]*100 * (1 - bgtransparency))
    pbgColor.Value = int(bgcolor[2]*100)
    print(pbgColor.Hue)
    print(pbgColor.Saturation)
    print(pbgColor.Value)
    #pbgColor.Red = int(bgcolor[0])
    #pbgColor.Blue = int(bgcolor[2])
    #pbgColor.Green = int(bgcolor[1])
    #pbgColor.Transparency = bgtransparency

    #create simple line symboll
    pLineSymbol = NewObj(esriDisplay.SimpleLineSymbol, esriDisplay.ISimpleLineSymbol)
    pLineSymbol.Width = 0.5

    #create simple Fill symbol for background
    pFillSymbol = NewObj(esriDisplay.SimpleFillSymbol, esriDisplay.ISimpleFillSymbol)
    pFillSymbol.Color = pbgColor
    pFillSymbol.Outline = pLineSymbol
    #pFillSymbol.Style = esriDisplay.esriSimpleFillStyle.esriSFSSolid
    
    #create text box object and set font and color
    #pFillShapeElement = NewObj(esriDisplay.FillShapeElement, esriDisplay.IFillShapeElement)
    #pFillShapeElement.Symbol = pFillSymbol

    # Create text element and add it to map
    pRectangleElement = NewObj(esriCarto.RectangleElement, esriCarto.IRectangleElement)
    pElement = CType(pRectangleElement, esriCarto.IFillShapeElement)
    pElement.Symbol = pFillSymbol
    pElement = CType(pRectangleElement, esriCarto.IElement)
    pElement.Geometry = pRecEnv
    pElement = CType(pRectangleElement, esriCarto.IElementProperties3)
    #tag element with name
    pElement.Name = tag
    
    pGC = CType(pMap, esriCarto.IGraphicsContainer)
    pGC.AddElement(pElement, 0)
    
    pGCSel = CType(pMap, esriCarto.IGraphicsContainerSelect)
    pGCSel.SelectElement(pElement)
    iOpt = esriCarto.esriViewGraphics + \
           esriCarto.esriViewGraphicSelection
    pAV.PartialRefresh(iOpt, None, None)


def AddTextElement(bStandalone = False, position = (10.0, 25.0), txtfont = "Arial",
     txtsize = 12, txtcolor = (0,0,0),
     txtbold = False, txtstring = "txtElemTemplate", bg = False,
     bgcolor = (255,255,255), tag = "txtElemTemplate"):


    '''
    position: where to place text box
    bgcolor: background color of text. Default no background at all.
    txtfont: font type. Default Arial.
    txtsize: font size. Default 12pt.
    txtcolor: font color. Default black.
    txtbold: bold font (boolean). Default False.
    txtstring: text string to be displaye by text box.
    bg: create background for textfield. Default False.
    bgcolor: Background color. Default white.
    tag: string to attach to the element to be able to identify it later.
    '''

    GetDesktopModules()
    import comtypes.gen.esriFramework as esriFramework
    if bStandalone:
        InitStandalone()
        pApp = GetApp()
        pFact = CType(pApp, esriFramework.IObjectFactory)
    else:
        pApp = GetCurrentApp()
    import comtypes.gen.esriArcMapUI as esriArcMapUI
    import comtypes.gen.esriSystem as esriSystem
    import comtypes.gen.esriGeometry as esriGeometry
    import comtypes.gen.esriCarto as esriCarto
    import comtypes.gen.esriDisplay as esriDisplay
    import comtypes.gen.stdole as stdole

    # Get midpoint of focus map

    pDoc = pApp.Document
    pMxDoc = CType(pDoc, esriArcMapUI.IMxDocument)
    pMap = pMxDoc.PageLayout
    pAV = CType(pMap, esriCarto.IActiveView)
    pSD = pAV.ScreenDisplay
    pEnv = pAV.Extent
    dX = pEnv.XMax - position[0] #(pEnv.XMin + pEnv.XMax) / 2
    dY = pEnv.YMax - position[1] #(pEnv.YMin + pEnv.YMax) / 2
    if bStandalone:
        pUnk = pFact.Create(CLSID(esriGeometry.Point))
        pPt = CType(pUnk, esriGeometry.IPoint)
    else:
        pPt = NewObj(esriGeometry.Point, esriGeometry.IPoint)
    pPt.PutCoords(dX, dY)

    # Create text symbol
	#create color object for text
    if bStandalone:
        pUnk = pFact.Create(CLSID(esriDisplay.RgbColor))
        pColor = CType(pUnk, esriDisplay.IRgbColor)
    else:
        pColor = NewObj(esriDisplay.RgbColor, esriDisplay.IRgbColor)
    pColor.Red = txtcolor[0]
    pColor.Blue = txtcolor[1]
    pColor.Green = txtcolor[2]
    
	#create color object for background
    if bStandalone:
        pbgUnk = pFact.Create(CLSID(esriDisplay.RgbColor))
        pbgColor = CType(pbgUnk, esriDisplay.IRgbColor)
    else:
        pbgColor = NewObj(esriDisplay.RgbColor, esriDisplay.IRgbColor)
    pbgColor.Red = int(bgcolor[0])
    pbgColor.Blue = int(bgcolor[1])
    pbgColor.Green = int(bgcolor[2])

    #create simple Fill symbol for background
    pFillSymbol = NewObj(esriDisplay.SimpleFillSymbol, esriDisplay.ISimpleFillSymbol)
    pFillSymbol.Color = pbgColor
    #pFillSymbol.Style = esriDisplay.esriSimpleFillStyle.esriSFSSolid
    
    #create font face object
    if bStandalone:
        pUnk = pFact.Create(CLSID(stdole.StdFont))
        pFontDisp = CType(pUnk, stdole.IFontDisp)
    else:
        pFontDisp = NewObj(stdole.StdFont, stdole.IFontDisp)
    pFontDisp.Name = txtfont
    pFontDisp.Bold = txtbold
    
    #create text box object and set font and color
    if bStandalone:
        pUnk = pFact.Create(CLSID(esriDisplay.TextSymbol))
        pTextSymbol = CType(pUnk, esriDisplay.ITextSymbol)
    else:
        pTextSymbol = NewObj(esriDisplay.TextSymbol, esriDisplay.ITextSymbol)
    pTextSymbol.Font = pFontDisp
    pTextSymbol.Color = pColor
    pTextSymbol.Size = txtsize
    pTextSymbol.HorizontalAlignment = esriDisplay.esriTextHorizontalAlignment(0)
    
    #create background object
    if bg:
        if bStandalone:
            pUnk = pFact.Create(CLSID(esriDisplay.BalloonCallout))
    	    pTextBackground = CType(pUnk, esriDisplay.ITextBackground)
        else:
            pTextBackground = NewObj(esriDisplay.BalloonCallout, esriDisplay.ITextBackground)

       #add color to pTextBackground before applying it to pTextSymbol
        pTextBackground.Symbol = pFillSymbol
        print(pTextBackground.Symbol.Color)
        pFormattedTS = CType(pTextSymbol, esriDisplay.IFormattedTextSymbol)
        pFormattedTS.Background = pTextBackground

   
    # Create text element and add it to map
    if bStandalone:
        pUnk = pFact.Create(CLSID(esriCarto.TextElement))
        pTextElement = CType(pUnk, esriCarto.ITextElement)
    else:
        pTextElement = NewObj(esriCarto.TextElement, esriCarto.ITextElement)
    pTextElement.Symbol = pTextSymbol
    pTextElement.Text = txtstring
    pElement = CType(pTextElement, esriCarto.IElement)
    pElement.Geometry = pPt
    pElement = CType(pTextElement, esriCarto.IElementProperties3)
    #tag element with name
    pElement.Name = tag
    
    pGC = CType(pMap, esriCarto.IGraphicsContainer)
    pGC.AddElement(pElement, 0)
    
    pGCSel = CType(pMap, esriCarto.IGraphicsContainerSelect)
    pGCSel.SelectElement(pElement)
    iOpt = esriCarto.esriViewGraphics + \
           esriCarto.esriViewGraphicSelection
    pAV.PartialRefresh(iOpt, None, None)

    # Get element width

    #iCount = pGCSel.ElementSelectionCount
    #pElement = pGCSel.SelectedElement(iCount - 1)
    #pEnv = NewObj(esriGeometry.Envelope, esriGeometry.IEnvelope)
    #pElement.QueryBounds(pSD, pEnv)
    #print "Width = ", pEnv.Width
    

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


        #registrykey2 = _winreg.OpenKey(_winreg.HKEY_CURRENT_USER, r"Software\ESRI\Desktop10.3\Export\ExportDlg", 0,_winreg.KEY_WRITE)
		#_winreg.SetValueEx(registrykey2,"WorkingDirectory",0,_winreg.REG_SZ,lastexport)
		#_winreg.CloseKey(registrykey2)
		pass

class OpenPathForSelectedLayer(object):
    """Implementation for OpenPathForSelectedLayer.button (Button)"""
    def __init__(self):
        self.enabled = True
        self.checked = False
    def onClick(self):
        import os
        import logging

        #usage logging
        user = os.environ.get("USERNAME")
        logging.info('%s, %s', "Open path for layer", user)

        def get_geodatabase_path(input_table, toclayer):
            '''Return the Geodatabase path from the input table or feature class.
            :param input_table: path to the input table or feature class
            '''
            workspace = os.path.dirname(input_table)
            if [any(ext) for ext in ('.gdb', '.mdb', '.sde') if ext in os.path.splitext(workspace)]:
                return workspace
            else:
                filename = str(toclayer) + ".shp"
                return os.path.join(input_table, filename)

        mxd = arcpy.mapping.MapDocument("CURRENT")
        toclayer = pythonaddins.GetSelectedTOCLayerOrDataFrame()
        desc = arcpy.Describe(toclayer)
        path = get_geodatabase_path(desc.path, toclayer)
        #path = os.path.join(desc.path, str(toclayer) + ".shp")
        print(path)
       
        subprocess.Popen('explorer /select, "{0}"'.format(path))
        pass

class OpenPathForCurrentMXD(object):
    """Implementation for OpenPathForCurrentMXD.button (Button)"""
    def __init__(self):
        self.enabled = True
        self.checked = False
    def onClick(self):
        import logging

        #usage logging
        user = os.environ.get("USERNAME")
        logger.info('%s, %s', "Open path for mxd", user)

        mxd = arcpy.mapping.MapDocument("CURRENT")
        mxdpath = mxd.filePath
       
        subprocess.Popen('explorer /select, "{0}"'.format(mxdpath))
        pass
        
class CopyPathToClipboard(object):
    """Implementation for CopyPathToClipboard.button (Button)"""
    def __init__(self):
        self.enabled = True
        self.checked = False
    def onClick(self):
        import logging

        #usage logging
        user = os.environ.get("USERNAME")
        logging.info('%s, %s', "Copy path to clipboard", user)


        mxd = arcpy.mapping.MapDocument("CURRENT")
        toclayer = pythonaddins.GetSelectedTOCLayerOrDataFrame()
        desc = arcpy.Describe(toclayer)
        path = desc.path

        pyperclip.copy(path + "\\" + str(toclayer) +  ".shp")


        #r = Tk()
        #r.withdraw()
        #r.clipboard_clear()
        #r.clipboard_append(path)

        #df=pd.DataFrame(['Text to copy'])
        #df.to_clipboard(index=False,header=False)

        pass

class FindDefinitionQuerys(object):
    """Implementation for FindDefinitionQuerys.button (Button)"""
    def __init__(self):
        self.enabled = True
        self.checked = False
    def onClick(self):
        import logging

        #usage logging
        user = os.environ.get("USERNAME")
        logger.info('%s, %s', "Find definition queries", user)


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
        import logging

        #usage logging
        user = os.environ.get("USERNAME")
        logger.info('%s, %s', "List locks", user)

        mxd = arcpy.mapping.MapDocument("CURRENT")

        lyrs = arcpy.mapping.ListLayers(mxd)
        out_msg = ""

        #HUNB20: Isgard
        #HUNB10: Benjamin
        #HUPC28: Maren
        #HUPC24: Yvonne
        #HUPC07: Jann
        #HUPC30: Andi
        for lyr in lyrs:
            if not lyr.isGroupLayer:                      #Is layer a group layer
                # print(lyr.isGroupLayer)
                # for glyr in arcpy.mapping.ListLayers(lyr): #loop layer in group layer
                #     if glyr != lyr:
                #         out_msg += str(lyr) + " is locked by user(s):\n"
                #         #get lyr path
                #         desc = arcpy.Describe(lyr)
                #         lyr_path = desc.path + "\\" + str(lyr) +  ".shp"
                #         #get all locks for this layer and append to msg string
                #         strlocks, listlocks = ListLocks(lyr_path)
                #         out_msg += strlocks + "\n"
           # else:
                out_msg += str(lyr) + " is locked by user(s):\n"
                #get lyr path
                try:
                    desc = arcpy.Describe(lyr)
                    lyr_path = desc.path + "\\" + str(lyr) +  ".shp"
                    #get all locks for this layer and append to msg string
                    strlocks, listlocks = ListLocks(lyr_path)
                except:
                    pass

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
        import logging

        #usage logging
        user = os.environ.get("USERNAME")
        logger.info('%s, %s', "Calculate area", user)


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
            arcpy.CalculateField_management(toclayer, fieldName2, "round(!SHAPE.AREA@SQUAREMETERS!, 2)", "PYTHON")

        except Exception, e:
            #if error occurs, print line number and error message
            import traceback, sys
            tb = sys.exc_info()[2]
            print("Line %i" % tb.tb_lineno)
            print(e.message)

        pass
        
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
        
class BatchReproject(object):
    """Implementation for BatchReproject.button (Button)"""
    def __init__(self):
        self.enabled = True
        self.checked = False
    def onClick(self):

        mxd = arcpy.mapping.MapDocument("current")
        df = arcpy.mapping.ListDataFrames(mxd)[0]

        #pop up message box to query for archiving of old layers
        archive = pythonaddins.MessageBox('Move old layers to archive after reprojecting?', 'INFO', 4)
        print(archive)

        #data frame projection
        try:
            outcscode = df.spatialReference.PCSCode
            outcs = df.spatialReference
        except:
            err_dfcs = pythonaddin.MessageBox("Data frame has no coordinate system assigned.", "Error", 0)
            print(err_dfcs)

        GK2 = "31466"
        GK3 = "31467"
        GK4 = "31468"
        GK5 = "31469"
        #NZ-E EPSG Codes
        utmn31NZ = "5651"
        utmn32NZ = "5652"
        utmn33NZ = "5653"
        # "normal" UTM Codes
        utmn31 = "25831"
        utmn32 = "25832"
        utmn33 = "25833"
        wgs = "4326"
        gt = "DHDN_To_ETRS_1989_8_NTv2"
        gt1 = "ETRS_1989_To_WGS_1984"
        gt2 = "DHDN_To_WGS_1984_4_NTv2"
        #gt = "DHDN_to_WGS_1984_4_NTv2 + ETRS_1989_to_WGS_1984"
        trafoDict = {GK2: gt2, GK3: gt2, GK4: gt2, GK5: gt2, utmn31NZ: gt1, utmn32NZ: gt1, utmn33NZ: gt1, utmn31: gt1, utmn32: gt1, utmn33:gt1}


        if str(outcscode) in [utmn31, utmn32, utmn33, utmn31NZ, utmn32NZ, utmn33NZ]:
            coordtag = "_UTM"
        elif str(outcscode) in [GK2, GK3, GK4, GK5]:
            coordtag = "_GK"
        else:
            outcs_msg = "Please choose one of the following coordinate systems for the data frame: " + trafoDict.keys()
            err_outcs = pythonaddin.MessageBox(outcs_msg, "Error", 0)
            print(err_outcs)

        mxdpath = os.path.splitext(mxd.filePath)[0]
        logfile = mxdpath + "_trafo.log"
        #iterate over all layers in toc
        try:
            tfile = open(logfile, 'w')
            for infc in arcpy.mapping.ListLayers(mxd): #arcpy.ListFeatureClasses(mxd):
                # Determine if the input has a defined coordinate system,
                # can't project it if it does not
                indesc = arcpy.Describe(infc)
                insc = indesc.spatialReference
                #log trafos
                log = str(infc) + str(insc.PCSCode) + " ->"
                if indesc.spatialReference.Name == "Unknown":
                    print ("Skipped this fc due to undefined coordinate system: " + infc)
                    log = log + " skipped\n"
                    #write log
                    logfile.write(log)
                    continue
                elif insc == outcs:
                    log = log + " no need for reprojection (coordinate systems are the same.\n"
                    #write log
                    logfile.write(log)
                    continue
                else:
                    # Determine the new output feature class path and name
                    #get path of current feature class and append coord system
                    infcpath = infc.dataSource
                    #split path from extension
                    infcpath = os.path.splitext(infcpath)
                    #create coordsystem and extension
                    extension = coordtag + ".shp"
                    outfc = infcpath[0] + extension
                    #get list of possible transformations
                    trafolist = arcpy.ListTransformations(insc, outcs)
                    print(outfc)

                    if len(trafolist) > 0:
                        #run project tool with projection of data frame and apply transformation
                        #Project_management (in_dataset, out_dataset, out_coor_system, {transform_method},
                        #{in_coor_system}, {preserve_shape}, {max_deviation})
                        newlayerpath = arcpy.Project_management(infc, outfc, outcs, trafolist[0])
                        log = log + " " + str(outfc) + " " + "(" + trafolist[0] + ")\n"
                    else:
                        newlayerpath = arcpy.Project_management(infc, outfc, outcs)
                        log = log + " " + str(outfc) + " " + "(No transformation used)\n"


                    #apply style of old layer to new layer
                    newlayername = os.path.splitext(os.path.basename(str(newlayerpath)))[0]
                    newlayer = arcpy.mapping.ListLayers(mxd, newlayername)[0]
                    arcpy.ApplySymbologyFromLayer_management(newlayer, infc)

                    #write log
                    tfile.write(log)

                    #remove old layer from project
                    arcpy.mapping.RemoveLayer(df, infc)

                    #check messages
                    print(arcpy.GetMessages())

            tfile.close()

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
        import logging

        #usage logging
        user = os.environ.get("USERNAME")
        logger.info('%s, %s', "New Shape", user)


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
        base = re.split('05_GIS',mxdpath)[0]
        startpath = os.path.join(base, "05_GIS/av_daten")

        #create filename
        #construct date
        today = dt.date.today()
        strdate = str(today.year) + str(today.month) + str(today.day)
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

        #get path where to save shp from user
        savepath = pythonaddins.SaveDialog("Speichern unter", contstr, startpath, "", "Shapefile (*.shp)")
        print(savepath)
        #catch if save dialog is exited with cancel
        if savepath != None:
            print("copy features")
            #copy shape to user specified path
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
        
class ChangePlankopf(object):
    """Implementation for ChangePlankopf.combobox (ComboBox)"""
    def __init__(self):
        self.editable = True
        self.enabled = True
        self.dropdownWidth = 'WWWWWWWWWWWWWWWWWW'
        self.width = ''
    def onSelChange(self, selection):

        import logging

        #usage logging
        user = os.environ.get("USERNAME")
        logger.info('%s, %s', "Change Plankopf", user)

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
        zeichnerl = [u"Dipl. Geo. Julia Krimkowski",u"M.Sc. Geoökol. Isgard Rudloff",u"M.Sc. Landsch.-Ökol. Andreas Menzel",u"B.Sc. Geo. Benjamin Rösner",u"Dipl. Geo. Yvonne Dernedde",u"Dipl. Geo. Sandra Kiessling"]
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
        elif user == "Yvonne.Dernedde":
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
        import logging

        #usage logging
        user = os.environ.get("USERNAME")
        logger.info('%s, %s', "Layer paths to file", user)


        mxd = arcpy.mapping.MapDocument("CURRENT")

        lyrs = arcpy.mapping.ListLayers(mxd)
        
        startpath = "L:\Ablage_Mitarbeiter"
        outfile = pythonaddins.SaveDialog("Speichern unter", "layers.txt", startpath)
        tfile = open(outfile, 'w') #open('L:\Ablage_Mitarbeiter\Benjamin\dokumente\layers.txt', 'w')
        #outfile = csv.writer(tfile)
        
        for lyr in lyrs:
            if lyr.supports('visible'):
                if lyr.isFeatureLayer:
                    path = lyr.dataSource.encode("utf-8") + "\n"
                #elif lyr.isGroupLayer:
                 #   path = lyr.name.encode("utf-8") + "\n"

                    tfile.write(path)

        tfile.close()
        pass
        
class ToGPX(object):
    """Implementation for ToGPX.button (Button)"""
    def __init__(self):
        self.enabled = True
        self.checked = False
    def onClick(self):
        import logging

        #usage logging
        user = os.environ.get("USERNAME")
        logger.info('%s, %s', "To GPX", user)


        '''
        Tool Name:  Features to GPX
        Source Name: FeaturesToGPX.py
        Version: ArcGIS 10.1+ or ArcGIS Pro 1.0+
        Author: Esri
        Contributors: Matt Wilkie
           (https://github.com/maphew/arcgiscom_tools/blob/master/Features_to_GPX/FeaturesToGPX.py)

        Required Arguments:
            Input Features (features): path to layer or featureclass on disk
            Output Feature Class (file): path to GPX which will be created
        Optional Arguements:
            Zero date (boolean): If no date exists, use this option to force dates to epcoh
                start, 1970-Jan-01. This will allow GPX files to open in Garmin Basecamp
            Pretty (boolean): Output gpx file will be "pretty", or easier to read.

        Description:
            This tool takes input features (layers or featureclass) with either point or
            line geometry and converts into a .GPX file. Points and multipoint features
            are converted in to WPTs, lines are converted into TRKS. If the features conform
            to a known schema, the output GPX file will honor those fields.
        '''


        try:
            from xml.etree import cElementTree as ET
        except:
            from xml.etree import ElementTree as ET
        import arcpy
        import time
        import datetime

        unicode = str

        gpx = ET.Element("gpx", xmlns="http://www.topografix.com/GPX/1/1",
                         xalan="http://xml.apache.org/xalan",
                         xsi="http://www.w3.org/2001/XMLSchema-instance",
                         creator="Esri",
                         version="1.1")


        def prettify(elem):
            """Return a pretty-printed XML string for the Element.
            """
            from xml.dom import minidom
            rough_string = ET.tostring(elem, 'utf-8')
            reparsed = minidom.parseString(rough_string)
            return reparsed.toprettyxml(indent="  ")


        def featuresToGPX(inputFC, outGPX, zerodate, pretty):
            ''' This is called by the __main__ if run from a tool or at the command line
            '''

            descInput = arcpy.Describe(inputFC)
            if descInput.spatialReference.factoryCode != 4326:
                arcpy.AddWarning("Input data is not projected in WGS84,"
                                 " features were reprojected on the fly to create the GPX.")

            generatePointsFromFeatures(inputFC, descInput, zerodate)

            # Write the output GPX file
            try:
                gpxFile = open(outGPX, "w")
                if pretty:
                    gpxFile.write(prettify(gpx))
                else:
                    ET.ElementTree(gpx).write(gpxFile, encoding="UTF-8", xml_declaration=True)
            except TypeError:
                arcpy.AddError("Error serializing GPX into the file.")
            finally:
                gpxFile.close()


        def generatePointsFromFeatures(inputFC, descInput, zerodate=False):
            def attHelper(row):
                # helper function to get/set field attributes for output gpx file

                pnt = row[1].getPart()
                valuesDict["PNTX"] = str(pnt.X)
                valuesDict["PNTY"] = str(pnt.Y)

                Z = pnt.Z if descInput.hasZ else None
                if Z or ("ELEVATION" in cursorFields):
                    valuesDict["ELEVATION"] = str(Z) if Z else str(row[fieldNameDict["ELEVATION"]])
                else:
                    valuesDict["ELEVATION"] = str(0)

                valuesDict["NAME"] = row[fieldNameDict["NAME"]] if "NAME" in fields else " "
                valuesDict["DESCRIPT"] = row[fieldNameDict["DESCRIPT"]] if "DESCRIPT" in fields else " "

                if "DATETIMES" in fields:
                    row_time = row[fieldNameDict["DATETIMES"]]
                    formatted_time = row_time if row_time else " "
                elif zerodate and "DATETIMES" not in fields:
                    formatted_time = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(0))
                else:
                    formatted_time = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(0)) if zerodate else " "

                valuesDict["DATETIMES"] = formatted_time

                return

            # -------------end helper function-----------------


            def getValuesFromFC(inputFC, cursorFields):

                previousPartNum = 0
                startTrack = True

                # Loop through all features and parts
                with arcpy.da.SearchCursor(inputFC, cursorFields, spatial_reference="4326",
                                           explode_to_points=True) as searchCur:
                    for row in searchCur:
                        if descInput.shapeType == "Polyline":
                            for part in row:
                                newPart = False
                                if not row[0] == previousPartNum or startTrack is True:
                                    startTrack = False
                                    newPart = True
                                previousPartNum = row[0]

                                attHelper(row)
                                yield "trk", newPart

                        elif descInput.shapeType == "Multipoint" or descInput.shapeType == "Point":
                            # check to see if data was original GPX with "Type" of "TRKPT" or "WPT"
                            trkType = row[fieldNameDict["TYPE"]].upper() if "TYPE" in fields else None

                            attHelper(row)

                            if trkType == "TRKPT":
                                newPart = False
                                if previousPartNum == 0:
                                    newPart = True
                                    previousPartNum = 1

                                yield "trk", newPart

                            else:
                                yield "wpt", None

            # ---------end get values function-------------


            # Get list of available fields
            fields = [f.name.upper() for f in arcpy.ListFields(inputFC)]
            valuesDict = {"ELEVATION": 0, "NAME": "", "DESCRIPT": "", "DATETIMES": "", "TYPE": "", "PNTX": 0, "PNTY": 0}
            fieldNameDict = {"ELEVATION": 0, "NAME": 1, "DESCRIPT": 2, "DATETIMES": 3, "TYPE": 4, "PNTX": 5, "PNTY": 6}

            cursorFields = ["OID@", "SHAPE@"]

            for key, item in valuesDict.items():
                if key in fields:
                    fieldNameDict[key] = len(cursorFields)  # assign current index
                    cursorFields.append(key)  # build up list of fields for cursor
                else:
                    fieldNameDict[key] = None

            for index, gpxValues in enumerate(getValuesFromFC(inputFC, cursorFields)):

                if gpxValues[0] == "wpt":
                    wpt = ET.SubElement(gpx, 'wpt', {'lon': valuesDict["PNTX"], 'lat': valuesDict["PNTY"]})
                    wptEle = ET.SubElement(wpt, "ele")
                    wptEle.text = valuesDict["ELEVATION"]
                    wptTime = ET.SubElement(wpt, "time")
                    wptTime.text = valuesDict["DATETIMES"]
                    wptName = ET.SubElement(wpt, "name")
                    wptName.text = valuesDict["NAME"]
                    wptDesc = ET.SubElement(wpt, "desc")
                    wptDesc.text = valuesDict["DESCRIPT"]

                else:  # TRKS
                    if gpxValues[1]:
                        # Elements for the start of a new track
                        trk = ET.SubElement(gpx, "trk")
                        trkName = ET.SubElement(trk, "name")
                        trkName.text = valuesDict["NAME"]
                        trkDesc = ET.SubElement(trk, "desc")
                        trkDesc.text = valuesDict["DESCRIPT"]
                        trkSeg = ET.SubElement(trk, "trkseg")

                    trkPt = ET.SubElement(trkSeg, "trkpt", {'lon': valuesDict["PNTX"], 'lat': valuesDict["PNTY"]})
                    trkPtEle = ET.SubElement(trkPt, "ele")
                    trkPtEle.text = valuesDict["ELEVATION"]
                    trkPtTime = ET.SubElement(trkPt, "time")
                    trkPtTime.text = valuesDict["DATETIMES"]
                    
                    
        mxd = arcpy.mapping.MapDocument("CURRENT")
        #get first data frame of map document

        #get directory of map document
        mxdpath = mxd.filePath
        #split path by GIS directory, keep first part and add GIS folder again
        base = re.split('05_GIS', mxdpath)[0]
        startpath = base + "05_GIS/av_daten"

        inputFC = pythonaddins.GetSelectedTOCLayerOrDataFrame()
        outGPX = pythonaddins.SaveDialog("Speichere GPX", "GPS.gpx", startpath, "", "GPX (*.gpx)")
        zerodate = False
        pretty = False

        if outGPX != None:
            featuresToGPX(inputFC, outGPX, zerodate, pretty)

        pass
        
class TB(object):
    """Implementation for TB.button (Button)"""
    def __init__(self):
        self.enabled = True
        self.checked = False
    @property
    def onClick(self):
        import logging

        #usage logging
        user = os.environ.get("USERNAME")
        logger.info('%s, %s', "Legend", user)


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
            AddRectangleElement(position = position, bgcolor = sigcolor, bgtransparency = transparency, tag = "sig")
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

        #add initial text element
        AddTextElement(position = (0.0, 0.0), txtstring = "txtElemTemplate")
        AddTextElement(position = (0.0, 0.0), txtstring = "txtElemTemplate2", tag = "txtElemTemplate2", txtsize = headingFontSize)
#       #get created text element
        mxd = arcpy.mapping.MapDocument("current")
        txtElemTemplate = arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT")[1]
        txtElemTemplate2 = arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT")[0]

        #get selected toc layer
        toclayer = pythonaddins.GetSelectedTOCLayerOrDataFrame()
        #get layer transparency
        toclayertrans = toclayer.transparency
        print(toclayertrans)
        #toclayertrans = 0.0
        #get data from attribute table and create dictionary
        fieldlist = ["CODE_NR", "CODE_NAME", "BTTGROUP", "SIGCOLOR"]
        #init dict
        legendDict = dict()
        with arcpy.da.SearchCursor(toclayer, fieldlist) as cursor:
            for row in set(cursor):
                item = row[0] + ": " + row[1]
                if row[2] in legendDict:
                    legendDict[row[2]]["items"].append(item)
                else:
                    legendDict[row[2]] = {"items" : [item], "color" : tuple(row[3].split(","))}

        #create legend
        for key in legendDict.keys():
            print("create item")
            iPosition = createHeader(iPosition, legendDict[key]["color"],toclayertrans, key, txtElemTemplate2)
            iPosition = listItems(iPosition, legendDict[key]["items"], txtElemTemplate)

        #clean uo
        #del legendDict, iPosition
        pass
        
class OSM(object):
    """Implementation for OSM.combobox (ComboBox)"""
    def __init__(self):
        self.editable = True
        self.enabled = True
        self.dropdownWidth = 'WWWWWWW'
        self.width = ''
    def onSelChange(self, selection):
        import arcpy
        from arcpy import env
        import urllib
        import urllib2
        import os
        import shutil
        import ssl
        import itertools
        import logging

        #usage logging
        user = os.environ.get("USERNAME")
        logger.info('%s, %s', "OSM", user)


        #maybe a security risk but solves the issue with
        #URLError: <urlopen error [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed (_ssl.c:590)>
        ssl._create_default_https_context = ssl._create_unverified_context
        import errno

        def make_dir(path):
            try:
                os.makedirs(path)
            except OSError:
                if not os.path.isdir(path):
                    raise

        # load the OpenStreetMap specific toolbox
        try:
            arcpy.ImportToolbox(r"c:\program files (x86)\arcgis\desktop10.4\ArcToolbox\Toolboxes\OpenStreetMap Toolbox.tbx")
        except:
            msg = pythonaddins.MessageBox("Please install the ArcGIS Editor for OSM", "Error", 0)
            print(msg)
            raisev



        ######################
        ##constants
        ######################
        timeout = 600

        GK2 = "31466"
        GK3 = "31467"
        GK4 = "31468"
        GK5 = "31469"
        #NZ-E EPSG Codes
        utmn31NZ = "5651"
        utmn32NZ = "5652"
        utmn33NZ = "5653"
        # "normal" UTM Codes
        utmn31 = "25831"
        utmn32 = "25832"
        utmn33 = "25833"
        wgs = "4326"
        gt = "DHDN_To_ETRS_1989_8_NTv2"
        gt1 = "ETRS_1989_To_WGS_1984"
        gt2 = "DHDN_To_WGS_1984_4_NTv2"
        #gt = "DHDN_to_WGS_1984_4_NTv2 + ETRS_1989_to_WGS_1984"
        trafoDict = {GK2: gt2, GK3: gt2, GK4: gt2, GK5: gt2, utmn31NZ: gt1, utmn32NZ: gt1, utmn33NZ: gt1, utmn31: gt1, utmn32: gt1, utmn33:gt1}

        ######################
        #begin of code
        ######################
        #get bounding box of current viewing extent or (largest) layer?
        toclayer = pythonaddins.GetSelectedTOCLayerOrDataFrame()
        try:
            lyrDesc = arcpy.Describe(toclayer)
        except:
            msg = pythonaddins.MessageBox("No TOC layer is selected.", "Error", 0)
            print(msg)

        #get path to project
        mxd = arcpy.mapping.MapDocument("current")
        try:
            mxdpath = mxd.filePath
        except:
            print("Could not get projects path. Probably project is not saved yet.")

        #get data frame and df PCS
        df  = arcpy.mapping.ListDataFrames(mxd)[0]
        try:
            dfPCS = df.spatialReference.PCSCode
        except:
            err_dfcs = pythonaddins.MessageBox("Data frame has no coordinate system assigned.", "Error", 0)
            print(err_dfcs)

        if not str(dfPCS) in trafoDict.keys():
            outMSG = ("The data frame coordinate system did not"
            "match any of the following EPSG codes: {0}. Please choose one of the specified"
            "coordinate systems before using this tool in order to prevent inaccuracies while reprojecting.").format(trafoDict.keys())
            PCSwarning = pythonaddins.MessageBox(outMSG, "PCS Warning", 0)
            print(PCSwarning)
            ####### Continue does not work, loop breaks if error is encounterd!!!!########

        #create path to GIS data directory in project directory
        rootpath = re.split("05_GIS",mxdpath)[0]
        OSMdir = os.path.join(rootpath, "05_GIS", "av_daten", "10_OSM", selection)

        #create osm dir if not existent
        make_dir(OSMdir)

        #create temp directory for storing osm xml data
        OSMtmp = os.path.join(OSMdir, "ztmp")
        make_dir(OSMtmp)


        lyrext = lyrDesc.extent
        #transform coord of extent if not WGS84
        #lyrPCS = lyrDesc.spatialReference.PCSCode
        if not str(dfPCS) == wgs:
            if str(dfPCS) in [utmn31, utmn32, utmn33, utmn31NZ, utmn32NZ, utmn33NZ]:
                lyrext = lyrext.projectAs(wgs, gt1)
            elif str(dfPCS) in [GK2, GK3, GK4, GK5]:
                lyrext = lyrext.projectAs(wgs, gt2)
            else:
                lyrext = lyrext.projectAs(wgs)

        bboxtuple = (lyrext.YMin, lyrext.XMin, lyrext.YMax, lyrext.XMax)


        overpassurl = "https://overpass-api.de/api/interpreter?data=[out:xml];"

        #end tag for query
        etag = """out body; >; out skel qt;"""

        ######## queries #########
        churches = """
        (
          node["amenity"="place_of_worship"]["religion"="christian"]{0};
          way["amenity"="place_of_worship"]["religion"="christian"]{0};
          relation["amenity"="place_of_worship"]["religion"="christian"]{0};
        );"""

        ###### Straßennetz
        qHighway = """
        (
          way["highway"]{0};
        );"""

        tHighway = ["highway", "name", "surface", "maxspeed", "access", "opening_date", "lanes", "source", "oneway"]

        ###### Windenergieanlagen
        qWEA = """
        (
          node [power=generator][power_source=wind]{0};
          node [power=generator]["generator:source"=wind]{0};
          way [power=generator][power_source=wind]{0};
          way [power=generator]["generator:source"=wind]{0};
        ); """

        tWEA = ["power", "power:source", "note", "operator", "manufacturer", "manufacturer:type", "generator:output:electricity", "height", "rotor:diameter" ]

        ###### Krankenhäuser
        qHospitals = """
         (
          node["amenity"="hospital"]{0};
          way["amenity"="hospital"]{0};
          relation["amenity"="hospital"]{0};
         );"""

        tHospitals = ["name"]

        ###### Schutzgebiete
        #for classes of protected areas see http://wiki.openstreetmap.org/wiki/DE:Tag:boundary%3Dprotected_area
        qSchutz = """
         (
          node["boundary"="protected_area"]{0};
          way["boundary"="protected_area"]{0};
          relation["boundary"="protected_area"]{0};
         );"""
        #http://wiki.openstreetmap.org/wiki/Tag:boundary%3Dprotected_area
        tSchutz = ["name", "protected_title", "protected_object", "related_law", "operator", "website", "protected_class"]

        ###### Energieleitungen und Masten
        qPowerline = """
         (
          node["power"="line"]{0};
          way["power"="line"]{0};
          relation["power"="line"]{0};
          node["power"="cable"]{0};
          way["power"="cable"]{0};
          relation["power"="cable"]{0};
          node["power"="minor_underground_cable"]{0};
          way["power"="minor_underground_cable"]{0};
          relation["power"="minor_underground_cable"]{0};
          node["power"="minor_line"]{0};
          way["power"="minor_line"]{0};
          relation["power"="minor_line"]{0};
          node["power"="tower"]{0};
          way["power"="tower"]{0};
          relation["power"="tower"]{0};
          node["power"="planned"]{0};
          way["power"="planned"]{0};
          relation["power"="planned"]{0};
          node["power"="construction"]{0};
          way["power"="construction"]{0};
          relation["power"="construction"]{0};
         );"""

        tPowerline = ["cables", "operator", "frequency", "voltage", "source", "wires", "power", "note"]

        #waterways and bodys
        qWater = """
        (
         way["waterway"="riverbank"]{0};
         relation["waterway"="riverbank"]{0};
         way["waterway"="river"]{0};
         way["waterway"="stream"]{0};
         way["waterway"="river"]{0};
         way["waterway"="canal"]{0};
         way["waterway"="drain"]{0};
         way["waterway"="ditch"]{0};
         way["natural"="water"]{0};
        );"""

        tWater = ["name", "water", "waterway", "width", "tunnel", "boat"]

        qForest = """
        (
         way["natural" = "wood"]{0};
         way["landuse" = "forest"]{0};
        );"""

        tForest = ["name", "leaf_type", "leaf_cycle"]

        #make dictionary from queries
        qDict = ({"Streets": [qHighway, tHighway], "WEA": [qWEA, tWEA], "Powerlines": [qPowerline, tPowerline], "Hospitals": [qHospitals, tHospitals],
                 "Schutzgebiete": [qSchutz, tSchutz], "Gewaesser": [qWater, tWater], "Wald": [qForest, tForest]})

        #create full query
        query = (qDict[selection][0] + etag).format(bboxtuple)
        #fetch data from Overpass
        requesturl = overpassurl + urllib.quote_plus(query)

        myRequest = urllib2.Request(requesturl)
        #file path for temporary osm data
        OSMdata = os.path.join(OSMtmp, "osm.xml")
        try:
            OSMurlHandle = urllib2.urlopen(myRequest, timeout=timeout)
            OSMfile = file(OSMdata, 'wb')
            OSMfile.write(OSMurlHandle.read())
            OSMfile.close()
        except urllib2.URLError, e:
            raise
            # if hasattr(e, 'reason'):
            #     AddMsgAndPrint('Unable to reach the server.', 2)
            #     AddMsgAndPrint(e.reason, 2)
            # elif hasattr(e, 'code'):
            #     AddMsgAndPrint('The server was unable to fulfill the request.', 2)
            #     AddMsgAndPrint(e.code, 2)

        #check if xml file contains "out of memory" message
        with open(OSMdata, "r") as infile:
            for line in itertools.islice(infile, 8):
                if "Query run out of memory" in line:
                    msg = pythonaddins.MessageBox("Query run out of memory on Server.\n Reason: Probably selected extent to large.", "Server message", 0)
                    print(msg)
                    raise SystemExit

        # define the names for the feature dataset and the feature classes
        #inputName = "OSM"
        inputName = selection
        #set workspace to scratch workspace
        wspace = env.scratchWorkspace

        #check if workspace already contains seleted data and delete
        if arcpy.Exists(os.path.join(wspace, selection)):
            arcpy.Delete_management(os.path.join(wspace, selection))
            arcpy.Delete_management(os.path.join(wspace, selection + "_osm_relation"))
            arcpy.Delete_management(os.path.join(wspace, selection + "_osm_revision"))

        validatedTableName = arcpy.ValidateTableName(inputName, wspace)
        nameOfTargetDataset = os.path.join(wspace, validatedTableName)

        fcpoint = os.path.join(validatedTableName, selection + r"_osm_pt")
        fcline = os.path.join(validatedTableName, selection + r"_osm_ln")
        fcpoly = os.path.join(validatedTableName, selection + r"_osm_ply")

        nameOfPointFeatureClass = os.path.join(wspace, fcpoint)
        nameOfLineFeatureClass = os.path.join(wspace, fcline)
        nameOfPolygonFeatureClass = os.path.join(wspace, fcpoly)

        #import downloaded osm.xml into default database and get attributes
        arcpy.OSMGPFileLoader_osmtools(OSMdata, "CONSERVE_MEMORY", "ALL", nameOfTargetDataset, nameOfPointFeatureClass, nameOfLineFeatureClass, nameOfPolygonFeatureClass)


        # filter the points to only process the attribute carrying nodes
        #filteredPointLayer = 'Only attributed nodes'
        #arcpy.MakeFeatureLayer_management(r'stuttgart\stuttgart_osm_pt', filteredPointLayer, "osmSupportingElement = 'no'")

        # extract the name tag for the filtered point features
        #arcpy.OSMGPAttributeSelector_osmtools(filteredPointLayer, 'name,note')

        tmpLayer = []
        #loop feature classes get attributes and project to coord of project dataframe
        for fc in arcpy.ListFeatureClasses(feature_dataset=selection):
            # extract the name tag for all line features
            print(qDict[selection][1])
            arcpy.OSMGPAttributeSelector_osmtools(fc, qDict[selection][1])
            #export fc to shape database
            arcpy.FeatureClassToShapefile_conversion(os.path.join(wspace, selection, fc), OSMtmp)
            tmpLayer.append(fc)
            outshp = os.path.join(OSMdir, fc + ".shp")
            shptmp = os.path.join(OSMtmp, fc + ".shp")
            arcpy.Project_management(shptmp, outshp, str(dfPCS), trafoDict[str(dfPCS)])


        #delete fc from scratch db afterwards
        arcpy.Delete_management(os.path.join(wspace, selection))
        arcpy.Delete_management(os.path.join(wspace, selection + "_osm_relation"))
        arcpy.Delete_management(os.path.join(wspace, selection + "_osm_revision"))

        #remove layers
        #for lyr in tmpLayer:
         #   rlyr = arcpy.mapping.ListLayers(mxd, lyr, df)[0]
          #  try:
           #     arcpy.mapping.RemoveLayer(df, rlyr)
           # except:
            #    raise
        lyrs = arcpy.mapping.ListLayers(mxd, selection + "*")
        for lyr in lyrs:
            if not lyr.isGroupLayer:
                try:
                    arcpy.mapping.RemoveLayer(df, lyr)
                except:
                    raise

        groupLyr = arcpy.mapping.ListLayers(mxd, selection)[0]
        arcpy.env.workspace = OSMdir
        fcList = arcpy.ListFeatureClasses()
        for f in fcList:
            #nlyr = arcpy.MakeFeatureLayer_management(os.path.join(OSMdir, f))
            lyr = arcpy.mapping.Layer(os.path.join(OSMdir, f))
                #arcpy.mapping.ListLayers(mxd, str(nlyr))[0]
            arcpy.mapping.AddLayerToGroup(df, groupLyr, lyr)


        #move layers to OSM group layer
        #lyrs = arcpy.mapping.ListLayers(mxd, selection + "*")
        #get group layer object
        #groupLyr = arcpy.mapping.ListLayers(mxd, selection)[0]
        #for lyr in lyrs:
        #    if not lyr.isGroupLayer:
        #        arcpy.mapping.AddLayerToGroup(df, groupLyr, lyr)


        #add shapes to project (create group layer?)

        #delete temporary data dir
        try:
            shutil.rmtree(OSMtmp)
        except:
            raise

        pass

    def onEditChange(self, text):
        pass
    def onFocus(self, focused):
        self.items = ["Streets", "WEA", "Powerlines", "Hospitals", "Schutzgebiete", "Gewaesser", "Wald"]
        pass
    def onEnter(self):
        pass
    def refresh(self):
        pass
        
class ZipShapes(object):
    """Implementation for ZipShapes.button (Button)"""
    def __init__(self):
        self.enabled = True
        self.checked = False
    def onClick(self):
        import arcpy
        import pythonaddins
        import os
        import re
        import zipfile
        import datetime as dt
        import logging

        #usage logging
        user = os.environ.get("USERNAME")
        logger.info('%s, %s', "Zip shapes", user)

        #local vars

        def make_dir(path):
            try:
                os.makedirs(path)
            except OSError:
                if not os.path.isdir(path):
                    raise

        # tk inter save file dialog
        # def saveFileDialog(FileExtension, InitialDirectory, DialogTitle):
        #     """
        #     Raises a standard File Save dialog and returns the absolute path of the file
        #     given by the user in the dialog.
        #     An extension can automatically be appended to the end of the return value by specifying
        #     the extension type in the 'FileExtension' parameter.
        #
        #     Usage:
        #         selectFileDialog(".lyr", r"C:\Temp", "Save a file")
        #     """
        #     if not FileExtension:
        #         raise Exception("File extension is a required parameter")
        #     if InitialDirectory == "":
        #         import os
        #         InitialDirectory = os.path.expanduser('~\Documents')
        #     if DialogTitle == "":
        #         DialogTitle = "Save As"
        #     import Tkinter, tkFileDialog
        #     root = Tkinter.Tk()
        #     root.withdraw()
        #     FileToSave = tkFileDialog.asksaveasfilename(defaultextension=FileExtension, initialdir=InitialDirectory, title=DialogTitle)
        #     return FileToSave

        mxd = arcpy.mapping.MapDocument("CURRENT")
        toclayers = pythonaddins.GetSelectedTOCLayerOrDataFrame()

        #get shape file path
        if type(toclayers) is not list:
           toclayers = [toclayers]

        desc = [arcpy.Describe(i) for i in toclayers]

        #get file path of first toc layer
        shp_path = desc[0].path


        #get directory of map document
        #mxdpath = mxd.filePath
        #split path by GIS directory, keep first part and add GIS folder again
        #base = re.split('05_GIS',mxdpath)[0]
        #use shapefile path instead of mxd path to get basepath
        base = re.split('05_GIS',shp_path)[0]
        startpath = os.path.join(base, "12_Datenweitergabe")
        print(startpath)

        #create filename
        #construct date
        today = dt.date.today()
        strdate = str(today.year) + "-" + "{:02d}".format(today.month) + "-" + "{:02d}".format(today.day) + "_ .zip"

        #get path where to save shp from user
        zipfilepath = pythonaddins.SaveDialog("Speichern unter", strdate, startpath, "", "Zipfile (*.zip)")
        #zipfilepath = saveFileDialog("zip", strdate, "Speichern unter")
        #catch if save dialog is exited with cancel
        if zipfilepath != None:
            #splitpath = zipfilepath.split("\\")
            splitpath = zipfilepath.split(".")
            #savedir = os.path.join(*splitpath[0:len(splitpath)-1])

            savedir = splitpath[0]
            make_dir(savedir)

            #open zip file
            with zipfile.ZipFile(os.path.join(savedir, os.path.basename(zipfilepath) + ".zip"), "w") as myzip:
                for shape in toclayers:
                    shpsavepath = os.path.join(savedir, arcpy.Describe(shape).name)

                    #copy shape to user specified path
                    arcpy.CopyFeatures_management(shape, shpsavepath)

                    #add files to zip
                    shpfilename = shpsavepath.split(".")[0]
                    for ext in [".prj", ".dbf", ".shx", ".shp"]:
                        tmpfilename = shpfilename + ext
                        print(tmpfilename)
                        myzip.write(tmpfilename, os.path.basename(tmpfilename))



        pass

class DynBirdTab(object):
    """Implementation for DynBirdTab.button (Button)"""
    def __init__(self):
        self.enabled = True
        self.checked = False
    def onClick(self):
        import arcpy
        import pythonaddins
        import logging

        #usage logging
        user = os.environ.get("USERNAME")
        logger.info('%s, %s', "Dynamic Vogel table", user)

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
        fieldNames = ["Abk", "Name_dt", "Name_wiss"]
        colWidth = 4.0
        smallColWidth = 1.5


        #Add initial text element
        AddTextElement(position = (0.0, 0.0), txtstring = "txtElemTemplate",
                        tag = "txtElemTemplate", txtsize = itemFontSize)
        #get created text element
        mxd = arcpy.mapping.MapDocument("current")
        tableText = arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT")[0]

        toclayer = pythonaddins.GetSelectedTOCLayerOrDataFrame()

        #start coords for elements
        pageWidth = mxd.pageSize.width
        upperX = pageWidth + 3.0
        upperY = 25.0

        #get data from attribute table and store rows as tuples in list
        tabledata = []
        with arcpy.da.SearchCursor(toclayer, fieldNames) as cursor:
            for row in cursor:
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

        pass

class RepairBrokenLayers(object):
    """Implementation for RepairBrokenLayers.button (Button)"""
    def __init__(self):
        self.enabled = True
        self.checked = False
    def onClick(self):
        import logging

        #usage logging
        user = os.environ.get("USERNAME")
        logging.info('%s, %s', "Repair broken layers", user)

        #function to split given path up to gis folder of project
        def pathuptogisdir(path):
            #split path by GIS directory, keep first part and add GIS folder again
            base = re.split('05_GIS',path)[0]
            startpath = os.path.join(base, "05_GIS")

            return startpath

        #get properties of map document
        mxd = arcpy.mapping.MapDocument("CURRENT")
        #get directory of map document
        mxdpath = mxd.filePath

        #get new path
        newpath = pathuptogisdir(mxdpath)
        print(newpath)

        #get old path from broken layer
        brkLyrpath = arcpy.mapping.ListBrokenDataSources(mxd)[0].dataSource
        oldpath = pathuptogisdir(brkLyrpath)
        print(oldpath)

        #fix all broken layers
        mxd.findAndReplaceWorkspacePaths(oldpath, newpath)

        pass


class GetPip(object):
    """Implementation for GetPip.button (Button)"""
    def __init__(self):
        self.enabled = True
        self.checked = False
    def onClick(self):
        #get pip install script
        urllib.urlretrieve(r"https://bootstrap.pypa.io/get-pip.py", r"C:\Python27\ArcGIS10.3\Scripts\get_pip.py")
        #install pip
        subprocess.call(["python", r"C:\Python27\ArcGIS10.3\Scripts\get_pip.py"])
        #get setup tools
        #urllib.urlretrieve(r"https://bootstrap.pypa.io/ez_setup.py", r"C:\Python27\ArcGIS10.3\Scripts\ez_setup.py")
        #install setuptools
        #subprocess.call([pythonpath, r"C:\Python27\ArcGIS10.3\Scripts\ez_setup.py"])

        subprocess.call([r"L:\Ablage_Mitarbeiter\Benjamin\pandas-0.13.1.win32-py2.7.exe"])
        pass