# Name: NHA Visit Combinator
# Purpose: Perform simple statistical analysis (Mean, Median, Min, Max, Count) on NHA visit years
# Author: Helena Yu
# Created: 08/04/2023
# Updates:
# --------------------
# Extensibility: local paths that need to be modified to match those on different computers:
#                1. NHA_path: local path to NHA database
#                2. biotics_path: local path to Biotics database
# Notes:
# All the try-except operations are used for integrating local testings with formal arcpy functions; they specify the
# path to the feature class if already created
#

import arcpy
import os
import pandas as pd
import numpy as np
from datetime import datetime as dt
import matplotlib.pyplot as plt

# Initialize local geodatabase paths (modify for extensibility)
NHA_path = r"C:\\Users\\hyu\\Desktop\\GIS_projects\\NHA.gdb"
Biotics_path = r"C:\\Users\\hyu\\Desktop\\GIS_projects\\Biotics_datasets.gdb"

eo_ptreps_path = os.path.join(Biotics_path, "eo_ptreps")
eo_sourceln_path = os.path.join(Biotics_path, "eo_sourceln")
eo_sourcept_path = os.path.join(Biotics_path, "eo_sourcept")
eo_sourcepy_path = os.path.join(Biotics_path, "eo_sourcepy")
NHA_core_path = os.path.join(NHA_path, "NHA_core")

# Buffer eo_sourceln, eo_sourcept for 1m to create polygons: if feature layers exist then get the path, else buffer
try:
    new_sourceln = arcpy.Describe(f"{Biotics_path}/new_sourceln").catalogPath
except OSError:
    new_sourceln = arcpy.analysis.Buffer(in_features=eo_sourceln_path,
                                         out_feature_class=os.path.join(Biotics_path, "new_sourceln"),
                                         buffer_distance_or_field="1 Meters")

try:
    new_sourcept = arcpy.Describe(f"{Biotics_path}/new_sourcept").catalogPath
except OSError:
    new_sourcept = arcpy.analysis.Buffer(in_features=eo_sourcept_path,
                                         out_feature_class=os.path.join(Biotics_path, "new_sourcept"),
                                         buffer_distance_or_field="1 Meters")

# Buffer eo_sourcepy for 1m to match buffer size with eo_sourceln and eo_sourcept
try:
    new_sourcepy = arcpy.Describe(f"{Biotics_path}/new_sourcepy").catalogPath
except OSError:
    new_sourcepy = arcpy.analysis.Buffer(in_features=eo_sourcepy_path,
                                         out_feature_class=os.path.join(Biotics_path, "new_sourcepy"),
                                         buffer_distance_or_field="1 Meters")

# Merge the 3 updated polygons
try:
    eo_sources = arcpy.Describe(f"{Biotics_path}/eo_sources").catalogPath
except:
    eo_sources = arcpy.management.Merge([new_sourceln, new_sourcept, new_sourcepy],
                                        os.path.join(Biotics_path, "eo_sources"))

# Join EO fields to merged SF layer for where_clause
arcpy.JoinField_management(eo_sources, "EO_ID", eo_ptreps_path, "EO_ID", ["LASTOBS", "LASTOBS_YR", "EORANK"])
# calculate 50 years ago to use with state listed plants
year = dt.now().year - 50
# Use query to copy all qualifying EO records to new table
where_clause = "(((ELCODE LIKE 'AB%' AND LASTOBS >= '1990') OR " \
               "(ELCODE = 'ABNKC12060' AND LASTOBS >= '1980')) OR " \
               "(((ELCODE LIKE 'P%' OR ELCODE LIKE 'N%' OR ELCODE LIKE 'C%' OR ELCODE LIKE 'H%' OR ELCODE LIKE 'G%') AND (LASTOBS >= '{0}')) OR ((ELCODE LIKE 'P%' OR ELCODE LIKE 'N%') AND (USESA = 'LE' OR USESA = 'LT') AND (LASTOBS >= '1950'))) " \
               "OR (((ELCODE LIKE 'AF%' OR ELCODE LIKE 'AA%' OR ELCODE LIKE 'AR%') AND (LASTOBS >= '1950')) OR (ELCODE = 'ARADE03011')) OR (((ELCODE LIKE 'AM%' OR ELCODE LIKE 'OBAT%') AND ELCODE <> 'AMACC01150' AND LASTOBS >= '1970') OR (ELCODE = 'AMACC01100' AND LASTOBS >= '1950') OR (ELCODE = 'AMACC01150' AND LASTOBS >= '1985')) OR (((ELCODE LIKE 'IC%' OR ELCODE LIKE 'IIEPH%' OR ELCODE LIKE 'IITRI%' OR ELCODE LIKE 'IMBIV%' OR ELCODE LIKE 'IMGAS%' OR ELCODE LIKE 'IP%' OR ELCODE LIKE 'IZ%') AND LASTOBS >= '1950') OR (ELCODE LIKE 'I%' AND ELCODE NOT LIKE 'IC%' AND ELCODE NOT LIKE 'IIEPH%' AND ELCODE NOT LIKE 'IITRI%' AND ELCODE NOT LIKE 'IMBIV%' AND ELCODE NOT LIKE 'IMGAS%' AND ELCODE NOT LIKE 'IP%' AND ELCODE NOT LIKE 'IZ%' AND LASTOBS >= '1980'))OR (LASTOBS = '' OR LASTOBS = ' ')) AND (EO_TRACK = 'Y' OR EO_TRACK = 'W') AND (LASTOBS <> 'NO DATE' AND EORANK <> 'X' AND EORANK <> 'X?') AND (EST_RA <> 'Very Low' AND EST_RA <> 'Low')".format(year)
