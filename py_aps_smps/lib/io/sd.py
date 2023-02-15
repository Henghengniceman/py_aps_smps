#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 28 11:24:50 2021

Read information about size distributions from database

@author: tobias.schorr@kit.edu
"""
import warnings
import pandas as pd

from py_aps_smps.lib.io.sql import sql_query


def read_sd_parameters(device_name, exp_id):
    """Read size distribution parameters from database"""
    query = f'SELECT * FROM {device_name}_parameter WHERE (id = {exp_id})'
    sd_parameters = sql_query('device_data', query)
    sd_parameters = sd_parameters.to_dict(orient='records')[0]
    sd_parameters['timestamp'] = pd.Timestamp(sd_parameters.pop('zeitpunkt'))
    return sd_parameters


def read_sd_calibration_table(device_name, sd_parameters):
    """Read calibration table to map channels to sizes from database"""
    if 'aps' in device_name:
        diameter_column_name = 'dp_um'
    elif 'smps' in device_name:
        diameter_column_name = 'dp_nm'
    
    query = (f"SELECT {diameter_column_name}, effizienz, messkanal "
             f"FROM {device_name}_messmodus "
             f"WHERE (kampagne = '{sd_parameters['kampagne']}' "
             f"AND messmodus = {sd_parameters['messmodus']} "
             f"AND {diameter_column_name} != 0)")
    calibration_table = sql_query('device_data', query, df_index_col='messkanal')
    
    if len(calibration_table) == 0:
        warnings.warn(f'No data in database table {device_name}_messmodus', UserWarning)
    return calibration_table


# %%

def read_raw_sd(device_name, exp_id):
    """Import APS or SMPS size distribution data from database.

    Parameters
    ----------
    device_name : str
        Name of the device, e.g. 'aps3' or 'smps2'.
    exp_id : str or int
        SMPS_id or APS_id related to a specific size distribution measurement.

    Returns
    -------
    SD_data : pd.DataFrame()
        Contains information on number of particles per channel/size
    
    See also
    --------
    in size_distribution_analysis.py
        * correct_extend_truncate_raw_sd_data()
        * combine_SMPS_APS_sd()
        * analyze_sd()

    """
    from py_aps_smps.lib.sd_processing.structure import calc_bin_boundaries
    from py_aps_smps.lib.sd_processing.content import calc_dXdlogd_from_dX
    
    exp_id = str(exp_id)  # format variable to a str, if input was an integer
    
    def get_raw_sd_data(device_name, exp_id):
        """read size distribution data, with values mapped to channels"""
        query = f'SELECT messwert, messkanal FROM {device_name}_data WHERE (id = {exp_id})'
        sd_data = sql_query('device_data', query, df_index_col='messkanal')
        
        if len(sd_data) == 0:
            warnings.warn(f'No data in database table {device_name}_data', UserWarning)
        return sd_data
    
    def add_size_calibration_to_sd_table(sd_data, calibration_table):
        """Combine bin channel number with corresponding diameter"""
        if 'smps' in device_name:
            calibration_table['dp_um'] = calibration_table['dp_nm'].rename('dp_um') / 1000
    
        sd_data_calib = pd.concat([sd_data['messwert'], calibration_table['dp_um']], axis=1)
        return sd_data_calib
    
    def apply_efficiency_correction_on_dn(dN, size_bin_efficiency):
        return dN / size_bin_efficiency
    
    sd_parameters = read_sd_parameters(device_name, exp_id)
    calibration_table = read_sd_calibration_table(device_name, sd_parameters)
    
    sd_data = get_raw_sd_data(device_name, exp_id)
    sd_data = add_size_calibration_to_sd_table(sd_data, calibration_table)
    sd_data = sd_data.rename(columns={'dp_um': 'dp'})  # in µm
    sd_data['dp_lower'], sd_data['dp_upper'] = calc_bin_boundaries(sd_data['dp'], sd_parameters['channel_res'])  # add bin boundaries
    sd_data['dn'] = apply_efficiency_correction_on_dn(sd_data['messwert'], calibration_table['effizienz'])
    sd_data['dndlogd'] = calc_dXdlogd_from_dX(sd_data['dn'], channel_resolution=sd_parameters['channel_res'])
    return sd_data
