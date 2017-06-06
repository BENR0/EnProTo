import arcpy
import numpy as np
import os


class split_lines_by_points(object):
    def __init__(self):
        self.label = "splitlinesbypoints"
        self.description = "Split lines by points"
        self.canRunInBackground = False

    def getParameterInfo(self):
        points_lyr = arcpy.Parameter(
            displayName="Layer with points.",
            name="wea_lyr",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Input")

        #wea_lyr.filter.list = ["POINT"]

        lines_lyr = arcpy.Parameter(
            displayName="Layer with lines.",
            name="flug_lyr",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Input")

        #flug_lyr.filter.list = ["LINE"]

        out_lyr = arcpy.Parameter(
            displayName="Output Layer",
            name="out_lyr",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Output")

        parameters = [points_lyr, lines_lyr, out_lyr]

        return parameters

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        #check if Exemplare field exists

       return

    def updateMessages(self, parameters):
        if parameters[1].hasBeenValidated:
            exemplare_field = arcpy.ListFields(parameters[1].value, "Exemplare")
            if len(exemplare_field) < 1:
                parameters[1].setErrorMessage("No >>Exemplare<< field could be found.")
            else:
                parameters[1].clearMessage()

        return

    def execute(self, parameters, messages):

        #Input
        points = parameters[0].valueAsText
        lines = parameters[1].valueAsText
        outputLayer = parameters[2].valueAsText

        split_main(lines, points, outputLayer)

        return



def split_main(lines, points, output):
    ######
    #split lines at point code from http://gis.stackexchange.com/questions/101472/split-line-at-a-point-with-arcgis-10-1-basic-level-license
    line_fc = lines
    point_fc = points
    point_fc_desc = arcpy.Describe(point_fc)
    in_spatial_reference = point_fc_desc.spatialReference

    # clear up in_memory workspace
    arcpy.Delete_management("in_memory")

    #can use CopyFeatures to write the geometries to disk when troubleshooting
    buffered_point_fc = r"C:\Users\Benjamin.Roesner\Documents\ArcGIS\Default.gdb\PointsBuffered"
    intersected_line_fc = r"C:\Users\Benjamin.Roesner\Documents\ArcGIS\Default.gdb\LineIntersected"
    symmetrical_difference_line_fc = r"C:\Users\Benjamin.Roesner\Documents\ArcGIS\Default.gdb\LineIntersectedSymmDiff"
    wkspace = arcpy.env.workspace
    single_part_splitted_lines = r"C:\Users\Benjamin.Roesner\Documents\ArcGIS\Default.gdb\SplittedLines"
    total_splitted_lines = r"C:\Users\Benjamin.Roesner\Documents\ArcGIS\Default.gdb\TotalSplittedLines"
        #os.path.join(wkspace, "TotalSplittedLines")

    #total_splitted_lines_attributed = r"in_memory\TotalSplittedLinesAttributed"
        #os.path.join(wkspace, "TotalSplittedLinesAttributed")

    total_splitted_lines_attributed = r"C:\Users\Benjamin.Roesner\Documents\ArcGIS\Default.gdb\TotalSplittedLinesattributed"
    #arcpy.TruncateTable_management(total_splitted_lines)

    #arcpy.CreateFeatureclass_management(r"C:\Users\Benjamin.Roesner\Documents\ArcGIS\Default.gdb", "SplittedLines")
    arcpy.CreateFeatureclass_management(r"C:\Users\Benjamin.Roesner\Documents\ArcGIS\Default.gdb", "TotalSplittedLines")
    #arcpy.CreateFeatureclass_management(r"C:\Users\Benjamin.Roesner\Documents\ArcGIS\Default.gdb", "TotalSplittedLinesattributed")




    #--- reference dictionaries ----------------#
    points_id_geometry_dict = {} #{pointID: pointGeometry}
    lines_id_geometry_dict = {} #{lineID: lineGeometry}

    search_cursor = arcpy.da.SearchCursor(point_fc,["FID","SHAPE@"])
    for point_feature in search_cursor:
        points_id_geometry_dict[point_feature[0]] = point_feature[1]
    del search_cursor

    search_cursor = arcpy.da.SearchCursor(line_fc,["FID","SHAPE@"])
    for line_feature in search_cursor:
        lines_id_geometry_dict[line_feature[0]] = line_feature[1]
    del search_cursor
    #-------------------------------------------#

    points_list =[]
    lines_list = []

    dictionary_lines_points = {} #{lineID: pointID} or {lineID: (pointID, pointID,...)}

    point_cursor = arcpy.da.SearchCursor(point_fc,["SHAPE@","FID"])
    line_cursor = arcpy.da.SearchCursor(line_fc,["SHAPE@","FID"])

    for point in point_cursor:
        point_geom_and_id = [point[0],point[1]]
        points_list.append(point_geom_and_id)

    for line in line_cursor:
        line_geom_and_id = [line[0],line[1]]
        lines_list.append(line_geom_and_id)

    del point_cursor
    del line_cursor

    for line in lines_list:
        for point in points_list:
            if line[0].contains(point[0]): #finding what points are on what lines
                msg = "LineID:" + str(line[1]) + "PointID:" + str(point[1])
                #arcpy.AddMessage(msg)
                if not line[1] in dictionary_lines_points: #handling situations when multiple points are on the same line
                    dictionary_lines_points[line[1]] = (point[1],) #lineid is key, point ids is value (can be a tuple)
                    #arcpy.AddMessage(dictionary_lines_points[line[1]])
                else:
                    dictionary_lines_points[line[1]] = dictionary_lines_points[line[1]] + (point[1],) #making tuple for "" line: (point ids) ""

    #arcpy.AddMessage(dictionary_lines_points)
    nn = 0
    for key_line in dictionary_lines_points.keys(): #iterating each line in the line_fc
        arcpy.AddMessage(nn)
        pointID = dictionary_lines_points.get(key_line) #getting what PointID have match to lineID
        #arcpy.AddMessage(pointID)

        if not isinstance(pointID,tuple):
            input_point_geom_object = points_id_geometry_dict.get(pointID) #obtain point geometry based on pointID
            multipoints = input_point_geom_object
        else:
            merged_point_geometries = arcpy.Array() #constructing a multipoint (if multiple points are on the same line)
            for pointID_element in pointID:
                input_point_geom_object = points_id_geometry_dict.get(pointID_element)
                merged_point_geometries.add(input_point_geom_object.centroid) #creating array of points
                multipoints = arcpy.Multipoint(merged_point_geometries,in_spatial_reference)

        line_geometry_object = lines_id_geometry_dict.get(key_line) #obtain line geometry based on LineID

        buffered_point = multipoints.buffer(0.1) #same units as the geometry
        intersected_line = buffered_point.intersect(line_geometry_object,2) #2 - polyline returned
        symmetrical_difference_line = intersected_line.symmetricDifference(line_geometry_object)
        arcpy.MultipartToSinglepart_management(symmetrical_difference_line,single_part_splitted_lines)
        arcpy.Integrate_management(single_part_splitted_lines,"0.1 Meters")
        arcpy.Append_management(single_part_splitted_lines,total_splitted_lines,"NO_TEST")
        arcpy.Delete_management(single_part_splitted_lines)

        nn += 1

    arcpy.SpatialJoin_analysis(target_features=total_splitted_lines,
                                   join_features=line_fc,
                                   out_feature_class=total_splitted_lines_attributed,
                                   join_operation="JOIN_ONE_TO_ONE",join_type="KEEP_ALL",
                                   match_option="INTERSECT",search_radius="#",distance_field_name="#")



    ##TODO
    #iterate through line features that did not have any points located on them (distanceTo geometry method / select by location)
    #if there are any points located within the search distance >> move them on line and run the logic >> append to the output fc
    #if no point features are located within the search distance >> append them directly to the output fc
    return total_splitted_lines_attributed



# import os
# import shapefile
# from shapely.geometry import *
#
# def cut(line_file, point_file, cut_file):
#     """Cuts a line shapefile using a point shapefile."""
#     # Line shapefile we are going to cut
#     line_sf = shapefile.Reader(line_file)
#
#     # Point shapefile containing the cut points
#     point_sf = shapefile.Reader(point_file)
#
#     # Prefix for output shapefile file name
#     cut_fn = cut_file
#
#     # Create the shapefile writer for the output line shapefile
#     cut_sf = shapefile.Writer(shapefile.POLYLINE)
#
#     cut_sf.fields = list(line_sf.fields)
#
#     for sr in line_sf.shapeRecords():
#         line = LineString(sr.shape.points)
#         envelope = box(*line.bounds)
#         pt = None
#         for shape in point_sf.shapes():
#             pt2 = Point(*shape.points[0])
#             if envelope.contains(pt2):
#                 if not pt:
#                     pt = pt2
#                     continue
#                 if line.distance(pt2) < line.distance(pt):
#                     pt = pt2
#         cut_line = None
#         if not pt:
#             cut_line = [line]
#         else:
#             coords = list(line.coords)
#             distance = line.project(pt)
#             if distance <= 0.0 or distance >= line.length:
#                 return [LineString(line)]
#             for i, p in enumerate(coords):
#                 pd = line.project(Point(p))
#                 if pd == distance:
#                     return [LineString(coords[:i+1]), LineString(coords[i:])]
#                 if pd > distance:
#                     cp = line.interpolate(distance)
#                     return [
#                         LineString(coords[:i] + [(cp.x, cp.y)]),
#                         LineString([(cp.x, cp.y)] + coords[i:])]
#         for part in cut_line:
#             coords = list(part.coords)
#             cut_sf.line([coords])
#             cut_sf.record(*sr.record)
#
#     cut_sf.save("{}.shp".format(cut_fn))
#
#     # If the line shapefile has a cry file, copy it for the new file.
#     shp_name = os.path.splitext(line_sf.shp.name)[0]
#     line_prj = "{}.prj".format(shp_name)
#     if os.path.exists(line_prj):
#         with open(line_prj, "r") as line_crs:
#             crs = line_crs.read()
#             with open("{}.prj".format(cut_fn), "w") as cut_crs:
#                 cut_crs.write(crs)