# create feature layer filtered by where_clause
new_eo_sources = arcpy.MakeFeatureLayer_management(eo_sources, "new_eo_sources", where_clause)

# Create a data frame for new_eo_sources => fill in NULL values in eo_visits with LASTOBS_YR
new_eo_sources_arr = arcpy.da.FeatureClassToNumPyArray(in_table=new_eo_sources,
                                                       field_names=["SF_ID", "LASTOBS_YR"],
                                                       null_value=-9999)
new_eo_sources_df = pd.DataFrame(new_eo_sources_arr)

# Insert spatial join between SF features and NHAs to get NHA join id (exclude NHAs with Historic or Draft statuses)
where_clause2 = "STATUS NOT IN ('Draft', 'Historic', 'H', 'D')"
filtered_status_NHAlyr = arcpy.MakeFeatureLayer_management(NHA_core_path, "filtered_status_NHAlyr", where_clause2)
try:
    SF_NHA_joined_path = arcpy.Describe(f"{NHA_path}/SF_NHA_joined").catalogPath
except OSError:
    SF_NHA_joined_path = os.path.join(NHA_path, "SF_NHA_joined")
    arcpy.analysis.SpatialJoin(target_features=new_eo_sources,
                               join_features=filtered_status_NHAlyr,
                               out_feature_class=SF_NHA_joined_path,
                               join_operation="JOIN_ONE_TO_MANY")


# create copy of Visits table in memory space to work with/alter
VISITS_path = os.path.join(Biotics_path, "VISITS")
VISITS_path = arcpy.TableToTable_conversion(VISITS_path, "memory", "visits_tbl")

# Add field that extracts year from VISIT_DATE in VISITS in Biotics
arcpy.management.AddField(in_table=VISITS_path,
                          field_name="visit_year",
                          field_type="Integer")
with arcpy.da.UpdateCursor(VISITS_path, ["VISIT_DATE", "visit_year"]) as cursor:
    for row in cursor:
        curr_date = row[0]
        if curr_date is not None:
            formattedTime = dt.strftime(curr_date, "%Y")
            row[1] = int(formattedTime)
            cursor.updateRow(row)
del cursor

# Outer join VISITS and SF_NHA_joined based on SF_ID
eo_visits = arcpy.management.AddJoin(in_layer_or_view=VISITS_path,
                                     in_field="SF_ID",
                                     join_table=SF_NHA_joined_path,
                                     join_field="SF_ID",
                                     join_type="KEEP_ALL")
def get_null_dict(fields):
    res_dict = dict()
    for field in fields:
        # Assign default values to various types to handle null values
        if field.type == 'String':
            res_dict[field.name] = "-9999"
        elif field.type == 'Integer' or 'SmallInteger':
            res_dict[field.name] = -9999
        elif field.type == 'Double' or field.type == 'Single':
            res_dict[field.name] = -9999.0
    return res_dict

eo_visits_fields = arcpy.ListFields(eo_visits)
eo_visits_cleaned_fields = []
eo_visits_cleaned_fieldnames = []
for field in eo_visits_fields:
    if field.type != 'Date' and field.type != 'OID':
        eo_visits_cleaned_fields.append(field)
        eo_visits_cleaned_fieldnames.append(field.name)
null_dict = get_null_dict(eo_visits_cleaned_fields)
eo_visits_arr = arcpy.da.TableToNumPyArray(eo_visits, field_names=eo_visits_cleaned_fieldnames, null_value=null_dict)
eo_visits_df = pd.DataFrame(data=eo_visits_arr)

# If visits_tbl.visit_year is NULL, fill it out with LASTOBS_YR from new_eo_sources
# Pre-checked that new_eo_sources_df["SF_ID"] are all unique, no need to handle duplicates/overlapping
assert(len(pd.unique(new_eo_sources_df["SF_ID"])) == len(new_eo_sources_df["SF_ID"]))
if "VISITS.visit_year" in list(eo_visits_df.columns):
    visit_year_column = "VISITS.visit_year"
    sf_id_column = "VISITS.SF_ID"
else:
    visit_year_column = "visits_tbl.visit_year"
    sf_id_column = "visits_tbl.SF_ID"
for i in eo_visits_df.index:
    if eo_visits_df.at[i, visit_year_column] == -9999:
        curr_sf_id = eo_visits_df.at[i, sf_id_column]
        new_row = new_eo_sources_df[new_eo_sources_df["SF_ID"] == curr_sf_id]
        if new_row.empty:
            continue
        else:
            eo_visits_df.at[i, visit_year_column] = new_row["LASTOBS_YR"]

