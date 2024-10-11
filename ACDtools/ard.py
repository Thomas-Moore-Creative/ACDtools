"""
ard.py

This module contains a collection of functions for analysis-ready-data (ARD) operations on climate data at NCI.
Author = {"name": "Thomas Moore", "affiliation": "CSIRO", "email": "thomas.moore@csiro.au", "orcid": "0000-0003-3930-1946"}
"""
# Standard library imports
# import os


# Third-party imports
#import numpy as np
import intake_esm
import xarray as xr
import numpy as np

# Local application imports (if needed)
#from .my_local_module import my_function

def load_ACCESS_ESM_ensemble(catalog_search):
    """
    Load the ACCESS-ESM ensemble data from an esm_datastore.

    Parameters
    ----------
    catalog_search : intake_esm.core.esm_datastore object -  This will come from filtering an intake catalog that contains the ACCESS-ESM ensemble data.

    Returns
    -------
    ds_sorted : xarray.Dataset - The concatenated dataset with the ACCESS-ESM ensemble data labelled and sorted based on the member names.

    """
    # check if the catalog_search is an esm_datastore object, specifically intake_esm.core.esm_datastore
    if not isinstance(catalog_search, intake_esm.core.esm_datastore):
        raise TypeError("catalog_search must be an instance of intake_esm.core.esm_datastore!!! Did catalog_search come from filtering an intake catalog?")
    # check if the catalog_search contains ACCESS-ESM ensemble data
    # is there one and only one source_id in the catalog_search?
    if len(catalog_search.df['source_id'].unique()) != 1:
        raise ValueError("The catalog_search must contain only one source_id!!!")
    # is the source_id ACCESS-ESM?
    if not any(source_id.startswith('ACCESS-ESM') for source_id in catalog_search.df['source_id'].unique()):
        raise ValueError("The catalog_search must contain ACCESS-ESM data!!!")
    # check that there is at least 2 ensembles in the catalog_search
    if len(catalog_search.df['member_id'].unique()) < 2:
        raise ValueError("The catalog_search must contain at least 2 ensembles!!!")
    # Get the dictionary of datasets and the corresponding keys (member names)
    dataset_dict = catalog_search.to_dataset_dict(progressbar=False)
    # check that the member names are unique
    if len(dataset_dict.keys()) != len(set([key.split('.')[5] for key in dataset_dict.keys()])):
        raise ValueError("The member names are not unique!!!")
    # Extract the member names from the keys
    member_names = [key.split('.')[5] for key in dataset_dict.keys()]  # Extract 'r9i1p1f1' as the member name from each key
    # check that the member names are in the format 'r[integer 1-99]i[integer 1-99]p[integer 1-99]f[integer 1-99]'
    if not all(member_name.startswith('r') and \
               member_name[1:].split('i')[0].isdigit() and \
               member_name[1:].split('i')[1].split('p')[0].isdigit() and \
               member_name[1:].split('i')[1].split('p')[1].split('f')[0].isdigit() and \
               member_name[1:].split('i')[1].split('p')[1].split('f')[1].isdigit() \
               for member_name in member_names):
        raise ValueError("The member names are not in the format 'r[integer 1-99]i[integer 1-99]p[integer 1-99]f[integer 1-99]'!!!")
    # Concatenate the datasets along the 'member' dimension and retain the member names
    ds = xr.concat(
    dataset_dict.values(), 
    dim=xr.DataArray(member_names, dims="member", name="member"))
    # Extract the numeric part from each member name and sort based on it
    sorted_member_indices = np.argsort([int(member[1:].split('i')[0]) for member in ds['member'].values])
    # Reorder the dataset based on the sorted member indices
    ds_sorted = ds.isel(member=sorted_member_indices)
    return ds_sorted
