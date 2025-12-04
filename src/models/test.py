
from CoolProp.CoolProp import PropsSI

# Define the fluid and pressure (in Pa)
fluid = "R1234ZE"
pressure = 2.28 * 1e5  # Convert bar to Pa (1 bar = 1e5 Pa)

# Calculate the saturation temperature (in Kelvin)
saturation_temp_kelvin = PropsSI("T", "P", pressure, "Q", 1, fluid)

# Convert the temperature to Celsius
saturation_temp_celsius = saturation_temp_kelvin - 273.15
print(f"Saturation Temperature of {fluid} at {pressure/1e5} bar: {saturation_temp_celsius}°C")



Pc = PropsSI("PCRIT", " ", 0, " ", 0, "R1234ZE")
print(Pc)
'''
import sys
print(sys.path)

import pandas as pd

df = pd.read_excel('data/process_data/Manheim_data_original.xlsx', sheet_name="Mannheim_rlgwp_2025-10-22", header=0)

# Remove rows where Column30 == 0
df = df[df['Column21'] != 0.00]

# Save back to Excel
df.to_excel("data_cleaned.xlsx", index=False)
'''
