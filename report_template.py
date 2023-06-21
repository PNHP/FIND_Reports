from pylatex import Document, Section, Subsection, Tabular, Math, TikZ, Axis, \
    Plot, Figure, Matrix, Alignat, MediumText, LineBreak, Head, MiniPage, NoEscape, \
    LargeText
from pylatex.utils import bold, italic

# Helper functions

def template(survey_sites_df, el_and_comms, property_name, species_info_df):
    # Initialize report page
    geometry_options = {"tmargin": "1cm", "lmargin": "1cm"}
    doc = Document(geometry_options=geometry_options)

    # Create title: bold{property}
    with doc.create(Head("L")) as left_header:
        with left_header.create(MiniPage(width=NoEscape(r"0.49\textwidth"),
                                        pos='c', align='l')) as title_wrapper:
            title_wrapper.append(LargeText(bold("Bank Account Statement")))
            title_wrapper.append(LineBreak())

    doc.append('Here is the survey sites report that you requested:\n')
    doc.append('There are survey sites in total in the area you requested.\n')




    doc.append(LineBreak())
    return doc
