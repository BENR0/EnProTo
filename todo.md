#### Dokumentation
 - RNA Tool:
    - Exemplare/ Anzahl spalte
    - exemplare/ anzahl spalte beim intersect
    
    
#### Bugs
 - RNA:
    - projection env. workspace defined before
    - fluglayer muss in utm vorliegen (<- Dokumentation?)
    
 - Neuer Shape Button
  - shape exists error
  - df coord error
  
 - locks abfragen
  - umlaute bug
  
  - OSM
   - check if feature class with same name exists

 - GPX Button (Line 1249 generate Points from features in Error in ListFields function). See mail from Andi
 
 - Reproject Button:
    - if the same feature class is in the project a second time don't reproject but update source path
    - choice to archive old layers?


#### Features
  - Doppelte Flächen Button
  - Verschneiden multipler Shapefiles tool
  - Dokumentationsbutton -> Wie viel Zeit in welchem Projekt?
  - repair broken layers
    - replaceDataSource (workspace_path, workspace_type, {dataset_name}, {validate})
    - ListBrokenDataSources (map_document_or_layer)
    
    
     
#### Snippets
##### Broken data sources

This script will search for broken data sources in all map documents that exist in a single folder. A report with map document names and broken sources will be printed.

import arcpy, os
path = r"C:\Project"
for fileName in os.listdir(path):
    fullPath = os.path.join(path, fileName)
    if os.path.isfile(fullPath):
        basename, extension = os.path.splitext(fullPath)
        if extension == ".mxd":
            mxd = arcpy.mapping.MapDocument(fullPath)
            print "MXD: " + fileName
            brknList = arcpy.mapping.ListBrokenDataSources(mxd)
            for brknItem in brknList:
                print "\t" + brknItem.name
del mxd

###### find files in directory tree with python
http://stackoverflow.com/questions/1724693/find-a-file-in-python