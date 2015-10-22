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
		lastexport = rootpath + "\\av_daten"
		lastsave = rootpath + "\\av_projekte"
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