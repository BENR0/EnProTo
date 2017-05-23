import arcpy


# Set local variables
files = r"L:/Ablage_Mitarbeiter/Benjamin/z_tmp/05_GIS/av_daten/sol_classifizierung/test_tiles"

inRaster = "c:/test/moncton.tif"
spectral_detail = "14.5"
spatial_detail = "10"
min_segment_size = "20"
band_indexes = "4 3 2"

# Check out the ArcGIS Spatial Analyst extension license
arcpy.CheckOutExtension("Spatial")

inRGB = "inrgb raster"
inIR = "inir raster"
outComposite = "filename"


RBand
GBand
BBand
IRBand

#calculate ndvi
#ndvi
#(NIR - RED) / (NIR + RED)
def ndvi(NIR, RED):
    return (NIR - RED) / (NIR + RED)

#enhanced ndvi
#2.5 * ((NIR - RED) / ((NIR + 6*RED - 7.5*Blue) + 1))
def endvi(NIR, RED, BLUE):
    return 2.5 * ((NIR - RED) / ((NIR + 6*RED - 7.5*BLUE) + 1))


ndviBand = ndvi(IRBand, RBand)

#create 4 band raster from rgb and ir raster
arcpy.CompositeBands_management([GBand, BBand, ndviBand], outComposite)


##########################
#segment image
seg_raster = arcpy.sa.SegmentMeanShift(inRaster, spectral_detail, spatial_detail,
                              min_segment_size, min_segment_size)

# Save the output
seg_raster.save("c:/output/moncton_seg.tif")


##########################
#calculate statistics from segmentation
#attributes = "COLOR;MEAN;STD;COUNT;COMPACTNESS;RECTANGULARITY"

# Execute
#compute_att = arcpy.sa.ComputeSegmentAttributes(inSegRaster, in_additional_raster,
                                       attributes)
#save output
#compute_att.save("c:/test/moncton_computeseg.tif")


##########################
#train svm
maxNumSamples = "10"
attributes = "COLOR;MEAN;STD;COUNT;COMPACTNESS;RECTANGULARITY"

# Check out the ArcGIS Spatial Analyst extension license
arcpy.CheckOutExtension("Spatial")

#Execute
arcpy.gp.TrainSupportVectorMachineClassifier(
    inSegRaster, train_features, out_definition,
    in_additional_raster, maxNumSamples, attributes)


##########################
#classify raster
classifiedraster = arcpy.sa.ClassifyRaster(insegras, indef_file, in_additional_raster)

#save output
classifiedraster.save("c:/test/moncton_classified.tif")