#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 28 11:21:34 2021

Read information about ambient conditions during size distribution measurement from database.

@author: tobias.schorr@kit.edu
"""
import warnings
import pandas as pd
from py_aps_smps.lib.io.sql import sql_query


def get_temperature_at_sd_exp(campaign, exp_num, chamber, trel):
    from sqlalchemy import exc
    """Read chamber temperature during size distribution measurement"""
    # read timestamp from from AIDA database `experimentliste`
    query = (f'SELECT RefZeit '
             f'FROM {chamber}.experimentliste '
             f'WHERE (Kampagne LIKE "{campaign}") '
             f'AND (ExperimentNr = {exp_num})')
    expansion_timestamp = sql_query(f'{chamber}', query, output_mode='dict')['RefZeit']
    time_sd = expansion_timestamp + pd.Timedelta(seconds=trel)
    
    # read temperature data
    try:
        if chamber == 'aida':
            select_columns = "Zeitpunkt, T_gasver2_thck_K, T_gasver4_thck_K, T_gasver6_thck_K, T_gasver8_thck_K"
        elif chamber == 'naua':
            select_columns = "Zeitpunkt, T_1NAUA_pt100_K, T_2NAUA_pt100_K, T_3NAUA_pt100_K"
        
        sql_time_fmt = "%Y-%m-%d %H:%M:%S"
        query = (f'SELECT {select_columns} FROM {campaign.lower()}_aida_sec '
                 f'WHERE Zeitpunkt BETWEEN "{(time_sd - pd.Timedelta(seconds=10)).strftime(sql_time_fmt)}" '
                 f'AND "{(time_sd + pd.Timedelta(seconds=10)).strftime(sql_time_fmt)}"')
        temp_gas_K = sql_query('aida', query, df_index_col='Zeitpunkt')
        temp_gas_K_mean = temp_gas_K.mean(axis=1).loc[time_sd]
    except exc.ProgrammingError as err:

        print("WARNING: Could not obtain mean temperature from temperature logger. Using room temperature.\n",
              "See error message: %s" % err)
        temp_gas_K_mean = 293.15
    return temp_gas_K_mean


def get_cpc_concentration_at_sd_exp(campaign, exp_num, chamber, trel, verbose=False):
    """Read CPC concentration during size distribution measurement."""
    # read timestamp from from AIDA database `experimentliste`
    query = (f'SELECT ExpStart, RefZeit, ExpEnde '
             f'FROM {chamber}.experimentliste '
             f'WHERE (Kampagne LIKE "{campaign}") '
             f'AND (ExperimentNr = {exp_num})')
    (t_start, expansion_timestamp, t_end) = sql_query('aida', query, output_mode='dict').values()
    t_sd = expansion_timestamp + pd.Timedelta(seconds=trel)
    
    if chamber.lower() == 'aida':
        query = (f'SELECT modus_cpc3010 '
                 f'FROM aida.in_ergebnisse '
                 f'WHERE (Kampagne LIKE "{campaign}") '
                 f'AND (ExperimentNr = {exp_num})')
        cpc3010_modus = sql_query('aida', query, output_mode='dict')['modus_cpc3010']

        if cpc3010_modus != 0:
            db_table = campaign.lower() + '_aida_cpc'
            query = f"SELECT * FROM {db_table} WHERE Zeitpunkt BETWEEN '{t_start}' AND '{t_end}'"
            cn = sql_query(database='aida', query=query, df_index_col='Zeitpunkt') * cpc3010_modus
            
        else:
            warn_msg = "aida.in_ergebnisse states that CPC3010 was not in use. Can not obtain CPC data."
            warnings.warn(warn_msg, UserWarning)
            return None

    elif chamber.lower() == 'naua':
        db_table = campaign.lower() + '_aida_sec'
        db_column = 'CNNAUA2_N0_ppc'
        
        if verbose:
            print("Info: Reading NAUA CPC number concetration from database "
                  f"      column '{db_column}' from {db_table}.")
        
        query = f"SELECT Zeitpunkt, {db_column} FROM {db_table} WHERE Zeitpunkt BETWEEN '{t_start}' AND '{t_end}'"
        cn = sql_query(database='aida', query=query, df_index_col='Zeitpunkt')
        
    cn_at_sd_exp = cn.loc[t_sd + pd.Timedelta(seconds=-10): t_sd + pd.Timedelta(seconds=10)].mean().item()
    return cn_at_sd_exp
