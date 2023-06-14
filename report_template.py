from pylatex import Document, Section, Subsection, Tabular, Math, TikZ, Axis, \
    Plot, Figure, Matrix, Alignat
from pylatex import Document, PageStyle, Head, MiniPage, Foot, LargeText, \
    MediumText, LineBreak, simple_page_number
from pylatex.utils import bold
from pylatex.utils import italic

# Helper functions

def template(survey_sites, el_and_comms, property_name, species_info_df):
    # Create title
    geometry_options = {"tmargin": "1cm", "lmargin": "1cm"}
    doc = Document(geometry_options=geometry_options)

    # Create titles
    with doc.create(Section((f'{property_name}'))):
        doc.append(LineBreak())
        # Raw Site Descriptions (directly drawn from FIND)
        for i in range(len(survey_sites)):
            curr_sitename = survey_sites.iloc[i, 'survey_sit']
            curr_sitedesc = survey_sites.iloc[i, 'site_desc']
            doc.append(MediumText(f'{curr_sitename}: {curr_sitedesc}\n'))

        doc.append(LineBreak())
    return doc