# Add dictionary for reference and comparison: extract year from SOURCE_REPORT
VISIT_year_reference = dict()
with arcpy.da.SearchCursor(eo_visits, ["SF_NHA_joined.SOURCE_REPORT", "SF_NHA_joined.NHA_JOIN_ID"]) as cursor:
    for row in cursor:
        source_report = row[0]
        if source_report is None:
            continue
        curr_year = source_report[:4]
        if not (curr_year.isnumeric()):
            continue
        NHA_id = row[1]
        # Update reference dictionary
        if NHA_id not in VISIT_year_reference:
            VISIT_year_reference[NHA_id] = curr_year
        else:
            if VISIT_year_reference[NHA_id] < curr_year:
                VISIT_year_reference[NHA_id] = curr_year
del cursor

# Perform statistical analysis on visit years: Min, Max, Mean, and Median
stats_fields = [[visit_year_column, "MIN"], [visit_year_column, "MAX"], [visit_year_column, "MEAN"],
                [visit_year_column, "MEDIAN"]]

try:
    stat_analysis_path = arcpy.Describe(f"{NHA_path}/stat_res").catalogPath
    arcpy.management.Delete(stat_analysis_path)
    arcpy.analysis.Statistics(in_table=eo_visits,
                              out_table=stat_analysis_path,
                              statistics_fields=stats_fields,
                              case_field=["SF_NHA_joined.NHA_JOIN_ID"])
except OSError:
    stat_analysis_path = os.path.join(NHA_path, "stat_res")
    arcpy.analysis.Statistics(in_table=eo_visits,
                              out_table=stat_analysis_path,
                              statistics_fields=stats_fields,
                              case_field=["SF_NHA_joined.NHA_JOIN_ID"])

# Add VISIT year as reference
arcpy.management.AddField(in_table=stat_analysis_path,
                          field_name="VISIT_year_reference",
                          field_type="Integer")
with arcpy.da.UpdateCursor(stat_analysis_path, ["VISIT_year_reference", "SF_NHA_joined_NHA_JOIN_ID"]) as cursor:
    for row in cursor:
        if row[1] in VISIT_year_reference:
            row[0] = VISIT_year_reference[row[1]]
            cursor.updateRow(row)
del cursor

# Add two fields for count before and after reference VISIT_year: count_before & count_after
arcpy.management.AddField(in_table=stat_analysis_path,
                          field_name="count_before",
                          field_type="Integer")
arcpy.management.AddField(in_table=stat_analysis_path,
                          field_name="count_after",
                          field_type="Integer")
with arcpy.da.UpdateCursor(stat_analysis_path, ["VISIT_year_reference", "SF_NHA_joined_NHA_JOIN_ID",
                                                "count_before", "count_after"]) as cursor:
    for row in cursor:
        curr_ref, curr_NHA_id = row[0], row[1]
        if curr_NHA_id in VISIT_year_reference:
            curr_df = eo_visits_df[eo_visits_df["SF_NHA_joined.NHA_JOIN_ID"] == curr_NHA_id]
            before_df = curr_df[curr_ref >= curr_df[visit_year_column]]
            before_df = before_df[before_df[visit_year_column] > 0]
            row[2] = before_df.shape[0]
            row[3] = curr_df.shape[0] - before_df.shape[0]
            cursor.updateRow(row)
del cursor

# Clear up temporarily added feature classes
arcpy.management.Delete(new_sourceln)
arcpy.management.Delete(new_sourcept)
arcpy.management.Delete(new_sourcepy)
arcpy.management.Delete(eo_sources)
arcpy.management.Delete(SF_NHA_joined_path)

# Visualize the visit counts before and after the reference year for each NHA
# Convert stat_analysis_path to dataframe
def getnull(oid):
    nullRows.append(oid)
    return True

nullRows = list()
stat_res_arr = arcpy.da.TableToNumPyArray(stat_analysis_path,
                                          field_names="*",
                                          skip_nulls=getnull)
stat_res_df = pd.DataFrame(stat_res_arr)

# NHA_join_ids: numpy array of NHA_join_ids of NHAs that user requested, default is all
def plot_NHA(stat_res_df, NHA_join_ids):
    df = stat_res_df[stat_res_df['SF_NHA_joined_NHA_JOIN_ID'].isin(NHA_join_ids)]
    NHA_join_IDs = NHA_join_ids.tolist()  # Convert numpy array to list
    visit_counts = {
        'before REF': np.array(df["count_before"]),
        'after REF': np.array(df["count_after"]),
    }

    width = 0.6  # the width of the bars: can also be len(x) sequence

    fig, ax = plt.subplots()
    bottom = np.zeros(len(NHA_join_IDs))

    for label, counts in visit_counts.items():
        p = ax.bar(NHA_join_IDs, counts, width, label=label, bottom=bottom)
        bottom += counts

        ax.bar_label(p, label_type='center')

    ax.set_title('NHA Visits Visualization')
    ax.legend()

    plt.show()

# Example of calling this simple visualization:
# plot_NHA(stat_res_df, np.array(['xxx43062', 'ct69874']))
