import arcpy
import pythonaddins
import subprocess

class OpenPathForSelectedLayer(object):
    def __init__(self):
        self.label = "OpenPathForSelectedLayer"
        self.description = "Select a layer in the TOC and open an new explorer window where it resides in the directory tree"
        self.canRunInBackground = False

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):

        return

    def updateMessages(self, parameters):
        
        return

    def execute(self, messages):
		mxd = arcpy.mapping.MapDocument("current")
		toclayer = pythonaddins.GetSelectedTOCLayerOrDataFrame()
		print toclayer
		desc = arcpy.Describe(toclayer)
		print desc
		path = desc.path
		print str(path)

		subprocess.Popen('explorer "{0}"'.format(path))	

		return




