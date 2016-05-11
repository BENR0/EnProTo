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