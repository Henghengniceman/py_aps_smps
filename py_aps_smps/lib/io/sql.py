# -*- coding: utf-8 -*-
"""
Collection of scripts importing data from different sources

"""


# %% Import mySQL database entries
    
def sql_query(database, query, username='aida', password='aida',
              ip='141.52.172.3', port='3306', output_mode='df',
              df_index_col=None, verbose=False):
    """Fetch data from IMK-AAF MySQL database, returns pd.DataFrame or dictionary.
    
    Parameters
    ----------
    database : str
        Database name, e.g. *'aida'* or *'device_data'* or *'naua'*.
    query : str
        SQL query to fetch data from database, e.g.
    >>> query = "SELECT * FROM in_ergebnisse WHERE Kampagne = 'AWICIT04'"

    username : str
        user name to authenticate to SQL DB
    password : str
        Password corresponding to username to authenticate to SQL DB.
    ip : str
        IP address for SQL database
    port : str
        Port number to address SQL database

    output_mode : `str` ('df' or 'dict')
        mode = 'df'
            Returns multiple rows as DataFrame.
        mode = 'dict'
            Returns a single row as dictionary.
    df_index_col : str
        Specify which column name in *'select'* should be taken as :obj:`pd.DataFrame.index`.
    
    Returns
    -------
    :obj:`pd.DataFrame` or `dict`
        contains all data fetched via SQL query,
    
    with:
        
        :obj:`pd.DataFrame.columns`
            defined by 'select'
        :obj:`pd.DataFrame.index`
            column defined by 'df_index_col'
    
    Examples
    --------
    >>> q = sql_query('aida', 'in_ergebnisse', select='*',
    ...         where="Kampagne LIKE 'AWICIT04'", df_index_col = 'tref')
    >>> q
                         index  ExperimentID  ... modus_cpc3776  modus_cpc3772
    tref                                      ...
    2018-01-12 10:53:00   3914          3862  ...           0.0            0.0
    2018-01-12 15:56:00   3915          3863  ...           0.0            0.0
    2018-01-15 08:47:20   3916          3864  ...           0.0            0.0
    2018-01-15 10:26:00   3917          3865  ...           0.0            0.0
    ...
    """
    import pandas as pd
    import sqlalchemy
    
    database_url = f"mariadb+mariadbconnector://{username}:{password}@{ip}:{port}/{database}"
    engine = sqlalchemy.create_engine(database_url)
    
    # fetch multiple rows of data and return as pd.DataFrame
    result = pd.read_sql(query, engine, index_col=df_index_col)
    engine.dispose()  # clean up connection
    
    # try to return single returned row as dictionary
    if output_mode == 'dict':
        n_rows = len(result)
        if n_rows == 0:
            result = dict()
        elif n_rows == 1:
            result = result.iloc[0].to_dict()  # raises error if len>1
        elif n_rows > 1:
            raise ValueError(f"Expected a single row from database, but got {len(result)} rows.")
    
    return result
    

# %% read CPC3010 data from database
    
