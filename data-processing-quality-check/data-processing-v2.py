#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np
import os


# In[2]:


input_file_name = 'data-v2.xlsx'
file_path = os.path.join(os.getcwd(), 'input-files', input_file_name)
read_columns = ['Time_stamp', 'SOLAR_GHI_GROUND_01_AVG', 'SOLAR_DIRECTRADIATION_GROUND_01_AVG', 'SOLAR_DIFFUSERADIATION_GROUND_01_AVG', 'DAY_OF_YEAR', 'DECLINATION', 'EOT', 'TC', 'LST', 'HOUR_ANGLE', 'ZENITH_ANGLE']
data_DF = pd.read_excel(file_path, usecols=read_columns)
data_DF.head()


# In[3]:


# data_DF.head()
# data_DF.dtypes
# data_DF.isnull().sum()
if data_DF.isnull().values.any():
    data_DF = data_DF.dropna()
# data_DF.duplicated().sum()
# data_DF.describe()


# In[4]:


# Calculation for I0n
# Extraterrestrial irradiance on a normal surface 
# I0n = Isc(1 + 0.033 * cos( 360 * n/ 365))
# Isc​ is the solar constant (1367 W/m²)
# n is the day of the year (from the date in your period column)

data_DF['I0n'] = 1367 * (1 + 0.033 * np.cos(2 * np.pi * data_DF['DAY_OF_YEAR'] / 365))
data_DF['COS_ZENITH'] = np.cos(np.deg2rad(data_DF['ZENITH_ANGLE']))
data_DF.rename(columns={
    'SOLAR_GHI_GROUND_01_AVG': 'GHI', 
    'SOLAR_DIRECTRADIATION_GROUND_01_AVG': 'DNI', 
    'SOLAR_DIFFUSERADIATION_GROUND_01_AVG': 'DHI'
}, inplace=True)
data_DF['Kt'] = data_DF['GHI'] / (data_DF['I0n'] * data_DF['COS_ZENITH'])
data_DF['Kd'] = data_DF['DHI'] / data_DF['GHI']
data_DF['Kn'] = data_DF['DNI'] / data_DF['I0n']

# # Horizontal extraterrestrial irradiance G0h
data_DF['G0h'] = data_DF['I0n'] * data_DF['COS_ZENITH']
# data_DF.head()
data_DF.describe()


# In[5]:


# K-tests
k_test_condition_1 = (data_DF['GHI'] > 50) & (data_DF['ZENITH_ANGLE'] < 75) & (data_DF['Kd'] < 1.05)
k_test_condition_2 = (data_DF['GHI'] > 50) & (data_DF['ZENITH_ANGLE'] > 75) & (data_DF['Kd'] < 1.10)
k_test_condition_3 = (data_DF['Kn'] < 0.8) & (data_DF['Kn'] > 0)
k_test_condition_4 = (data_DF['Kd'] < 0.96) & (data_DF['Kt'] > 0.6)

data_DF['k_test'] = np.where(
    k_test_condition_1 | k_test_condition_2 | k_test_condition_3 | k_test_condition_4,
    'Passed',
    'Failed'
)
data_DF.head()


# In[6]:


#  Individual Limits Test (ILT)
ILT_condition_1 = (data_DF['GHI'] > -4) & (data_DF['GHI'] < (1.5 * data_DF['I0n'] * data_DF['COS_ZENITH']**1.2 + 100))
ILT_condition_2 = (data_DF['DHI'] > -4) & (data_DF['DHI'] < (0.97 * data_DF['I0n'] * data_DF['COS_ZENITH']**1.2 + 50))
ILT_condition_3 = (data_DF['DNI'] > -4) & (data_DF['DNI'] < data_DF['I0n'])
ILT_condition_4 = (data_DF['DHI'] < 0.8 * data_DF['G0h'])
ILT_condition_5 = (data_DF['GHI'] - data_DF['DHI'] < data_DF['G0h'])

data_DF['individual_limit_test'] = np.where(
    ILT_condition_1 | ILT_condition_2 | ILT_condition_3 | ILT_condition_4 | ILT_condition_5,
    'Passed',
    'Failed'
)
data_DF.head()


# In[7]:


# Night-Time Zero Testing
filter_condition_1 = data_DF['GHI'] > 5
filter_condition_2 = data_DF['ZENITH_ANGLE'] < 85
data_DF['night_time_test'] = np.where(
    filter_condition_1 | filter_condition_2,
    'Passed',
    'Failed'
)
output_file_name = 'output-v2.csv'
output_path = os.path.join(os.getcwd(), 'output-files', output_file_name)
data_DF.to_csv(output_path, encoding='utf-8', index=None)
data_DF.head()

