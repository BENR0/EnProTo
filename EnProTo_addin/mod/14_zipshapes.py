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

