import os.path

import arcpy

# Set the workspace where the "survey_poly" feature class is located
arcpy.env.workspace = "memory"

# Input feature class
in_feature_class = r"C:\Users\hyu\Desktop\GIS_projects\FIND_updates_2023.gdb\survey_poly"

# Output folder where the images will be saved
output_folder = r"C:\Users\hyu\Desktop\pics"

aprx_path = r"C:\Users\hyu\Desktop\GIS_projects\MyProject.aprx"
aprx = arcpy.mp.ArcGISProject(aprx_path)
currmap = aprx.listMaps()[0]

FIND_path = r"C:\Users\hyu\Desktop\GIS_projects\FIND_updates_2023.gdb"
path = arcpy.Describe(f"{FIND_path}/survey_poly").catalogPath
fc_layer = currmap.addDataFromPath(path)
currmap.addLayer(fc_layer)

# feature_layer = currmap.listLayers()[2]  # Assuming the feature class is the first layer in the map


# polygon_fc = arcpy.Describe(f"{FIND_path}/survey_poly_polygon").catalogPath
# arcpy.FeatureToPolygon_management(path, f"{FIND_path}/survey_poly_polygon", "OBJECTID")

# Create a search cursor to iterate over the rows in the feature class
fields = ["SHAPE@", "OBJECTID", "refcode"]  # Adjust the fields as per your requirement
with arcpy.da.SearchCursor(in_feature_class, fields) as cursor:
    for row in cursor:
        print(row[1], row[2], row[0].getPart())

        currID = row[1]
        query = f"OBJECTID = {currID}"
        arcpy.SelectLayerByAttribute_management(in_feature_class, "SUBSET_SELECTION",
                                                query)  # Adjust the query as needed

        # Zoom to the selected feature extent
        # currmap.zoomToSelectedFeatures(in_feature_class)
        map_image = os.path.join(output_folder, "survey_poly_{}.png".format(row[1]))
        # # arcpy.mp.exportToPNG(map_image, resolution=96)
        # currmap.defaultView.exportToPNG(map_image, 500, 500)

    # Clean up
del aprx