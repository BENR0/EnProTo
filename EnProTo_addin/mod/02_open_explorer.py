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
        
class CopyPathToClipboard(object):
    """Implementation for CopyPathToClipboard.button (Button)"""
    def __init__(self):
        self.enabled = True
        self.checked = False
    def onClick(self):
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

