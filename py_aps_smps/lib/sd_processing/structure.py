#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 28 11:37:14 2021

Analyze and redefine the structure of size distributions.

@author: tobias.schorr@kit.edu
"""
import pandas as pd
import numpy as np

from py_aps_smps.lib.sd_processing.content import calc_dXdlogd_from_dX


def get_channel_resolution(data, x_axis='dpes'):
    """Get average channel resolution (bins per decade) along a given axis."""
    return len(data) / (np.log10(data[x_axis].max()) - np.log10(data[x_axis].min()))


def calc_bin_boundaries(bin_mean_diameter, channel_resolution):
    """Calculate lower and upper bin boundaries for a given mean diameter and channel resolution
    This calculation was derived using the expression 'dNdlogD = dN * channel_res'."""
    bin_lower_boundary = 2 * bin_mean_diameter / (10**(1 / channel_resolution) + 1)
    bin_upper_boundary = 2 * bin_mean_diameter / (10**(-1 / channel_resolution) + 1)
    return (bin_lower_boundary, bin_upper_boundary)


def combine_SMPS_APS_sd(sd_aps, sd_smps, merge_overlap=True, interpolate_gap=True, verbose=False):
    """Combine APS and SMPS size distributions.
    
    Parameters
    ----------
    sd_aps : pd.DataFrame()
        Pass a size distribution for SMPS.
    sd_smps : pd.DataFrame()
        Pass a size distribution for APS.
    
    Returns
    -------
    pd.DataFrame
        Contains the merged size distribution of APS and SMPS.
    """
    
    sd_aps._is_copy, sd_smps._is_copy = False, False  # Debugging, silence SettingWithCopyWarning, see https://stackoverflow.com/questions/38809796/pandas-still-getting-settingwithcopywarning-even-after-using-loc/38810015#38810015
    sd_aps.loc[:, 'flag'] = 'aps'
    sd_smps.loc[:, 'flag'] = 'smps'
    
    sd_combined = pd.concat([sd_smps, sd_aps]).reset_index(drop=True)
    
    # check if there is an overlap in aps and smps
    if (max(sd_smps['dpes_upper']) > min(sd_aps['dpes_lower'])):
        flag_overlap = True
        if verbose:
            print("There is an overlap in APS and SMPS spectra.")
    else:
        flag_overlap = False
            
    # check if there is a gap between aps and smps:
    if (max(sd_smps['dpes_upper']) < min(sd_aps['dpes_lower'])):
        flag_gap = True
        if verbose:
            print("There is a gap between APS and SMPS spectra.")
    else:
        flag_gap = False
    
    # interpolate gap between aps and smps
    if interpolate_gap and flag_gap:
        if verbose:
            print("Interpolate gap between APS and SMPS spectra.")
        
        def get_interpol_resolution(sd_smps, sd_aps):
            """Get averaged bin resolution (bins per decade) from smps and aps"""
            bins_per_decade_interpol = (get_channel_resolution(sd_smps) + get_channel_resolution(sd_aps)) // 2
            return bins_per_decade_interpol
        
        def get_bin_boundaries_in_interval(x_start, x_end, res):
            """Create bin boundaries with certain resolution (bins per decade)"""
            decades_in_x_range = np.log10(x_end) - np.log10(x_start)
            bin_num = round(res * decades_in_x_range)
            
            bin_bound_lower = np.logspace(start=np.log10(x_start),
                                          stop=np.log10(x_end),
                                          num=bin_num,
                                          endpoint=False)
            
            bin_bound_upper = np.append(bin_bound_lower[1:], x_end)
            return (bin_bound_lower, bin_bound_upper)
        
        def interpolate_dndlogd_gap(sd_gapped, edge_average_window=3):
            """Interpolate dndlogd in gap bins"""
            edge_bin_min_idx = sd_gapped[(sd_gapped.flag == 'smps')].dpes_upper.idxmax()
            edge_bin_max_idx = sd_gapped[(sd_gapped.flag == 'aps')].dpes_lower.idxmin()
            
            edge_bin_min_dndlogd_0 = sd_gapped.loc[edge_bin_min_idx, 'dndlogd']
            edge_bin_max_dndlogd_0 = sd_gapped.loc[edge_bin_max_idx, 'dndlogd']
            
            edge_bin_min_dndlogd_avg = sd_gapped.loc[edge_bin_min_idx - edge_average_window: edge_bin_min_idx].dndlogd.mean()
            edge_bin_max_dndlogd_avg = sd_gapped.loc[edge_bin_max_idx: edge_bin_max_idx + edge_average_window].dndlogd.mean()
            
            # slice gap with edge bins
            gap_with_edges = sd_gapped.loc[edge_bin_min_idx: edge_bin_max_idx]
            gap_with_edges._is_copy = False  # silence SettingWithCopyWarning
            gap_with_edges.iloc[0, gap_with_edges.columns.get_loc('dndlogd')] = edge_bin_min_dndlogd_avg
            gap_with_edges.iloc[-1, gap_with_edges.columns.get_loc('dndlogd')] = edge_bin_max_dndlogd_avg
            
            # interpolate gap with averaged/smoothed edges
            sd_interpolated_dndlogd = sd_gapped.copy()
            sd_interpolated_dndlogd.loc[edge_bin_min_idx: edge_bin_max_idx, 'dndlogd'] = gap_with_edges.set_index('dpes')['dndlogd'].interpolate(method='index').to_numpy()
            
            # restore original edge values
            sd_interpolated_dndlogd.loc[edge_bin_min_idx, 'dndlogd'] = edge_bin_min_dndlogd_0
            sd_interpolated_dndlogd.loc[edge_bin_max_idx, 'dndlogd'] = edge_bin_max_dndlogd_0
                        
            return sd_interpolated_dndlogd
        
        # fill gap with new bin grid
        (interpol_dpes_range_start, interpol_dpes_range_end) = (sd_smps.dpes_upper.max(), sd_aps.dpes_lower.min())
        interpol_resolution = get_interpol_resolution(sd_smps, sd_aps)
        (interpol_dpes_bins_lower, interpol_dpes_bins_upper) = get_bin_boundaries_in_interval(interpol_dpes_range_start,
                                                                                              interpol_dpes_range_end,
                                                                                              interpol_resolution)
        interpol_dpes_bins_center = (interpol_dpes_bins_lower + interpol_dpes_bins_upper) / 2
        
        interpolated_bins = pd.DataFrame({'flag': 'interpolated',
                                          'dpes': interpol_dpes_bins_center,
                                          'dpes_lower': interpol_dpes_bins_lower,
                                          'dpes_upper': interpol_dpes_bins_upper})
        sd_combined = pd.concat([sd_combined, interpolated_bins], ignore_index=True)
        sd_combined = sd_combined.sort_values('dpes').reset_index(drop=True)
        
        # apply interpolation on dndlogd over gap
        sd_combined = interpolate_dndlogd_gap(sd_combined, edge_average_window=3)
        sd_combined['dn'] = sd_combined['dndlogd'] * (np.log10(sd_combined['dpes_upper']) - np.log10(sd_combined['dpes_lower']))
    
    # merge overlapping bins
    if merge_overlap and flag_overlap:
        if verbose:
            print("Merge overlap in APS and SMPS spectra.")
        # in overlap range merge smaller binned smps data into aps bins
        smps_mask_overlap = sd_combined.where(sd_combined.flag == 'smps').dpes_upper > min(sd_combined[sd_combined.flag == 'aps'].dpes_lower)  # identify overlapping smps bins
        aps_mask_overlap = sd_combined.where(sd_combined.flag == 'aps').dpes_lower < max(sd_combined[sd_combined.flag == 'smps'].dpes_upper)
        
        aps_overlap = sd_combined[aps_mask_overlap]
        smps_overlap = sd_combined[smps_mask_overlap]
        
        merged_indices = list()
        for s, smps_bin in enumerate(smps_overlap.itertuples()):
            smps_bin_width = smps_bin.dpes_upper - smps_bin.dpes_lower
            
            # edge case, first smps bin to overlap with smalest aps bin
            if smps_bin.dpes_lower < min(aps_overlap.dpes_lower):
                aps_bin = aps_overlap[(smps_bin.dpes_upper > aps_overlap.dpes_lower)]
                assert len(aps_bin) == 1
                aps_bin = aps_bin.iloc[0]
                aps_bin_width = aps_bin.dpes_upper - aps_bin.dpes_lower
                
                # identify widths of bin overlap
                smps_only_width = aps_bin.dpes_lower - smps_bin.dpes_lower
                overlap_width = smps_bin.dpes_upper - aps_bin.dpes_lower
                aps_only_width = aps_bin.dpes_upper - smps_bin.dpes_upper
                
                # modify aps bin, by merging with smps bin
                sd_combined.loc[aps_bin.name, 'dpes_lower'] = smps_bin.dpes_lower
                sd_combined.loc[aps_bin.name, 'dpes_upper'] = aps_bin.dpes_upper
                sd_combined.loc[aps_bin.name, 'dpes'] = (smps_bin.dpes_lower + aps_bin.dpes_upper) / 2
                sd_combined.loc[aps_bin.name, 'dn'] = smps_bin.dn * (smps_only_width / smps_bin_width)
                sd_combined.loc[aps_bin.name, 'dn'] += aps_bin.dn * (aps_only_width / aps_bin_width)
                sd_combined.loc[aps_bin.name, 'dn'] += (0.5 * smps_bin.dn * overlap_width / smps_bin_width
                                                        + 0.5 * aps_bin.dn * overlap_width / aps_bin_width)
                sd_combined.loc[aps_bin.name, 'flag'] = 'merged'
                
                # merged_indices.append(aps_bin.name)
                
            # standard case
            elif (smps_bin.dpes_lower > min(aps_overlap.dpes_lower)) & (smps_bin.dpes_upper < max(aps_overlap.dpes_upper)):
                aps_bins = aps_overlap[(smps_bin.dpes_lower < aps_overlap.dpes_upper) & (smps_bin.dpes_upper > aps_overlap.dpes_lower)]
                
                # subcase 1: smps bin is embraced by one aps bin
                if len(aps_bins) == 1:
                    aps_bin = aps_bins.iloc[0]
                    aps_bin_width = aps_bin.dpes_upper - aps_bin.dpes_lower
                    
                    # combined_bin_idx = sd_combined.index.max() + 1
                    sd_combined.loc[aps_bin.name, 'dpes_lower'] = aps_bin.dpes_lower
                    sd_combined.loc[aps_bin.name, 'dpes_upper'] = aps_bin.dpes_upper
                    sd_combined.loc[aps_bin.name, 'dpes'] = aps_bin.dpes
                    sd_combined.loc[aps_bin.name, 'dn'] = aps_bin.dn * (aps_bin_width - smps_bin_width) / aps_bin_width
                    sd_combined.loc[aps_bin.name, 'dn'] += (aps_bin.dn * (smps_bin_width / aps_bin_width) + smps_bin.dn) / 2
                    sd_combined.loc[aps_bin.name, 'flag'] = 'merged'
                    
                    # merged_indices.append(aps_bin.name)
                    
                # subcase 2: smps bin overlaps the boundary between two aps bins
                elif len(aps_bins) == 2:
                    # merge smps bin with first of both aps bins
                    aps_bin = aps_bins.iloc[0]
                    aps_bin_width = aps_bin.dpes_upper - aps_bin.dpes_lower
                    
                    aps_only_width = smps_bin.dpes_lower - aps_bin.dpes_lower
                    overlap_width = aps_bin.dpes_upper - smps_bin.dpes_lower
                    
                    # combined_bin_idx = sd_combined.index.max() + 1
                    sd_combined.loc[aps_bin.name, 'dpes_lower'] = aps_bin.dpes_lower
                    sd_combined.loc[aps_bin.name, 'dpes_upper'] = aps_bin.dpes_upper
                    sd_combined.loc[aps_bin.name, 'dpes'] = aps_bin.dpes
                    sd_combined.loc[aps_bin.name, 'dn'] = aps_bin.dn * (aps_only_width / aps_bin_width)
                    sd_combined.loc[aps_bin.name, 'dn'] += (aps_bin.dn * (overlap_width / aps_bin_width) + smps_bin.dn * (overlap_width / smps_bin_width)) / 2
                    sd_combined.loc[aps_bin.name, 'flag'] = 'merged'
                        
                    # merged_indices.append(aps_bin.name)
                    
                    # merge smps bin with second of both aps bins
                    aps_bin = aps_bins.iloc[1]
                    aps_bin_width = aps_bin.dpes_upper - aps_bin.dpes_lower
                    
                    aps_only_width = aps_bin.dpes_upper - smps_bin.dpes_upper
                    overlap_width = smps_bin.dpes_upper - aps_bin.dpes_lower
                    
                    # combined_bin_idx = sd_combined.index.max() + 1
                    sd_combined.loc[aps_bin.name, 'dpes_lower'] = aps_bin.dpes_lower
                    sd_combined.loc[aps_bin.name, 'dpes_upper'] = aps_bin.dpes_upper
                    sd_combined.loc[aps_bin.name, 'dpes'] = aps_bin.dpes
                    sd_combined.loc[aps_bin.name, 'dn'] = aps_bin.dn * (aps_only_width / aps_bin_width)
                    sd_combined.loc[aps_bin.name, 'dn'] += (aps_bin.dn * (overlap_width / aps_bin_width) + smps_bin.dn * (overlap_width / smps_bin_width)) / 2
                    sd_combined.loc[aps_bin.name, 'flag'] = 'merged'
                    
                    # merged_indices.append(aps_bin.name)
            
            merged_indices.append(smps_bin.Index)
        
        sd_combined = sd_combined.drop(merged_indices)
        sd_combined = sd_combined.sort_values(['dpes']).reset_index(drop=True)
    
    modified_bins = (sd_combined.flag != 'smps') & (sd_combined.flag != 'aps')
    sd_combined.loc[modified_bins, 'dndlogd'] = calc_dXdlogd_from_dX(sd_combined.loc[modified_bins, 'dn'],
                                                                     bins_lower=sd_combined.loc[modified_bins, 'dpes_lower'],
                                                                     bins_upper=sd_combined.loc[modified_bins, 'dpes_upper'])
    return sd_combined
