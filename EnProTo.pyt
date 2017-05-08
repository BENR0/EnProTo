import arcpy
import os
import csv
import subprocess
import pythonaddins

#import each tool from subdir
from tools.adddescriptiontofeatures import AddDescriptionToFeatures
from tools.plankopf_wizard import PlankopfWizard
from tools.multibufferspeciesexport import MultiBufferSpeciesExport
from tools.polylinetopolygon import PolylineToPolygon
from tools.group_annos_by_pf import GroupAnnosByPF
from tools.legen_waitforit_dary import Legen_WaitForIt_Dary
from tools.kartenserie_to_png import KartenserieToPng
from tools.batchconvertpdftotif import BatchConvertPDFToTif
from tools.buffertool import MultiPurposeBufferTool
from tools.batchaddfieldmerge import BatchAddFieldMerge

#groupannosbypf not found

class Toolbox(object):
    def __init__(self):
        self.label = "EnProTo"
        self.alias = "EnProTo"

        #List of tool classes associated with this toolbox
        #self.tools = [AddDescriptionToFeatures,MultiBufferSpeciesExport,PlankopfWizard,GroupAnnosByPF,Legen_WaitForIt_Dary,PolylineToPolygon,KartenserieToPng]
        self.tools = [AddDescriptionToFeatures,MultiBufferSpeciesExport,KartenserieToPng,BatchConvertPDFToTif,PlankopfWizard,MultiPurposeBufferTool,BatchAddFieldMerge]

