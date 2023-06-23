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


from pylatex import Document
from pylatex import Package
from pylatex import Tabu
import subprocess
from pylatex import Document, Tabular


# Create a new document
doc = Document()

# Create a table with a center-aligned and fixed width column
table = Tabular('|m{5cm}|c|')
table.add_hline()
table.add_row(('Center Aligned', 'Column 2'))
table.add_hline()

# Add content to the center-aligned column
content = 'This is a long text that should be center-aligned and have a fixed width of 5cm.'
table.add_row((content, 'Value'))

# Add the table to the document
doc.append(table)

output_pdf_path = "C:/Users/hyu/Desktop"
property_name = "hi"

doc.generate_tex(filepath=f'{output_pdf_path}' + '/' + f'{property_name}_report')

# Specify the path to the LaTeX file
latex_file = f'{output_pdf_path}' + '/' + f'{property_name}_report.tex'

# Specify the path to the output PDF file
pdf_file = f'{output_pdf_path}'

# Execute the LaTeX compiler command and move PDF report to user-specified directory
subprocess.run(['pdflatex', '-output-directory=' + pdf_file, latex_file])
