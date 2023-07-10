import arcpy
import os
from getpass import getuser
import pandas as pd
import numpy as np
import subprocess
import string
from datetime import datetime

from pylatex import Document, Section, Subsection, Tabular, Math, TikZ, Axis, \
    Plot, Figure, Matrix, Alignat, MediumText, LineBreak, Head, MiniPage, NoEscape, \
    LargeText, PageStyle, Command, Itemize, NewPage, SubFigure
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
            input_lyr = r"C:\\Users\\hyu\\Desktop\\GIS_projects\\FIND_updates_2023.gdb\\test5"
            property_name = "Local Test"
            output_pdf_path = "C:/Users/hyu/Desktop/pics"

        # Survey Site dataframe, address and variables are hardcoded
        FIND_path = r"C:\Users\hyu\Desktop\GIS_projects\FIND_updates_2023.gdb"
        survey_poly_addr = r"C:\Users\hyu\Desktop\GIS_projects\FIND_updates_2023.gdb\survey_poly"
        survey_poly_vars = [field.name for field in arcpy.ListFields(survey_poly_addr)]
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

        el_pt = FIND_path + "\el_pt"
        el_line = FIND_path + "\el_line"
        el_poly = FIND_path + "\el_poly"
        comm_pt = FIND_path + "\comm_pt"
        comm_poly = FIND_path + "\comm_poly"

        # Make {el_pt, el_line, el_poly, comm_pt, comm_poly} dataframe on refcode
        el_and_comms = pd.DataFrame(columns= [field.name for field in arcpy.ListFields(el_pt)])
        for layer in [el_pt, el_line, el_poly, comm_pt, comm_poly]:
            # refcode_str = ', '.join(f"'{code}'" for code in refcode_list)
            refcode_str = tuple(refcode_list)
            # where_clause = f"\"refcode\" IN ({refcode_str})"
            curr_refcodes = []
            with arcpy.da.SearchCursor(layer, ["refcode"]) as cursor:
                for row in cursor:
                    curr_refcodes.append(row[0])
            result_refcodes = set.intersection(set(refcode_list), set(curr_refcodes))
            arcpy.AddMessage(result_refcodes)
            if result_refcodes != set():
                if len(result_refcodes) == 1:
                    ref = list(result_refcodes)[0]
                    where_clause = "'refcode' = '{}'".format(ref)
                else:
                    where_clause = f"'refcode' IN {refcode_str}"
                curr_layer = arcpy.management.SelectLayerByAttribute(
                    in_layer_or_view=layer,
                    selection_type="SUBSET_SELECTION",
                    # where_clause="\"refcode\" IN {}".format(tuple(map(str, refcode_list)))
                    where_clause=where_clause)
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
        arcpy.AddMessage(el_and_comms.columns)
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
        all_species_df = all_species_df[all_species_df['refcode'].isin(refcode_list)]
        all_species_df['elem_name'] = all_species_df['elem_name'].astype('int32')
        all_species_df = pd.merge(all_species_df, speciesET_df, on="elem_name")
        # Delete duplicates with same refcode and same elem_name
        all_species_df = all_species_df.drop_duplicates(subset=['refcode', 'elem_name'])

        def importAttachments(output_path, inTable, curr_refcode):
            if not os.path.exists(output_path + "/" + curr_refcode):
                os.mkdir(output_path + "/" + curr_refcode)
            temp_folder = output_path + "/" + curr_refcode
            db_name = arcpy.Describe(inTable).baseName
            with arcpy.da.SearchCursor(inTable, ['DATA', 'ATT_NAME', 'CONTENT_TYPE', 'attach_name']) as cursor:
                # print([field.name for field in arcpy.ListFields(inTable)])
                counter = 0
                for item in cursor:
                    attachment = item[0]
                    att_name = item[1]
                    extend_name = (att_name.split("."))[-1]
                    real_att_name = item[3]
                    filename = real_att_name + "~" + str(counter) + f".{extend_name}"
                    filetype = item[2]
                    # print(filename, filetype)
                    if filetype == "image/jpeg":
                        open(temp_folder + os.sep + filename, 'wb').write(attachment.tobytes())
                    del item
                    del filename
                    del attachment
                    del filetype
                    counter += 1
            return os.listdir(temp_folder)  # return all the images for this site

        def deleteFolder(dirpath):
            for file in (os.listdir(dirpath)):
                os.remove(dirpath + os.sep + file)
            os.rmdir(dirpath)

        def addNameFieldAttachmentTable(feature_layer, inTableFieldName):
            # input 1: local path to feature class (survey_poly, el_pt, el_line, el_poly, comm_pt, comm_poly)
            # input 2: field names that represent attachment name, e.g. survey_sit, elem_name
            attachment_table = feature_layer + "__ATTACH"
            arcpy.management.AddField(attachment_table, "attach_name", "TEXT")
            with arcpy.da.UpdateCursor(attachment_table, ["REL_GLOBALID", "attach_name"]) as att_cursor:
                for att_row in att_cursor:
                    rel_guid = att_row[0]
                    with arcpy.da.SearchCursor(feature_layer, ["GlobalID", inTableFieldName]) as temp_cursor:
                        if rel_guid == temp_cursor[0]:
                            # insert attachment_name to attachment table if IDs match
                            if feature_layer == survey_poly_addr:
                                att_row[1] = "site~" + temp_cursor[1]
                            else:
                                att_row[1] = temp_cursor[1]
                            cursor.updateRow(row)

        # update attachment tables in advance, and use updated tables to perform SQL query in layer intersection
        for feature_layer in [survey_poly_addr, el_line, el_poly, comm_pt, comm_poly]:
            if feature_layer == survey_poly_addr:
                addNameFieldAttachmentTable(feature_layer, "survey_sit")
            else:
                addNameFieldAttachmentTable(feature_layer, "elem_name")

        # Delete name fields afterwards here


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
                curr_site = survey_sites_df.iloc[i]
                site_name = curr_site["survey_sit"]
                site_description = curr_site["site_desc"]
                curr_refcode = curr_site["refcode"]

                for n in range(len([survey_sites_df, el_and_comms])):
                    df = [survey_sites_df, el_and_comms][n]
                    info = df[df['refcode'] == curr_refcode]
                    globalIDs = (info['GlobalID']).tolist()
                    formatted_guids = ["'{}'".format(guid) for guid in globalIDs]
                    # print("formatted_guids:", formatted_guids)
                    # str_globalIDs = [format(guid) for guid in globalIDs]
                    if n == 0:
                        attachment_table = survey_poly_addr + "__ATTACH"

                        # Add a temporary field to hold the names for each site
                        arcpy.management.AddField(attachment_table, "attach_name", "TEXT")
                        with arcpy.da.UpdateCursor(attachment_table, ["REL_GLOBALID", "attach_name"]) as cursor:
                            for row in cursor:
                                rel_guid = row[0]
                                # print("rel_guid:", rel_guid)
                                # if str(rel_guid) in str_globalIDs:
                                if rel_guid in globalIDs:
                                    row[1] = "site~" + ((survey_sites_df[survey_sites_df['GlobalID'] == rel_guid])['survey_sit']).iloc[0]
                                    print("enter:\n", (row[1]))
                                    cursor.updateRow(row)

                        if formatted_guids:
                            sql_expression = "REL_GLOBALID IN ({})".format(",".join(formatted_guids))
                        else:
                            # Handle the case when formatted_guids is empty
                            sql_expression = "OBJECTID < 0"  # This will create a condition that is always false

                        # Create a new table view based on the SQL expression
                        arcpy.MakeTableView_management(attachment_table, "attachment_view", sql_expression)

                        # Save the view as a new table (subtable)
                        # result_path = os.path.join(FIND_path, "subtable.dbf")
                        arcpy.TableToTable_conversion("attachment_view", FIND_path, "subtable")

                    else:
                        for m in range(len([el_pt, el_line, el_poly, comm_pt, comm_poly])):
                            subdf = [el_pt, el_line, el_poly, comm_pt, comm_poly][m]
                            attachments_addr = subdf + "__ATTACH"
                            curr_att_table = attachments_addr

                            # Add a temporary field to hold the names for each site
                            arcpy.management.AddField(curr_att_table, "attach_name", "TEXT")
                            with arcpy.da.UpdateCursor(curr_att_table, ["REL_GLOBALID", "attach_name"]) as cursor:
                                for row in cursor:
                                    rel_guid = row[0]
                                    if rel_guid in globalIDs:
                                        row[1] = ((el_and_comms[el_and_comms['GlobalID'] == rel_guid])['elem_name']).iloc[0]
                                        cursor.updateRow(row)


                            if formatted_guids:
                                sql_expression = "REL_GLOBALID IN ({})".format(",".join(formatted_guids))
                            else:
                                # Handle the case when formatted_guids is empty
                                sql_expression = "ATTACHMENTID < 0"  # This will create a condition that is always false

                            # Create a new table view based on the SQL expression
                            arcpy.MakeTableView_management(curr_att_table, "temp"+str(m), sql_expression)

                            # Save the view as a new table (subtable)
                            arcpy.TableToTable_conversion("temp"+str(m), FIND_path, f"temp{m}")

                            # Append current table to the big attachment table
                            arcpy.Append_management(os.path.join(FIND_path, f"temp{m}"),
                                                    os.path.join(FIND_path, "subtable"), "NO_TEST")

                            # Delete current table
                            arcpy.management.Delete(os.path.join(FIND_path, f"temp{m}"))


                    # import attachments of the attachments related to curr_refcode
                curr_attachments = importAttachments(output_pdf_path, os.path.join(FIND_path, "subtable"), curr_refcode)
                arcpy.management.Delete(os.path.join(FIND_path, "subtable"))

                if i > 0:
                    doc.append(NewPage())

                if site_name is None:
                    site_name = f"Unidentified Site: ({curr_site['X']}, {curr_site['Y']}) (WGS84)"
                with doc.create(Section(site_name)) as site:
                    # Survey date: start - end
                    if curr_site["survey_start"] is not None and not pd.isnull(curr_site["survey_start"]):
                        site.append(bold('Survey date: '))
                        reformat_start = (curr_site["survey_start"]).strftime("%m/%d/%Y")
                        if (curr_site["survey_end"] is None or pd.isnull(curr_site["survey_end"])) and (curr_site["survey_start"] is not None and not pd.isnull(curr_site["survey_start"])):
                            site.append(f'{reformat_start} \n')
                        else:
                            reformat_end = (curr_site["survey_end"]).strftime("%m/%d/%Y")
                            site.append(f'{reformat_start} - {reformat_end} \n')
                    # Surveyors of current survey site
                    site.append(bold('Surveyors: '))
                    site.append(f'{curr_site["surveyors"]} \n')

                    site.append(LineBreak())

                    # Survey site raw description (directly drawn from FIND)
                    site.append(bold("Site description: \n"))
                    site.append(f'{site_description} \n')

                    site.append(LineBreak())

                    # Survey site driving direction (drawn from FIND)
                    if curr_site["drive_direc"] is not None:
                        site.append(bold("Driving directions: \n"))
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
                    site_species_df = species_info_df[species_info_df["refcode"] == curr_refcode]
                    # 2. get all found elements in the area
                    site_found_df = site_species_df[site_species_df["elem_found"] == "Y"]
                    # 3. get all not_founded elements in the area
                    site_unfound_df = site_species_df[site_species_df["elem_found"] == "N"]

                    if site_found_df.shape[0] == 0 and site_unfound_df.shape[0] == 0:
                        site.append("No tracked elements were found during this survey.\n")
                    else:
                        # Fix the width for each column in the findings table
                        table_spec = "p{3cm}" + "p{4cm}" + "p{2cm}" + "p{3cm}" + "p{5cm}"
                        if site_found_df.shape[0] == 0:
                            site.append("Elements that were NOT found during the survey: \n")
                            site.append(LineBreak())
                            with site.create(Tabular(table_spec)) as table:
                                table.add_hline()
                                table.add_row((Command('textbf', 'Common name'),
                                               Command('textbf', 'Scientific name'),
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
                            site.append("Elements that were found during the survey: \n")
                            site.append(LineBreak())
                            with site.create(Tabular(table_spec)) as table:
                                table.add_hline()
                                table.add_row((Command('textbf', 'Common name'),
                                               Command('textbf', 'Scientific name'),
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
                            site.append("Elements that were found during the survey: \n")
                            site.append(LineBreak())
                            with site.create(Tabular(table_spec)) as table:
                                table.add_hline()
                                table.add_row((Command('textbf', 'Common name'),
                                               Command('textbf', 'Scientific name'),
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
                            site.append("\n")
                            site.append("Elements that were NOT found during the survey:\n")
                            site.append(LineBreak())
                            with site.create(Tabular(table_spec)) as table:
                                table.add_hline()
                                table.add_row((Command('textbf', 'Common name'),
                                               Command('textbf', 'Scientific name'),
                                               Command('textbf', 'Population rank *'),
                                               Command('textbf', 'State status'),
                                               Command('textbf', 'Where found')))
                                for j in range(site_unfound_df.shape[0]):
                                    curr_row = site_unfound_df.iloc[j][['SCOMNAME', 'SNAME', 'eo_rank', 'SPROT', 'direc_elem']]
                                    table.add_hline()
                                    table.add_row(tuple(curr_row))
                                table.add_hline()
                            site.append(LineBreak())
                        site.append("*Populations are ranked using Nature Serve methods. Possible ranks are A=excellent viability; B=good viability; C=fair viability, E=extant, or present on site but not given a viability rank, and F=failed to find. Combination ranks span two categories. For instance, BC indicates “good to fair” viability.\n")

                    # site.append(LineBreak())
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
                            all_species_str += f'{curr_species["SCOMNAME"]} ({curr_species["SNAME"]}), '
                    all_species_str = all_species_str[:(len(all_species_str)-2)]
                    if all_species_str == "":
                        all_species_str = "A species list was not recorded for this survey."
                    all_species_str += "\n"
                    site.append(all_species_str)

                    # write the attachments to the report
                    if len(curr_attachments) > 0:
                        doc.append(NewPage())
                        # site.append("\n")
                        site.append(bold("Attachments: \n"))
                        # Number of rows and columns
                        num_rows = len(curr_attachments) // 3
                        num_cols = [3] * num_rows + [len(curr_attachments) - 3*num_rows]

                        for row in range(num_rows+1):
                            # Create a single imagesRow
                            with site.create(Figure(position='h!')) as imagesRow:
                                # Create a subfigure for each image
                                for col in range(num_cols[row]):
                                    # print("row, col: ", row, col)
                                    with imagesRow.create(
                                            SubFigure(position='c', width=NoEscape(r'0.33\linewidth'))) as subfig:
                                        # Add the image to the subfigure
                                        curr_dir = os.path.join(output_pdf_path, curr_refcode)
                                        img_addr = os.path.join(curr_dir, curr_attachments[row*3 + col])
                                        subfig.add_image(img_addr, width=NoEscape(r'0.95\linewidth'))
                                        # Add caption for each attachment in the survey site
                                        att_name_parts = (curr_attachments[row*3 + col]).split("~")
                                        if att_name_parts[0] == "site":
                                            # Indicate this is an attachment for survey site
                                            curr_att_name = att_name_parts[1]
                                        else:
                                            # Indicate this is an attachment for an element
                                            curr_SNAME = ((speciesET_df[speciesET_df['elem_name'] == int(att_name_parts[0])])['SNAME']).iloc[0]
                                            curr_SCOMNAME = ((speciesET_df[speciesET_df['elem_name'] == int(att_name_parts[0])])['SCOMNAME']).iloc[0]
                                            if curr_SNAME is None or curr_SNAME == "None":
                                                curr_att_name = curr_SCOMNAME
                                            elif curr_SCOMNAME is None or curr_SCOMNAME == "None":
                                                curr_att_name = curr_SNAME
                                            else:
                                                curr_att_name = f'{curr_SCOMNAME} ({curr_SNAME})'
                                        print(f'From {att_name_parts}, the name of this attachment is {curr_att_name}')
                                        subfig.add_caption('{}'.format(curr_att_name))

                    # Delete subtable for curr_refcode
                    arcpy.management.Delete(os.path.join(FIND_path, "subtable"))

        doc.generate_tex(filepath=f'{output_pdf_path}' + '/' + f'{property_name}_report')

        # Specify the path to the LaTeX file
        latex_file = f'{output_pdf_path}' + '/' + f'{property_name}_report.tex'
        arcpy.AddMessage(f"LaTeX file is generated here: {latex_file}")

        # Specify the path to the output PDF file
        pdf_file = f'{output_pdf_path}'
        arcpy.AddMessage(f"PDF file is generated here: {pdf_file}")

        # Execute the LaTeX compiler command and move PDF report to user-specified directory
        subprocess.run(['pdflatex', '-output-directory=' + pdf_file, latex_file])

        # Delete temporary folders
        for i in range(survey_sites_df.shape[0]):
            curr_site = survey_sites_df.iloc[i]
            curr_refcode = curr_site["refcode"]
            deleteFolder(os.path.join(output_pdf_path, curr_refcode))

        ATTACH_tables = [survey_poly_addr+"__ATTACH", el_pt+"__ATTACH", el_line+"__ATTACH",
                         el_poly+"__ATTACH", comm_pt+"__ATTACH", comm_poly+"__ATTACH"]
        for table in ATTACH_tables:
            arcpy.management.DeleteField(table, ["attach_name"])