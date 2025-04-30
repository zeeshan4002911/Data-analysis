## Automated Quality Control
The proposed QC methodology by [ 2] suggests a time-series visualisation and removes
duplicate and missing timestamps. An automated QC methodology is applied where
erroneous datapoints are automatically eliminated from the dataset without needing a
user review.
The automatic elimination flagging procedure includes datapoints which are phys-
ically impossible (from [ 10 ]), removing timestamps where no irradiance is recorded, i.e.,
night-time values (using [1,26 ]) K-tests (from [ 32]) and tracking errors. These QC proce-
dures are well-established and used within the available literature [2].
The automatic elimination process consists of three parts: removing night-time values,
K-tests, and then the individual limits of GHI, DHI, and DNI. The K-tests involve the direct
beam transmittance Kn, diffuse transmittance Kd and Kt. These K-values are given as:  
Kt = GHI / I0n · cos θZ   
Kd = DHI / GHI,   
Kn = DNI / I0n   

I0n is the extraterrestrial irradiance on a normal surface:  
I0n = ISC · (1 + 0.033 · cos( 360 · n / 365 ))  
where n denotes the day of the year and ISC denotes the solar constant (1367 W/m2).

The horizontal extraterrestrial irradiance G0h is defined by:  
G0h = I0n · cos θZ.

GHI, DHI and DNI units are in W/m2, and all K-values (Kt, Kn and Kd) are unitless.

### Application of K’s Limits Test (Physical Limits Test)
In this step, each measured irradiance component is checked against theoretical physical limits:
•	Irradiance values must be non-negative (≥ 0 W/m²).
•	The maximum possible value is set based on extraterrestrial solar radiation at the given location and solar zenith angle, typically allowing a margin for atmospheric effects.
•	Any data points falling outside these physical boundaries are flagged as physically unrealistic. K-tests are applied by assessing the Kd, Kn and Kt-space. The BSRN tests, as well as
the K-tests, are applied as follows:  
Kd < 1.05 for GHI > 50 and qZ < 75  
Kd < 1.10 for GHI > 50 and qZ > 75  
Kn < 0.8,   
Kd < 0.96 for Kt > 0.6.   

### Individual Limits Test
Separate limit checks are applied individually to GHI, DNI, and DHI measurements:
•	Maximum thresholds are defined based on standard expected maximum solar radiation values for the geographic location and season.
•	DHI is tested to ensure it does not exceed GHI under clear-sky conditions.
•	DNI values are compared against the solar constant adjusted for atmospheric path length.
•	Data points exceeding individual component thresholds are identified and flagged for further investigation. The individual limits for GHI, DHI, and DNI are assessed using:  
−4 < GHI < 1.5I0n(cos θZ )1.2 + 100,  
−4 < DHI < 0.95I0n(cos θZ )1.2 + 50,  
−4 < DN I < I0n,  
DHI < 0.8 · G0h,  
GHI − DHI < G0h,  

### Night-Time Zero Testing
This test focuses on ensuring that irradiance values approach zero during periods when the sun is below the horizon (solar zenith angle > 90°):
•	GHI, DNI, and DHI values during night-time periods are checked.
•	Non-zero or significantly positive values during night are flagged as potential sensor offset errors, electronic noise, or incorrect timestamp issues.
The night-time values are removed using:  
GHI > 5,   
qZ < 85.  

Note:. Formula for zenith angle @  
* GHI = DHI + DNI cos@  
* BHI = DNI cos@  
* DNI = BNI  

## Commands
For conversion to python from notebook  
`jupyter nbconvert .\data-processing-quality-check\data-processing-v2.ipynb --to python`