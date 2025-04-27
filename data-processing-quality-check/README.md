# Load the CSV file
file_path = 'C://Users//vagisha//Downloads/d257d5b07bad8da44320fdfc54b21f1f.csv'
data = pd.read_csv(file_path)
print(data.columns)

# Convert index to datetime if necessary
# data['Observation period'] = pd.to_datetime(data['Observation period'])  # Adjust column name if needed
# data.set_index('dateperiod', inplace=True)

# print(data)

data[['start_time', 'end_time']] = data['Observation period'].str.split('/', expand=True)
data['start_time'] = pd.to_datetime(data['start_time'])
data['end_time'] = pd.to_datetime(data['end_time'])

# Make sure GHI and TOA are not zero or negative (clip to avoid math errors)
ghi = data['Clear sky GHI'].clip(lower=0)
toa = data['TOA'].clip(lower=1e-6)  # avoid divide by zero

cos_zenith = ghi / toa

# Clip to valid range for arccos (sometimes floating point errors make it slightly >1 or < -1)
cos_zenith = np.clip(cos_zenith, -1.0, 1.0)

data['Solar_Zenith_Angle'] = np.degrees(np.arccos(cos_zenith))

# print(data)


# # Define extraterrestrial irradiance and site location
I_0n = 1367  # W/m²
latitude = 28.42
longitude = 77.15
altitude = 216  #south delhi region

data['cos_theta'] = np.cos(np.radians(data['Solar_Zenith_Angle']))

# Filter cos_theta to avoid division by zero or negatives
data['cos_theta'] = data['cos_theta'].clip(lower=0.01)

# Step 3: Calculate GHI (optional, since 'Clear sky GHI' already exists)
# Formula: GHI = DHI + BNI * cos(zenith)
dhi = data['Clear sky DHI']
bni = data['Clear sky BNI']

# If BNI is missing or NaN, clip or fill
bni = bni.fillna(0)

# Calculate GHI
calculated_ghi = dhi + bni * cos_zenith

# Step 4: Add calculated GHI to dataframe
data['GHI'] = calculated_ghi

# Step 5 (Optional): Calculate DHI from GHI and BNI if needed
# Formula: DHI = GHI - BNI * cos(zenith)
calculated_dhi = calculated_ghi - bni * cos_zenith
data['DHI'] = calculated_dhi

data['DNI'] = (data['GHI'] - data['Clear sky DHI']) / cos_zenith


# Basic checks (already in your code)
data['1a_flag'] = (-4 < data['GHI']) & (data['GHI'] < 1.5 * I_0n * data['cos_theta'] ** 1.2 + 100)
data['1b_flag'] = (-4 < data['DHI']) & (data['DHI'] < 0.95 * I_0n * data['cos_theta'] ** 1.2 + 50)
data['1c_flag'] = (-4 < data['DNI']) & (data['DNI'] < I_0n)

# Compute Kt, Kd, Kn
data['Kt'] = data['GHI'] / (I_0n * data['cos_theta'])
data['Kd'] = data['DHI'] / data['GHI']
data['Kn'] = data['DNI'] / I_0n

# Replace infinite or NaN due to division by 0
data.replace([np.inf, -np.inf], np.nan, inplace=True)
data.dropna(subset=['Kt', 'Kd', 'Kn'], inplace=True)

# Condition (8): Kd < 1.05 for GHI > 50 and qZ < 75°
data['cond_8'] = ((data['GHI'] > 50) & (data['Solar_Zenith_Angle'] < 75) & (data['Kd'] < 1.05))

# Condition (9): Kd < 1.10 for GHI > 50 and qZ > 75°
data['cond_9'] = ((data['GHI'] > 50) & (data['Solar_Zenith_Angle'] > 75) & (data['Kd'] < 1.10))

# Condition (10): Kn < 0.8
data['cond_10'] = (data['Kn'] < 0.8)

# Condition (11): Kd < 0.96 for Kt > 0.6
data['cond_11'] = ((data['Kt'] > 0.6) & (data['Kd'] < 0.96))

# Final composite quality flag (all conditions must be met)
data['quality_flag'] = (
    (data['cond_8'] | data['cond_9']) &
    data['cond_10'] &
    data['cond_11']
)

# Output result
print(data[['GHI', 'DHI', 'DNI', 'Solar_Zenith_Angle', 'Kd', 'Kn', 'Kt', 'quality_flag']])
data.to_excel("C://Users//vagisha//Downloads/report.xlsx", index=False)



Application of K’s Limits Test (Physical Limits Test)
In this step, each measured irradiance component is checked against theoretical physical limits:
•	Irradiance values must be non-negative (≥ 0 W/m²).
•	The maximum possible value is set based on extraterrestrial solar radiation at the given location and solar zenith angle, typically allowing a margin for atmospheric effects.
•	Any data points falling outside these physical boundaries are flagged as physically unrealistic. K-tests are applied by assessing the Kd, Kn and Kt-space. The BSRN tests, as well as
the K-tests, are applied as follows:
Kd < 1.05 for GHI > 50 and qZ < 75
Kd < 1.10 for GHI > 50 and qZ > 75
Kn < 0.8, 
Kd < 0.96 for Kt > 0.6. 

4. Individual Limits Test
Separate limit checks are applied individually to GHI, DNI, and DHI measurements:
•	Maximum thresholds are defined based on standard expected maximum solar radiation values for the geographic location and season.
•	DHI is tested to ensure it does not exceed GHI under clear-sky conditions.
•	DNI values are compared against the solar constant adjusted for atmospheric path length.
•	Data points exceeding individual component thresholds are identified and flagged for further investigation. The individual limits for GHI, DHI, and DNI are assessed using:
􀀀4 < GHI < 1.5I0n(cos qZ)1.2 + 100,
􀀀4 < DHI < 0.95I0n(cos qZ)1.2 + 50,
􀀀4 < DNI < I0n,
DHI < 0.8 _ G0h,
GHI 􀀀 DHI < G0h,
DNI < 1100 + 0.03Elev.
5. Night-Time Zero Testing
This test focuses on ensuring that irradiance values approach zero during periods when the sun is below the horizon (solar zenith angle > 90°):
•	GHI, DNI, and DHI values during night-time periods are checked.
•	Non-zero or significantly positive values during night are flagged as potential sensor offset errors, electronic noise, or incorrect timestamp issues.
The night-time values are removed using:
GHI > 5, 
qZ < 85_.


GHI = DHI + DNI cos@
BHI = DNI cos@
DNI = BNI