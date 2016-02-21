import shutil
import subprocess
import os

addindir = r"C:\Users\ro\Documents\ArcGIS\AddIns\Desktop10.1\{de2881e9-b5ef-4dd1-bd2b-8c2cbe8b49a7}\enproto_addin.esriaddin"
desktop = r"C:\Users\ro\Desktop\EnProTo_addin"
shareddir = r"E:\toolboxes\EnProTo\EnProTo_addin"

#copy folder from shared dir to desktop of virtial machine
if os.path.exists(desktop):
    shutil.rmtree(desktop)
shutil.copytree(shareddir, desktop)
#run make addin script
test = r"C:\Users\ro\Desktop\EnProTo_addin\makeaddin.py" # os.path.join(desktop, "makeaddin.py")
subprocess.call(["python", test])
if os.path.exists(addindir):
    os.remove(addindir)
shutil.copy(os.path.join(desktop, "EnProTo_addin.esriaddin"), addindir)

#subprocess.Popen(["ArcMap.exe"])
