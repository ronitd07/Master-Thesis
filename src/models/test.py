from CoolProp.CoolProp import PropsSI

# Define the fluid and pressure (in Pa)
fluid = "R1234ZE"
pressure = 3.3 * 1e5  # Convert bar to Pa (1 bar = 1e5 Pa)

# Calculate the saturation temperature (in Kelvin)
saturation_temp_kelvin = PropsSI("T", "P", pressure, "Q", 1, fluid)

# Convert the temperature to Celsius
saturation_temp_celsius = saturation_temp_kelvin - 273.15
print(f"Saturation Temperature of {fluid} at {pressure/1e5} bar: {saturation_temp_celsius}°C")



Pc = PropsSI("PCRIT", " ", 0, " ", 0, "R1234ZE")
print(Pc)