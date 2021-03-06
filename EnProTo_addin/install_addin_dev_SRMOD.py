# -*- coding: utf-8 -*-
import shutil
import subprocess
import os
import traceback

try:
    user = os.environ.get("USERNAME")

    addindir = os.path.join("C:\Users", user, "Documents\ArcGIS\AddIns\Desktop10.5\{de2881e9-b5ef-4dd1-bd2b-8c2cbe8b49a7}\enproto_addin.esriaddin")
    desktop = r"C:\Users\ro\Desktop\EnProTo_addin"
    shareddir = r"E:\toolboxes\EnProTo\EnProTo_addin"
    addinsourcedir = r"L:\Ablage_Mitarbeiter\Benjamin\dev\EnProTo_dev\EnProTo_addin\EnProTo_addin.esriaddin"

    #copy folder from shared dir to desktop of virtial machine
    #if os.path.exists(desktop):
    #    shutil.rmtree(desktop)
    #shutil.copytree(shareddir, desktop)
    #cat together all toolbar scripts
    cat = r"L:\Ablage_Mitarbeiter\Benjamin\dev\EnProTo_dev\EnProTo_addin\cat.py"
    subprocess.call(["python", cat])
    #run make addin script
    test = r"L:\Ablage_Mitarbeiter\Benjamin\dev\EnProTo_dev\EnProTo_addin\makeaddin.py" # os.path.join(desktop, "makeaddin.py")
    subprocess.call(["python", test])
    if os.path.exists(addindir):
        os.remove(addindir)
    shutil.copy(addinsourcedir, addindir)

    #subprocess.Popen(["ArcMap.exe"])
    subprocess.Popen([r"C:\Program Files (x86)\ArcGIS\Desktop10.5\bin\ArcMap.exe"])
except:
    traceback.print_exc()

#raw_input("Press Enter to close") # Python 2
