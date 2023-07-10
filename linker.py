import os
import numpy as np
# from pylatex import Document, Section, Subsection, Tabular, Math, TikZ, Axis, \
#     Plot, Figure, Matrix, Alignat, MediumText, LineBreak
# from pylatex.utils import italic, bold
# import subprocess
# import arcpy
# import report_template
#
# # Examples of pylatex: https://jeltef.github.io/PyLaTeX/current/examples.html
# # Note: Remember to close the pdf file that you generated before running the program to edit/overwrite it!
#
#
# def produce_report(survey_sites,
#                    el_and_comms,
#                    property_name,
#                    output_path,
#                    species_info_df):
#     survey_sites_row_num = survey_sites.shape[0]
#     survey_sites_col_num = 4
#     el_and_comms_row_num = el_and_comms.shape[0]
#     el_and_comms_col_num = 4
#
#     survey_sites_colnames = survey_sites.columns
#     el_and_comms_colnames = el_and_comms.columns
#     #
#     geometry_options = {"tmargin": "1cm", "lmargin": "1cm"}
#     doc = Document(geometry_options=geometry_options)
#     with doc.create(Section(f'{property_name}')):
#         # Raw Site Descriptions (directly drawn from FIND)
#         for i in range(survey_sites.shape[0]):
#             curr_sitename = survey_sites.iloc[i].at['survey_sit']
#             curr_sitedesc = survey_sites.iloc[i].at['site_desc']
#             doc.append(MediumText(f'{curr_sitename}: {curr_sitedesc}\n'))
#             doc.append("not end here ----\n")
#             doc.append("~~~~~~~")


    # Create titles
    # with doc.create(Section(f'{property_name} Report')):
    #     doc.append('Here is the survey sites report that you requested:\n')
    #     doc.append(f'There are {survey_sites_row_num} survey sites in total in the area you requested.\n')
    #     with doc.create(Subsection('Survey sites table')):
    #         # Get table width to align with number of columns in survey_sites_df
    #         table_spec = "c|"*survey_sites_col_num
    #         # print("table_spec:", table_spec)
    #
    #         with doc.create(Tabular(table_spec)) as table: # table width to be edited
    #             # Add column names
    #             table.add_row(tuple(survey_sites_colnames[:survey_sites_col_num]))
    #             for i in range(survey_sites_row_num):
    #                 curr_row = survey_sites.iloc[i, :4]
    #                 table.add_hline()
    #                 table.add_row(tuple(curr_row))
    #
    # with doc.create(Section('Species Information Report')):
    #     doc.append('Here is the summary of elements and communities stored in our database:')
    #     with doc.create(Subsection('el_and_comms table')):
    #         # Get table width to align with number of columns in el_and_comms_df
    #         table_spec = "c|"*el_and_comms_col_num
    #         with doc.create(Tabular(table_spec)) as table:
    #             # Add column names
    #             table.add_row(tuple(el_and_comms_colnames[:el_and_comms_col_num]))
    #             for i in range(el_and_comms_row_num):
    #                 curr_row = el_and_comms.iloc[i, :4]
    #                 table.add_hline()
    #                 table.add_row(tuple(curr_row))
    # doc = report_template.template(survey_sites, el_and_comms, property_name, species_info_df)

    import os

from pylatex import Document, PageStyle, NewPage, SubFigure, Figure, Section, Command
from pylatex.utils import NoEscape
import os
import arcpy
import subprocess

imageFilename = r"C:\Users\hyu\Desktop\cat.jpg"


geometry_options = {"head": "30pt",
                    "margin": "0.3in",
                    "top": "0.2in",
                    "bottom": "0.4in",
                    "includeheadfoot": True}

doc = Document(geometry_options=geometry_options)
# first_page = PageStyle("firstpage")
# doc.preamble.append(first_page)
# doc.change_document_style("firstpage")
#
# with doc.create(Section('Plotting multiple figures')):
#     doc.append("How to set the pictures at center of page without change the width?")
#
#     with doc.create(Figure(position='h!')) as imagesRow1:
#         doc.append(Command('centering'))
#         with doc.create(
#                 SubFigure(position='c', width=NoEscape(r'0.33\linewidth'))) as left_imagesRow1:
#             left_imagesRow1.add_image(imageFilename, width=NoEscape(r'0.95\linewidth'))
#             left_imagesRow1.add_caption("img 1")
#
#         with doc.create(
#                 SubFigure(position='c', width=NoEscape(r'0.33\linewidth'))) as right_imagesRow1:
#             right_imagesRow1.add_image(imageFilename, width=NoEscape(r'0.95\linewidth'))
#             right_imagesRow1.add_caption("img 2")
#
#     with doc.create(Figure(position='h!')) as imagesRow2:
#         doc.append(Command('centering'))
#         with doc.create(
#                 SubFigure(position='c', width=NoEscape(r'0.33\linewidth'))) as left_imagesRow2:
#             left_imagesRow2.add_image(imageFilename, width=NoEscape(r'0.95\linewidth'))
#             left_imagesRow2.add_caption("img 3")
#
#         with doc.create(
#                 SubFigure(position='c', width=NoEscape(r'0.33\linewidth'))) as right_imagesRow2:
#             right_imagesRow2.add_image(imageFilename, width=NoEscape(r'0.95\linewidth'))
#             right_imagesRow2.add_caption("img 4")
#
#     imagesRow2.add_caption("Setting the subpictures at center")
#
# doc.append(NewPage())
#
# doc.append(NewPage())
# doc.append("OH HIIIIII!")

# Number of rows and columns
num_rows = 2
num_cols = 3
for j in range(num_rows):
    # Create a single imagesRow
    with doc.create(Figure(position='h!')) as imagesRow:
        # Create a subfigure for each image
        for i in range(num_cols):
            with imagesRow.create(SubFigure(position='c', width=NoEscape(r'0.33\linewidth'))) as subfig:
                # Add the image to the subfigure
                subfig.add_image(imageFilename.format(i), width=NoEscape(r'0.95\linewidth'))
                # Add a caption for the subfigure
                subfig.add_caption('Caption for Image {}'.format(i))
                # subfig.append("HIIIIII\n")

output_pdf_path = "C:/Users/hyu/Desktop"
property_name = "hiii"
doc.generate_tex(filepath=f'{output_pdf_path}' + '/' + f'{property_name}_report')

# Specify the path to the LaTeX file
latex_file = f'{output_pdf_path}' + '/' + f'{property_name}_report.tex'
arcpy.AddMessage(f"LaTeX file is generated here: {latex_file}")

# Specify the path to the output PDF file
pdf_file = f'{output_pdf_path}'
arcpy.AddMessage(f"PDF file is generated here: {pdf_file}")

# Execute the LaTeX compiler command and move PDF report to user-specified directory
subprocess.run(['pdflatex', '-output-directory=' + pdf_file, latex_file])

