#!/usr/bin/env python
# coding: utf-8

# In[11]:


import pandas as pd
import numpy as np
import os


# In[12]:


input_file_name = 'data.csv'
file_path = os.path.join(os.getcwd(), 'input-files', input_file_name)
columns = ['period', 'TOA', 'GHI', 'BHI', 'DHI', 'BNI']
data_DF = pd.read_csv(file_path, comment='#', sep=';', header=None, names=columns)
data_DF.head()


# In[13]:


data_DF[['start', 'end']] = data_DF['period'].str.split('/', expand=True)
# Convert to datetime
data_DF['start'] = pd.to_datetime(data_DF['start'])
data_DF['end'] = pd.to_datetime(data_DF['end'])
data_DF.head()
# data_DF.dtypes
# data_DF.isnull().sum()
# data_DF.duplicated().sum()
# data_DF.describe()


# In[14]:


# Calculate cosine of zenith using 
# GHI = DHI + DNI cos@
# DNI = BNI

data_DF['DNI'] = data_DF['BNI']
cos_zenith = (data_DF['GHI'] - data_DF['DHI']) / data_DF['DNI']

# Clamp values to [-1, 1] to avoid math errors
cos_zenith = np.clip(cos_zenith, -1, 1)
data_DF['cos_zenith'] = cos_zenith

# Compute zenith angle in radians and degree
data_DF['zenith_rad'] = np.arccos(cos_zenith)
data_DF['zenith_deg'] = np.degrees(data_DF['zenith_rad'])
# data_DF.fillna('NA', inplace=True)

# Extraterrestrial irradiance on a normal surface 
# I0n = Isc(1 + 0.033 * cos( 360 * n/ 365))
# Isc​ is the solar constant (1367 W/m²)
# n is the day of the year (from the date in your period column)

data_DF['day_of_year'] = (data_DF['start'] + (data_DF['end'] - data_DF['start']) / 2).dt.dayofyear
data_DF['I0n'] = 1367 * (1 + 0.033 * np.cos(2 * np.pi * data_DF['day_of_year'] / 365))
data_DF['Kt'] = data_DF['GHI'] / (data_DF['I0n'] * data_DF['cos_zenith'])
data_DF['Kd'] = data_DF['DHI'] / data_DF['GHI']
data_DF['Kn'] = data_DF['DNI'] / data_DF['I0n']

# Horizontal extraterrestrial irradiance G0h
data_DF['G0h'] = data_DF['I0n'] * data_DF['cos_zenith']
data_DF.head()


# In[15]:


# K-tests
k_test_condition_1 = (data_DF['GHI'] > 50) & (data_DF['zenith_deg'] < 75) & (data_DF['Kd'] < 1.05)
k_test_condition_2 = (data_DF['GHI'] > 50) & (data_DF['zenith_deg'] > 75) & (data_DF['Kd'] < 1.10)
k_test_condition_3 = (data_DF['Kn'] < 0.8) & (data_DF['Kn'] > 0)
k_test_condition_4 = (data_DF['Kd'] < 0.96) & (data_DF['Kt'] > 0.6)

data_DF['k_test'] = np.where(
    k_test_condition_1 | k_test_condition_2 | k_test_condition_3 | k_test_condition_4,
    'Passed',
    'Failed'
)
data_DF.head()


# In[16]:


#  Individual Limits Test (ILT)
ILT_condition_1 = (data_DF['GHI'] > -4) & (data_DF['GHI'] < (1.5 * data_DF['I0n'] * data_DF['cos_zenith']**1.2 + 100))
ILT_condition_2 = (data_DF['DHI'] > -4) & (data_DF['DHI'] < (0.97 * data_DF['I0n'] * data_DF['cos_zenith']**1.2 + 50))
ILT_condition_3 = (data_DF['DNI'] > -4) & (data_DF['DNI'] < data_DF['I0n'])
ILT_condition_4 = (data_DF['DHI'] < 0.8 * data_DF['G0h'])
ILT_condition_5 = (data_DF['GHI'] - data_DF['DHI'] < data_DF['G0h'])

data_DF['individual_limit_test'] = np.where(
    ILT_condition_1 | ILT_condition_2 | ILT_condition_3 | ILT_condition_4 | ILT_condition_5,
    'Passed',
    'Failed'
)
data_DF.head()


# In[17]:


# Night-Time Zero Testing
filter_condition_1 = data_DF['GHI'] > 5
filter_condition_2 = data_DF['zenith_deg'] < 85
data_DF['night_time_test'] = np.where(
    filter_condition_1 | filter_condition_2,
    'Passed',
    'Failed'
)
output_file_name = 'output.csv'
output_file_path = os.path.join(os.getcwd(), 'output-files', output_file_name)
data_DF.to_csv(output_file_path, encoding='utf-8')
data_DF.head()

