import os
import numpy as np
from pylatex import Document, Section, Subsection, Tabular, Math, TikZ, Axis, \
    Plot, Figure, Matrix, Alignat
from pylatex.utils import italic
import subprocess
import arcpy
import report_template

# Examples of pylatex: https://jeltef.github.io/PyLaTeX/current/examples.html
# Note: Remember to close the pdf file that you generated before running the program to edit/overwrite it!


def produce_report(survey_sites,
                   el_and_comms,
                   property_name,
                   output_path,
                   species_info_df):
    # arcpy.AddMessage("Entering produce_report")
    # arcpy.AddMessage(output_path)
    # survey_sites_row_num = survey_sites.shape[0]
    # survey_sites_col_num = 4
    # el_and_comms_row_num = el_and_comms.shape[0]
    # el_and_comms_col_num = 4
    #
    # survey_sites_colnames = survey_sites.columns
    # el_and_comms_colnames = el_and_comms.columns
    #
    # geometry_options = {"tmargin": "1cm", "lmargin": "1cm"}
    # doc = Document(geometry_options=geometry_options)
    #
    # # Create titles
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
    doc = report_template.template(survey_sites, el_and_comms, property_name, species_info_df)

    # doc.generate_tex(filepath=f'{current_path}/{property_name}_report')
    doc.generate_tex(filepath=f'{output_path}'+"/"+f'{property_name}_report')
    arcpy.AddMessage(f'generate report here: {output_path}'+"/"+f'{property_name}_report')

    # Specify the path to the LaTeX file
    latex_file = f'{output_path}'+"/"+f'{property_name}_report.tex'
    arcpy.AddMessage(f"latex_file: {latex_file}")

    # Specify the path to the output PDF file
    # pdf_file = f'{output_path}'+"/"+f'{property_name}_report.pdf'
    pdf_file = f'{output_path}'
    arcpy.AddMessage(f"pdf_file: {pdf_file}")

    # Execute the LaTeX compiler command and move PDF report to user-specified directory
    subprocess.run(
        ['pdflatex', '-output-directory=' + pdf_file, latex_file])
    arcpy.AddMessage("Successfully compiled latex-pdf conversion")

