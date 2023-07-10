from pylatex import Document, Section, Subsection, Tabular, Math, TikZ, Axis, \
    Plot, Figure, Matrix, Alignat, MediumText, LineBreak, Head, MiniPage, NoEscape, \
    LargeText
from pylatex.utils import bold, italic

# Helper functions

# def template(survey_sites_df, el_and_comms, property_name, species_info_df):
#     # Initialize report page
#     geometry_options = {"tmargin": "1cm", "lmargin": "1cm"}
#     doc = Document(geometry_options=geometry_options)
#
#     # Create title: bold{property}
#     with doc.create(Head("L")) as left_header:
#         with left_header.create(MiniPage(width=NoEscape(r"0.49\textwidth"),
#                                         pos='c', align='l')) as title_wrapper:
#             title_wrapper.append(LargeText(bold("Bank Account Statement")))
#             title_wrapper.append(LineBreak())
#
#     doc.append('Here is the survey sites report that you requested:\n')
#     doc.append('There are survey sites in total in the area you requested.\n')
#
#     # Scratch: make a table for species info at this survey site
#     # 1. get the species of the same refcode
#     curr_refcode = curr_site["refcode"]
#     site_species_df = species_info_df[species_info_df["refcode"] == curr_refcode]
#     # 2. get all found elements in the area
#     site_found_df = site_species_df[site_species_df["elem_found"] == "Y"]
#     # SNAME, SCOMNAME, eo_rank, SPROT
#     table_spec = "c|"*4
#     site.append("Table of found elements in the area you requested:\n")
#     with site.create(Tabular(table_spec)) as table:
#         table.add_row(('SNAME','SCOMNAME','eo_rank','SPROT'))
#         for i in range(site_found_df.shape[0]):
#             curr_row = site_found_df.loc[i, ['SNAME', 'SCOMNAME', 'eo_rank', 'SPROT']]
#             table.add_hline()
#             table.add_row(tuple(curr_row))
#     # 3. get all not_founded elements in the area
#     site.append("Table of unfounded elements in the area you requested:\n")
#     site_unfound_df = site_species_df[site_species_df["elem_found"] == "N"]
#     with site.create(Tabular(table_spec)) as table:
#         table.add_row(('SNAME', 'SCOMNAME', 'eo_rank', 'SPROT'))
#         for i in range(site_unfound_df.shape[0]):
#             curr_row = site_unfound_df.loc[i, ['SNAME', 'SCOMNAME', 'eo_rank', 'SPROT']]
#             table.add_hline()
#             table.add_row(tuple(curr_row))
#
#
#
#
#
#     doc.append(LineBreak())
#     return doc


# from pylatex import Document
# from pylatex import Package
# from pylatex import Tabu
# import subprocess
# from pylatex import Document, Tabular, NewPage, Section
#
#
# # Create a new document
# doc = Document()
#
# # Create a table with a center-aligned and fixed width column
# table = Tabular('|p{5cm}|c|')
# table.add_hline()
# table.add_row(('Center Aligned', 'Column 2'))
# table.add_hline()
#
# # Add content to the center-aligned column
# content = 'This is a long text that should be center-aligned and have a fixed width of 5cm.'
# table.add_row((content, 'Value'))
#
# # Add the table to the document
# doc.append(table)
#
# doc.append(NewPage())
# doc.append("It's me, hi, i'm the problem it's me! :)")
#
# # Append long text
# long_text = """
# This is a long paragraph that will automatically wrap around based on the page width and formatting settings in PyLaTeX.
# You don't need to specify any special settings for text wrapping. PyLaTeX handles it automatically.
# """
# doc.append(long_text)
#
#
# output_pdf_path = "C:/Users/hyu/Desktop"
# property_name = "hi"
#
# doc.generate_tex(filepath=f'{output_pdf_path}' + '/' + f'{property_name}_report')
#
# # Specify the path to the LaTeX file
# latex_file = f'{output_pdf_path}' + '/' + f'{property_name}_report.tex'
#
# # Specify the path to the output PDF file
# pdf_file = f'{output_pdf_path}'
#
# # Execute the LaTeX compiler command and move PDF report to user-specified directory
# subprocess.run(['pdflatex', '-output-directory=' + pdf_file, latex_file])

