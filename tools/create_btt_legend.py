import arcpy
import os
import comtypes
import colorsys
from fieldexistsfunction import fieldExists

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