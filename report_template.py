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

    # Scratch: make a table for species info at this survey site
    # 1. get the species of the same refcode
    curr_refcode = curr_site["refcode"]
    site_species_df = species_info_df[species_info_df["refcode"] == curr_refcode]
    # 2. get all found elements in the area
    site_found_df = site_species_df[site_species_df["elem_found"] == "Y"]
    # SNAME, SCOMNAME, eo_rank, SPROT
    table_spec = "c|"*4
    site.append("Table of found elements in the area you requested:\n")
    with site.create(Tabular(table_spec)) as table:
        table.add_row(('SNAME','SCOMNAME','eo_rank','SPROT'))
        for i in range(site_found_df.shape[0]):
            curr_row = site_found_df.loc[i, ['SNAME', 'SCOMNAME', 'eo_rank', 'SPROT']]
            table.add_hline()
            table.add_row(tuple(curr_row))
    # 3. get all not_founded elements in the area
    site.append("Table of unfounded elements in the area you requested:\n")
    site_unfound_df = site_species_df[site_species_df["elem_found"] == "N"]
    with site.create(Tabular(table_spec)) as table:
        table.add_row(('SNAME', 'SCOMNAME', 'eo_rank', 'SPROT'))
        for i in range(site_unfound_df.shape[0]):
            curr_row = site_unfound_df.loc[i, ['SNAME', 'SCOMNAME', 'eo_rank', 'SPROT']]
            table.add_hline()
            table.add_row(tuple(curr_row))





    doc.append(LineBreak())
    return doc
