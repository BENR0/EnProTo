# -*- coding: utf-8 -*-
import urllib
import subprocess
import os


if not os.path.exists(r"C:\Python27\ArcGIS10.4\Scripts\get_pip.py"):
    #get pip install script
    #urllib.urlretrieve(r"https://bootstrap.pypa.io/get-pip.py", r"C:\Python27\ArcGIS10.4\Scripts\get_pip.py")
    urllib.urlretrieve(r"https://bootstrap.pypa.io/get-pip.py", r"L:\Ablage_Mitarbeiter\Benjamin\dev\EnProTo_dev\EnProTo_addin\get_pip.py")
    #install pip
    subprocess.call(["python", r"L:\Ablage_Mitarbeiter\Benjamin\dev\EnProTo_dev\EnProTo_addin\get_pip.py"])

import pip
try:
    import comtypes
except ImportError, e:
    pip.main(["install", "comtypes"])
    
    pass
#get setup tools
#urllib.urlretrieve(r"https://bootstrap.pypa.io/ez_setup.py", r"C:\Python27\ArcGIS10.4\Scripts\ez_setup.py")
#install setuptools
#subprocess.call([pythonpath, r"C:\Python27\ArcGIS10.4\Scripts\ez_setup.py"])

#try:
#    import pandas
#except ImportError, e:
#    subprocess.call([r"V:\Vorlagen_Software\toolbox_modules\pandas-0.13.1.win32-py2.7.exe"])
#    pass
    
try:
    import pyperclip
except ImportError, e:
    subprocess.call(["python", "-m", "pip", "install", "pyperclib"])
    #pip.main(["install", "pyperclip"])
    pass

try:
    import pyodbc
except ImportError, e:
    #subprocess.call(["python", "-m", "pip", "install", "pyodbc"])
    #subprocess.call(["pip", "install", "L:\Ablage_Mitarbeiter\Benjamin\pyodbc-4.0.17-cp27-cp27m-win_amd64.whl"])    
    #pip.main(["install", "L:\Ablage_Mitarbeiter\Benjamin\pyodbc-4.0.17-cp27-cp27m-win_amd64.whl"]) #"pyodbc"])
    pass
    
#subprocess.call([r"V:\Vorlagen_Software\toolbox_modules\ArcGIS_Editor_OSM_10_3Desktop\ArcGISEditor10_4\setup.exe"])

raw_input("Press Enter to close")
