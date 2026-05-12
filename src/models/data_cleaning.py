
"""
Data cleaning of the input data

"""
import pandas as pd

input_file = "data/process_data/Manheim_data_original.xlsx"
sheet = "Mannheim_rlgwp_2025-10-22"
output_file = "data/process_data/Manheim_data_cleaned_automated.xlsx"

# Read the first 5 rows: header row + rows 1 to 4
top_rows = pd.read_excel(
    input_file,
    sheet_name=sheet,
    header=None,
    nrows=5
)

# Read actual data, skipping rows 1 to 4
df = pd.read_excel(
    input_file,
    sheet_name=sheet,
    header=0,
    skiprows=range(1, 5)
)

# Keep rows with compressor ON stage, power factor (COP) not nan, source inlet temp greater than source outlet of river water, condensor outlet temp. greater than water return temp at sink, cop greater than 1
df_filtered = df[(df["Column21"] == 1) &  (df["Column4"].notna()) & (df["Column27"] > df["Column28"]) & (df["Column16"] > df["Column24"]) &  (df["Column4"] > 1)]

# Write both parts to the same Excel file
with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
    top_rows.to_excel(
        writer,
        sheet_name=sheet,
        index=False,
        header=False,
        startrow=0
    )

    df_filtered.to_excel(
        writer,
        sheet_name=sheet,
        index=False,
        header=False,
        startrow=5
    )