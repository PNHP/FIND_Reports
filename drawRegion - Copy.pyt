import arcpy
import os
from getpass import getuser
import pandas as pd
import numpy as np
import subprocess

from pylatex import Document, Section, Subsection, Tabular, Math, TikZ, Axis, \
    Plot, Figure, Matrix, Alignat, MediumText, LineBreak, Head, MiniPage, NoEscape, \
    LargeText, PageStyle, Command, Itemize, NewPage
from pylatex.utils import bold, italic

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

        testing = False

        # Hardcode for testing purposes
        if testing:
            input_lyr = r"C:\\Users\\hyu\\Desktop\\GIS_projects\\FIND_updates_2023.gdb\\test2"
            property_name = "Local Test"
            output_pdf_path = "C:/Users/hyu/Desktop"

        # Survey Site dataframe, address and variables are hardcoded
        survey_addr = r"C:\Users\hyu\Desktop\GIS_projects\FIND_updates_2023.gdb"
        survey_poly_addr = r"C:\Users\hyu\Desktop\GIS_projects\FIND_updates_2023.gdb\survey_poly"
        survey_poly_vars = ['refcode', 'dm_stat', 'survey_start', 'survey_end', 'surveyors', 'survey_sit', 'site_desc',
                            'site_comm', 'survey_typ', 'survey_typ_comm', 'land_use_in_site','land_use_surr_site',
                            'threats', 'drive_direc']
        sample_df = pd.DataFrame(data=arcpy.da.SearchCursor(survey_poly_addr, survey_poly_vars),
                                 columns=survey_poly_vars)

        # Make feature layer for survey_poly
        arcpy.MakeFeatureLayer_management(survey_poly_addr, "survey_sites_lyr")

        # Make feature layer for input feature parameter
        if testing:
            arcpy.management.MakeFeatureLayer(input_lyr, "OutputFeatureLayer")
        else:
            arcpy.management.MakeFeatureLayer(input_lyr.valueAsText, "OutputFeatureLayer")

        new_lyr = arcpy.management.SelectLayerByLocation(in_layer="survey_sites_lyr",
                                                         overlap_type="INTERSECT",
                                                         select_features="OutputFeatureLayer")

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
            refcode_str = ', '.join(f"'{code}'" for code in refcode_list)
            where_clause = f"\"refcode\" IN ({refcode_str})"
            curr_layer = arcpy.management.SelectLayerByAttribute(
                in_layer_or_view=layer,
                selection_type="SUBSET_SELECTION",
                # where_clause="\"refcode\" IN {}".format(tuple(map(str, refcode_list)))
                where_clause=where_clause

            )
            if layer in [el_pt, el_line, el_poly]:
                curr_fields = ['refcode', 'elem_name', 'elem_found', 'elem_found_comm', 'invasive_present',
                               'pmash_comm',
                               'eo_size', 'eo_landsc', 'eo_rank', 'eo_rank_comm', 'mgmt_needs', 'protect_needs',
                               'pmash_condition', 'disturb', 'direc_elem']  # last two are EO_conditions
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
        ET_arr = arcpy.da.TableToNumPyArray(table_path, ['ELSUBID', 'SPROT', 'SNAME', 'SCOMNAME'])
        speciesET_df = pd.DataFrame(ET_arr)
        # Change ELSUBID to elem_name
        speciesET_df.columns = ['elem_name', 'SPROT', 'SNAME', 'SCOMNAME']
        # Merge speciedET_df and el_and_comms based on elem_name(or ELSUBID)
        speciesET_df['elem_name'] = speciesET_df['elem_name'].astype('int32')
        el_and_comms['elem_name'] = el_and_comms['elem_name'].astype('int32')

        species_info_df = pd.merge(speciesET_df, el_and_comms, on="elem_name")
        # Delete duplicates with same refcode and same elem_name
        species_info_df = species_info_df.drop_duplicates(subset=['refcode', 'elem_name'])
        # Map SPROT column to its real meaning in English
        def map_SPROT(sprot):
            if sprot == "PE":
                return "Endangered"
            elif sprot == "PT":
                return "Threatened"
            elif sprot == "PR":
                return "Rare"
            elif sprot == "PX":
                return "Extirpated"
            elif sprot == "PV":
                return "Vulnerable"
            elif sprot == "TU":
                return "Undetermined"
            else:
                return sprot
        species_info_df["SPROT"] = species_info_df["SPROT"].map(map_SPROT)

        # Species List
        FIND_path = "C:/Users/hyu/Desktop/GIS_projects/FIND_updates_2023.gdb"
        table_name = "SpeciesList"
        table_path = arcpy.Describe(f"{FIND_path}/{table_name}").catalogPath
        all_species_arr = arcpy.da.TableToNumPyArray(table_path, ['elem_name', 'refcode'])
        all_species_df = pd.DataFrame(all_species_arr)
        # print(refcode_list)
        # l = all_species_df['refcode'].tolist()
        # print(set(refcode_list).intersection(set(l)))
        # print(sorted(list((set(l)))))
        all_species_df = all_species_df[all_species_df['refcode'].isin(refcode_list)]
        all_species_df['elem_name'] = all_species_df['elem_name'].astype('int32')
        all_species_df = pd.merge(all_species_df, speciesET_df, on="elem_name")
        # Delete duplicates with same refcode and same elem_name
        all_species_df = all_species_df.drop_duplicates(subset=['refcode', 'elem_name'])


        # Generate LaTeX and PDF report
        if not testing:
            property_name = property_name.valueAsText
        geometry_options = {"margin": "0.5in"}
        doc = Document(geometry_options=geometry_options) # default page size is US letter

        # Create title
        with doc.create(Section(f'{property_name}', numbering=False)):
            doc.append(f'There are {survey_sites_df.shape[0]} survey sites in the area you requested.\n')

            # Create subsections for survey site descriptions and findings
            for i in range(survey_sites_df.shape[0]):
                # Newpage for every survey site in the area
                if i > 0:
                    doc.append(NewPage())
                curr_site = survey_sites_df.iloc[i]
                site_name = curr_site["survey_sit"]
                site_description = curr_site["site_desc"]

                with doc.create(Section(site_name)) as site:
                    # Survey date: start - end
                    site.append(bold('Survey date: '))
                    site.append(f'{curr_site["survey_start"]} - {curr_site["survey_end"]} \n')
                    # Surveyors of current survey site
                    site.append(bold('Surveyors: '))
                    site.append(f'{curr_site["surveyors"]} \n')

                    site.append(LineBreak())

                    # Survey site raw description (directly drawn from FIND)
                    site.append(bold("Site Description: \n"))
                    site.append(f'{site_description} \n')

                    site.append(LineBreak())

                    # Survey site driving direction (drawn from FIND)
                    site.append(bold("Driving direction: \n"))
                    site.append(f'{curr_site["drive_direc"]} \n')

                    site.append(LineBreak())
                    # Survey site findings
                    site.append(bold("Findings: \n"))
                    if curr_site["survey_typ"] != None:
                        if curr_site["survey_typ"] == "QUAL":
                            site.append("This is a qualitative survey.\n")
                        else:
                            site.append("This is a quantitative survey.\n")
                    if curr_site["survey_typ_comm"] != None:
                        site.append(f'Survey type comments: {curr_site["survey_typ_comm"]} \n')

                    site.append(LineBreak())

                    # Make a table for species info at this survey site
                    # 1. get the species of the same refcode
                    curr_refcode = curr_site["refcode"]
                    site_species_df = species_info_df[species_info_df["refcode"] == curr_refcode]
                    # 2. get all found elements in the area
                    site_found_df = site_species_df[site_species_df["elem_found"] == "Y"]
                    # 3. get all not_founded elements in the area
                    site_unfound_df = site_species_df[site_species_df["elem_found"] == "N"]

                    if site_found_df.shape[0] == 0 and site_unfound_df.shape[0] == 0:
                        site.append("Our record shows that there are no elements in the area you requested.\n")
                    else:
                        # Fix the width for each column in the findings table
                        table_spec = "p{3cm}" + "p{4cm}" + "p{2cm}" + "p{3cm}" + "p{5cm}"
                        if site_found_df.shape[0] == 0:
                            site.append("Table of unfounded elements in the area you requested:\n")
                            site.append(LineBreak())
                            with site.create(Tabular(table_spec)) as table:
                                table.add_hline()
                                table.add_row((Command('textbf', 'Common name'),
                                               Command('textbf', 'Latin name'),
                                               Command('textbf', 'Population rank *'),
                                               Command('textbf', 'State status'),
                                               Command('textbf', 'Where found')))
                                for j in range(site_unfound_df.shape[0]):
                                    curr_row = site_unfound_df.iloc[j][['SCOMNAME', 'SNAME', 'eo_rank', 'SPROT', 'direc_elem']]
                                    table.add_hline()
                                    table.add_row(tuple(curr_row))
                                table.add_hline()
                            site.append(LineBreak())
                        elif site_unfound_df.shape[0] == 0:
                            site.append("Table of found elements in the area you requested:\n")
                            site.append(LineBreak())
                            with site.create(Tabular(table_spec)) as table:
                                table.add_hline()
                                table.add_row((Command('textbf', 'Common name'),
                                               Command('textbf', 'Latin name'),
                                               Command('textbf', 'Population rank *'),
                                               Command('textbf', 'State status'),
                                               Command('textbf', 'Where found')))
                                for j in range(site_found_df.shape[0]):
                                    curr_row = site_found_df.iloc[j][['SCOMNAME', 'SNAME', 'eo_rank', 'SPROT', 'direc_elem']]
                                    table.add_hline()
                                    table.add_row(tuple(curr_row))
                                table.add_hline()
                            site.append(LineBreak())
                        else:
                            site.append("Table of found elements in the area you requested:\n")
                            site.append(LineBreak())
                            with site.create(Tabular(table_spec)) as table:
                                table.add_hline()
                                table.add_row((Command('textbf', 'Common name'),
                                               Command('textbf', 'Latin name'),
                                               Command('textbf', 'Population rank *'),
                                               Command('textbf', 'State status'),
                                               Command('textbf', 'Where found')))
                                for j in range(site_found_df.shape[0]):
                                    curr_row = site_found_df.iloc[j][['SCOMNAME', 'SNAME', 'eo_rank', 'SPROT', 'direc_elem']]
                                    table.add_hline()
                                    table.add_row(tuple(curr_row))
                                table.add_hline()
                            site.append(LineBreak())
                            site.append("\n")
                            site.append("Table of unfounded elements in the area you requested:\n")
                            site.append(LineBreak())
                            with site.create(Tabular(table_spec)) as table:
                                table.add_hline()
                                table.add_row((Command('textbf', 'Common name'),
                                               Command('textbf', 'Latin name'),
                                               Command('textbf', 'Population rank *'),
                                               Command('textbf', 'State status'),
                                               Command('textbf', 'Where found')))
                                for j in range(site_unfound_df.shape[0]):
                                    curr_row = site_unfound_df.iloc[j][['SCOMNAME', 'SNAME', 'eo_rank', 'SPROT', 'direc_elem']]
                                    table.add_hline()
                                    table.add_row(tuple(curr_row))
                                table.add_hline()
                            site.append(LineBreak())

                    site.append(LineBreak())
                    site.append("\n")

                    # Survey site threat and management recommendations
                    site.append(bold("Threats and management recommendations: \n"))
                    site.append(f'{curr_site["threats"]} \n')

                    site.append(LineBreak())

                    # Survey site species list
                    site.append(bold("Species list: \n"))
                    site_all_species_df = all_species_df[all_species_df["refcode"] == curr_refcode]
                    all_species_str = ""
                    for k in range(site_all_species_df.shape[0]):
                        if k % 3 == 0 and k > 0:
                            all_species_str += "\n"
                        curr_species = site_all_species_df.iloc[k]
                        if curr_species["SCOMNAME"] == "None" and curr_species["SNAME"] == "None":
                            continue
                        elif curr_species["SCOMNAME"] == "None":
                            all_species_str += f'{curr_species["SNAME"]}, '
                        elif curr_species["SNAME"] == "None":
                            all_species_str += f'{curr_species["SCOMNAME"]}, '
                        else:
                            all_species_str += f'{curr_species["SCOMNAME"]}({curr_species["SNAME"]}), '
                    all_species_str = all_species_str[:(len(all_species_str)-2)]
                    site.append(all_species_str)



        doc.generate_tex(filepath=f'{output_pdf_path}' + '/' + f'{property_name}_report')

        # Specify the path to the LaTeX file
        latex_file = f'{output_pdf_path}' + '/' + f'{property_name}_report.tex'
        arcpy.AddMessage(f"LaTeX file is generated here: {latex_file}")

        # Specify the path to the output PDF file
        pdf_file = f'{output_pdf_path}'
        arcpy.AddMessage(f"PDF file is generated here: {pdf_file}")

        # Execute the LaTeX compiler command and move PDF report to user-specified directory
        subprocess.run(['pdflatex', '-output-directory=' + pdf_file, latex_file])
