import arcpy
import os
from getpass import getuser
import pandas as pd
import numpy as np

import linker # Latex and PDF report generator

arcpy.env.workspace = "memory"
arcpy.env.overwriteOutput = True


class Toolbox(object):
    def __init__(self):
        self.label = "draw region"
        self.alias = "draw region"
        self.tools = [regionData]

class regionData(object):
    def __init__(self):
        self.label = "region data0"
        self.description = "get the region with user-input polygons"
        self.canRunInBackground = False

    def getParameterInfo(self):
        # Define interactive polygon parameter
        feature_set = arcpy.Parameter(
            displayName="Selected region",
            name="in_feature_set",
            datatype="GPFeatureRecordSetLayer",
            parameterType="Required",
            direction="Input")

        # Define property name through user input
        property_name = arcpy.Parameter(
            displayName="Property Name to be displayed on report",
            name="property_name",
            datatype="String",
            parameterType="Required",
            direction="Input")

        # Define user-specified output directory
        output_location = arcpy.Parameter(
            name="output_pdf",
            displayName="Output PDF File Location",
            datatype="DEFolder",
            parameterType="Required",
            direction="Input"
        )

        return [feature_set, property_name, output_location]

    def isLicensed(self):
        return True

    def updateParameters(self, params):
        return

    def updateMessages(self, params):
        return

    def execute(self, params, messages):
        input_lyr = params[0]
        property_name = params[1]
        arcpy.AddMessage(f'You are generating report for {property_name.valueAsText}...')
        output_pdf_path = params[2].valueAsText

        testing = True

        # Hardcode for testing purposes
        if testing:
            # arcpy.AddMessage("ENTERRRRRRRRRRRRRRRR")
            input_lyr = r"C:\\Users\\hyu\\Desktop\\GIS_projects\\FIND_updates_2023.gdb\\test1"
            property_name = "trytry2"
            output_pdf_path = "C:/Users/hyu/Desktop/"

        # Survey Site dataframe, address and variables are hardcoded
        survey_addr = r"C:\Users\hyu\Desktop\GIS_projects\FIND_updates_2023.gdb"
        survey_poly_addr = r"C:\Users\hyu\Desktop\GIS_projects\FIND_updates_2023.gdb\survey_poly"
        survey_poly_vars = ['refcode', 'dm_stat', 'survey_start', 'survey_sit', 'site_desc', 'site_comm', 'land_use_in_site',
                            'land_use_surr_site', 'threats']
        sample_df = pd.DataFrame(data=arcpy.da.SearchCursor(survey_poly_addr, survey_poly_vars),
                                      columns=survey_poly_vars)

        # Make feature layer for survey_poly
        arcpy.MakeFeatureLayer_management(survey_poly_addr, "survey_sites_lyr")

        # Make feature layer for input feature parameter
        if testing:
            arcpy.management.MakeFeatureLayer(input_lyr, "OutputFeatureLayer")
        else:
            arcpy.management.MakeFeatureLayer(input_lyr.valueAsText, "OutputFeatureLayer")

        new_lyr = arcpy.management.SelectLayerByLocation(in_layer = "survey_sites_lyr",
                                                         overlap_type = "INTERSECT",
                                                         select_features = "OutputFeatureLayer")

        # Make result survey_sites dataframe
        survey_sites_df = pd.DataFrame(data=arcpy.da.SearchCursor(new_lyr, survey_poly_vars),
                                       columns=survey_poly_vars)
        survey_sites_df.columns = survey_poly_vars

        # Get refcode list
        refcode_list = (survey_sites_df["refcode"]).tolist()

        el_pt = survey_addr + "\el_pt"
        el_line = survey_addr + "\el_line"
        el_poly = survey_addr + "\el_poly"
        comm_pt = survey_addr + "\comm_pt"
        comm_poly = survey_addr + "\comm_poly"

        # Make {el_pt, el_line, el_poly, comm_pt, comm_poly} dataframe on refcode
        el_and_comms = pd.DataFrame()
        for layer in [el_pt, el_line, el_poly, comm_pt, comm_poly]:
            curr_layer = arcpy.management.SelectLayerByAttribute(
                in_layer_or_view=layer,
                selection_type="SUBSET_SELECTION",
                where_clause="\"refcode\" IN {}".format(tuple(refcode_list))
            )
            if layer in [el_pt, el_line, el_poly]:
                curr_fields = ['refcode', 'elem_name', 'elem_found', 'elem_found_comm', 'invasive_present', 'pmash_comm',
                               'eo_size', 'eo_landsc', 'eo_rank', 'eo_rank_comm', 'mgmt_needs', 'protect_needs',
                               'pmash_condition', 'disturb'] # last two are EO_conditions
            else:
                curr_fields = [field.name for field in arcpy.ListFields(layer)]
            curr_df = pd.DataFrame(data=arcpy.da.SearchCursor(curr_layer, curr_fields),
                                   columns=curr_fields)
            # Merge curr_df with survey_sites_df
            el_and_comms = pd.concat([el_and_comms, curr_df])

        # Get species information from Biotics database ET table
        biotics_path = "C:/Users/hyu/Desktop/GIS_projects/Biotics_datasets.gdb"
        table_name = "ET"
        table_path = arcpy.Describe(f"{biotics_path}/{table_name}").catalogPath
        ET_arr = arcpy.da.TableToNumPyArray(table_path, ['ELSUBID', 'SPROT'])
        speciesET_df = pd.DataFrame(ET_arr)
        # Change ELSUBID to elem_name
        speciesET_df.columns = ['elem_name', 'SPROT']
        # Merge speciedET_df and el_and_comms based on elem_name(or ELSUBID)
        speciesET_df['elem_name'] = speciesET_df['elem_name'].astype('int32')
        el_and_comms['elem_name'] = el_and_comms['elem_name'].astype('int32')

        species_info_df = pd.merge(speciesET_df, el_and_comms, on="elem_name")


        # Generate LaTeX and PDF report
        if testing:
            linker.produce_report(survey_sites_df,
                                  el_and_comms,
                                  property_name,
                                  output_pdf_path,
                                  species_info_df)
        else:
            linker.produce_report(survey_sites=survey_sites_df,
                                  el_and_comms=el_and_comms,
                                  property_name=property_name.valueAsText,
                                  output_path=output_pdf_path,
                                  species_info_df=species_info_df)
