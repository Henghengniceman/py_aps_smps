#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 28 11:30:22 2021

Define distribution functions

@author: tobias.schorr@kit.edu
"""
import numpy as np


def lognormal(x, mu, sig, tot):
    """Create a lognormal distribution with median mu and geometric standard
    deviation sig, both on the natural scale.
    
    Reference:
        Limpert, E.; Stahel, W. A.; Abbt, M. (2001). "Log-normal
        distributions across the sciences: Keys and clues".
        BioScience. 51 (5): 341–352."""
    return ((tot / (np.log10(sig) * np.sqrt(2 * np.pi)))
            * np.exp(-((np.log10(x / mu))**2) / (2 * np.log10(sig)**2)))


def bilognormal(x, mu1, sig1, N1, mu2, sig2, N2):
    """Create a bilognormal distribution.
    It is simply a superposition of two lognormal functions."""
    return ((N1 / (np.log10(sig1) * np.sqrt(2 * np.pi)))
            * np.exp(-((np.log10(x / mu1))**2) / (2 * np.log10(sig1)**2))
            + (N2 / (np.log10(sig2) * np.sqrt(2 * np.pi)))
            * np.exp(-((np.log10(x / mu2))**2) / (2 * np.log10(sig2)**2)))