def read_cn_cpc3010(Campaign, t_start, t_end, verbose=False):
    """Read CPC-3010 data from SQL database for time interval defined in experimentliste
    
    Parameters
    ----------
    Campaign : :obj:`str`
        Name of campaign
    t_start : :obj:`pd.Timestamp()`
        Start of experiment, get from database table :obj:`aida.experimentliste`
    t_end : :obj:`pd.Timestamp()`
        End of experiment, get from database table :obj:`aida.experimentliste`
    verbose : :obj:`bool`, *optional*
        Print informational statements during function execution
    
    Returns
    -------
    :obj:`pd.DataFrame`
        containing CPC-3010 data in cm⁻³
        
        :obj:`pd.DataFrame.index`
            DatetimeIndex
            
        :obj:`pd.DataFrame.columns` : ['Particles_per_ccm']
            measured CPC concentration in cm⁻³
            
    See Also
    --------
    :func:`sql_query`,  :func:`read_cn_cpc3776`
    
    Notes
    -----
    TODO: Combine this function with :func:`read_cn_cpc3776` for generalization of CPC calls
    
    Examples
    --------
    >>> Campaign = 'AWICIT01B'
    >>> ExpNo = '15'
    >>> experimentliste = sql_query('aida',
            query= "SELECT * FROM experimentliste \

            WHERE Kampagne LIKE '%s'AND ExperimentNr = %s" %(Campaign, ExpNo),
            output_mode='dict')
    >>> cpc3010 = read_cn_cpc3010(Campaign, t_start = experimentliste['ExpStart'],
            t_end = experimentliste['ExpEnde'], verbose = False)
    >>> cpc3010
                             Particles_per_ccm
    Zeitpunkt
    2017-03-30 13:30:00               0.00
    2017-03-30 13:30:01               0.08
    2017-03-30 13:30:02               0.00
    2017-03-30 13:30:03               0.00
    [...]
    """
    from tools_import import sql_query
    
    db_table = Campaign.lower() + '_aida_cpc'

    cpc3010 = sql_query(database='aida',
                        query="SELECT * FROM %s \
                        WHERE Zeitpunkt BETWEEN '%s' AND '%s'"
                        % (db_table, t_start, t_end),
                        df_index_col='Zeitpunkt')

    if verbose:
        print("Imported CPC-3010 data from database")
    
    return cpc3010


# %% Read CPC3776 Data
    
def read_cn_cpc3776(Campaign, t_start, t_end, verbose=False):
    """Read CPC-3776 data from SQL database for defined time interval
    
    Parameters
    ----------
    Campaign : :obj:`str`
        name of campaign
    t_start : :obj:`pd.Timestamp()`
        Start of experiment, get from database table :obj:`aida.experimentliste`
    t_end : :obj:`pd.Timestamp()`
        End of experiment, get from database table :obj:`aida.experimentliste`
    verbose : :obj:`bool`, *optional*
        Print informational statements during function execution
    
    Returns
    -------
    :obj:`pd.DataFrame`
        containing CPC-3776 data in cm⁻³
        
        :obj:`pd.DataFrame.index`
            DatetimeIndex
            
        :obj:`pd.DataFrame.columns` : ['Particles_per_ccm']
            measured CPC concentration in cm⁻³

    See Also
    --------
    :func:`sql_query`, :func:`read_cn_cpc3010`
    
    Examples
    --------
    >>> Campaign = 'AWICIT01B'
    >>> ExpNo = '15'
    >>> experimentliste = sql_query('aida',
            query= "SELECT * FROM experimentliste \

            WHERE Kampagne LIKE '%s'AND ExperimentNr = %s" %(Campaign, ExpNo),
            output_mode='dict')
    >>> cpc3776 = read_cn_cpc3776(Campaign, t_start = experimentliste['ExpStart'],
            t_end = experimentliste['ExpEnde'], verbose = False)
    >>> cpc3776
                             Particles_per_ccm
    Zeitpunkt
    2017-03-30 13:30:00               0.00
    2017-03-30 13:30:01               0.08
    2017-03-30 13:30:02               0.00
    2017-03-30 13:30:03               0.00
    [...]
    """
    from tools_import import sql_query
    
    cpc3776 = sql_query(database='aida',
                        query="SELECT Zeitpunkt, CNAIDA3_A1_ppc FROM %s_aida_sec \
                        WHERE Zeitpunkt BETWEEN '%s' AND '%s'" % (Campaign.lower(), t_start, t_end),
                        df_index_col='Zeitpunkt')
    cpc3776 = cpc3776.rename(columns={'CNAIDA3_A1_ppc': 'cn'})  # in cm⁻³
    
    if verbose:
        print("Imported CPC-3776 data from database")
        
    return cpc3776