# import os
# import arcpy
# import pandas as pd
#
# # path = "C:/Users/hyu/Desktop/mydir/dir1"
# # # os.mkdir(path)
# #
# # for file in (os.listdir(path)):
# #     os.remove(path+"/"+file)
# # os.rmdir(path)
#
#
# def tableToDataframe(gdb_path, table_name):
#     table_path = arcpy.Describe(f"{gdb_path}/{table_name}").catalogPath
#     fields = [field.name for field in arcpy.ListFields(table_path)]
#     arr = arcpy.da.TableToNumPyArray(table_path, fields)
#     df = pd.DataFrame(arr)
#     return df
#
# ###
# # current data frames:
# # 1. el_and_comms: Make {el_pt, el_line, el_poly, comm_pt, comm_poly} dataframe concat on refcode
# # 2. species_info_df: species names and locations (el_and_comms & ET)
#
# # Assume we have the refcode of current site: curr_refcode
# for df in [survey_sites_df, el_and_comms]:
#     info = df[df['refcode'] == curr_refcode]
#     globalIDs = info['GlobalID']
#     if (df == survey_sites_df):
#         attachments_addr = survey_poly_addr + "__ATTACH"
#         # find info in attachment database based on globalID
#         attachment_info = tableToDataframe(FIND_path, "survey_poly__ATTACH")
#         attachment_info = attachment_info[attachments_info['rel_GlobalID'].isin(globalIDs.tolist())]
#
#
#
#
#         # create table to hold attachment_info in gdb path
#         arcpy.da.NumPyArrayToTable(attachment_info.to_numpy(), os.path.join(FIND_path, "temp"))
#         # # import attachments of the filtered data frame
#         # importAttachments(output_pdf_path, os.path.join(FIND_path, "temp"), curr_refcode)
#     else:
#         names = ["el_pt", "el_line", "el_poly", "comm_pt", "comm_poly"]
#         for i in range(len([el_pt, el_line, el_poly, comm_pt, comm_poly])):
#             subdf = [el_pt, el_line, el_poly, comm_pt, comm_poly][i]
#             attachments_addr = subdf + "__ATTACH"
#             # find info in attachment database based on globalID
#             attachment_info = tableToDataframe(FIND_path, names[i])
#             attachment_info = attachment_info[attachments_info['rel_GlobalID'].isin(globalIDs.tolist())]
#             # create table to hold attachment_info in gdb path
#             arcpy.da.NumPyArrayToTable(attachment_info.to_numpy(), os.path.join(FIND_path, "temp"+str(i)))
#             # concatenate this table with previous concatenated table
#             arcpy.management.Append(os.path.join(FIND_path, "temp"+str(i)), os.path.join(FIND_path, "temp"))
#             # delete this table
#             arcpy.management.Delete(os.path.join(FIND_path, "temp"+str(i)))
#
#             # # import attachments of the filtered data frame
#             # importAttachments(output_pdf_path, os.path.join(FIND_path, "temp"), curr_refcode)
#
#     # import attachments of the filtered data frame
#     # check the type of attachments?
#     curr_attachments = importAttachments(output_pdf_path, os.path.join(FIND_path, "temp"), curr_refcode)
#
#
#     # write the attachments to the report
#     doc.append(NewPage())
#     # Number of rows and columns
#     num_rows = curr_attachments // 3 + 1
#     num_cols = 3
#     for row in range(num_rows):
#         # Create a single imagesRow
#         with doc.create(Figure(position='h!')) as imagesRow:
#             # Create a subfigure for each image
#             for col in range(1, num_cols + 1):
#                 with imagesRow.create(SubFigure(position='c', width=NoEscape(r'0.33\linewidth'))) as subfig:
#                     # Add the image to the subfigure
#                     subfig.add_image(curr_attachments[row][col], width=NoEscape(r'0.95\linewidth'))
#
#     # delete temporary saved folder and temp table
#     deleteFolder(os.path.join(output_pdf_path, curr_refcode))
#     arcpy.management.Delete(os.path.join(FIND_path, "temp"))
#
#
#
#
# def importAttachments(output_path, inTable, curr_refcode):
#     temp_folder = os.mkdir(output_path, curr_refcode)
#     with arcpy.da.SearchCursor(inTable, ['DATA', 'ATT_NAME', 'ATTACHMENTID', 'CONTENT_TYPE']) as cursor:
#         for item in cursor:
#             attachment = item[0]
#             filenum = "ATT" + str(item[2]) + "_"
#             filename = filenum + str(item[1])
#             filetype = item[3]
#             if filetype == "image/jpeg":
#                 open(temp_folder + os.sep + filename, 'wb').write(attachment.tobytes())
#             del item
#             del filenum
#             del filename
#             del attachment
#             del filetype
#     return os.listdir(temp_folder) # return all the images for this site
#
# def deleteFolder(dirpath):
#     for file in (os.listdir(dirpath)):
#         os.remove(dirpath + os.sep + file)
#     os.rmdir(dirpath)
