# -*- coding: utf-8 -*-
"""
Functions for acquiring and cleaning data  Baseball Hall of Fame Voting data
from baseball-reference.com

Project Luther, Metis Data Science Immersive

Author: Will Hetfield
"""

from collections import defaultdict
import pandas as pd
import numpy as np

def create_dataframe_dict ():
    """
    Scrape baseball-reference.com Hall of Fame Voting pages and create
    a dictionary with keys of year and values that year's dataframe
    
    Args
    
    None
    
    Return
    hf_df_dict: Dictionary of hall of fame vote results, key is int year
    """
    hf_df_dict = {}

    for year in range (1966,2019):
        url =  'https://www.baseball-reference.com/awards/hof_%s.shtml' % year
        
        #multiple tables may be on page due to Veterans Committee Vote
        #First table, index zero is what applies
        tables = pd.read_html(url)
        hf_df_dict[year] = format_bbref_table(tables[0], year)
        
    #Not all years prior to 1966 was their voting 
        
    odd_years = [1964,1962,1960, 1958, 1956, 1955, 1954, 1953, 1952, 1951, 
                 1950, 1949, 1948, 1947, 1946, 1945, 1942, 1939, 1938, 
                 1937, 1936]  
    
    for year in odd_years:
        url =  'https://www.baseball-reference.com/awards/hof_%s.shtml' % year
        table = pd.read_html(url)
        hf_df_dict[year] = format_bbref_table(table[0], year)
        
    return hf_df_dict
    

def format_bbref_table (raw_table, year):
    """
    Take raw pandas table from Baseball Reference Hall of Fame pages
    and clean for analysis
    
    Args
    
    raw_table: DataFrame with MultiIndex
    year: str, year of vote 
    
    Return 
    
    finished_table: Formatted DataFrame
    """
    
    #get rid of the multilevel index
    raw_table.columns = raw_table.columns.get_level_values(1)
    
    
    #want only first year on ballot and no pitchers
    #if positional summary string starts with 1, then pitcher
    mask = (raw_table['YoB'] == '1st') & \
    (raw_table['Pos\xa0Summary'].str.lstrip('*').str.startswith('1') == False) & \
    (raw_table['WAR'] > 10)
    
    
    finished_table = raw_table[mask]
    
    #add column for year of vote
    finished_table.loc[ : , 'Year_of_Vote'] = np.array([year] * len (finished_table))    
    return finished_table



def create_analysis_df (hf_df_dict):
    """
    Take dict of dataframes and combine for single dataframe
    
    Args
    hf_df_dict: dict of dataframes returned from create_dataframe_dict function
    
    Return  hof_df dataframe to perform analysis on 
    
    """

    hof_df = pd.concat(hf_df_dict.values())
    
    #get rid of pitcher statistic columns
    hof_df.dropna(axis=1, how='all', inplace=True)
    
    #all relevant columns were floats except what we are predicting!
    hof_df['%vote'] = hof_df['%vote'].str.rstrip('%').astype('float64')
    
    return hof_df



def check_columns(bbdf_dict):
    """
    Check to see if every year has same number of columns
    
    Args
    bbdf_dict: Dictionary of dataframes for each year's first time ballot
    
    
    Return
    
    row_dict = return dict with count for # of columns in each dataframe  
    """
    
    
    row_dict = defaultdict(int)
    for df in bbdf_dict.values():
        row_dict[df.shape[1]] += 1
        
    return row_dict