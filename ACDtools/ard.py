"""
ard.py

This module contains a collection of functions for analysis-ready-data (ARD) operations on climate data at NCI.
Author = {"name": "Thomas Moore", "affiliation": "CSIRO", "email": "thomas.moore@csiro.au", "orcid": "0000-0003-3930-1946"}
"""

def load_ACCESS_ESM_ensemble():
    """
    Load the ACCESS-ESM ensemble data from the esm_datastore.

    Parameters
    ----------
    None

    Returns
    -------
    esm_datastore : object
        The esm_datastore object containing the ACCESS-ESM ensemble data.
    """
    # Get the dictionary of datasets and the corresponding keys (member names)
    dataset_dict = search.to_dataset_dict(progressbar=False)
    member_names = [key.split('.')[5] for key in dataset_dict.keys()]  # Extract 'r9i1p1f1' as the member name from each key

    # Concatenate the datasets along the 'member' dimension and retain the member names
    ds2 = xr.concat(
    dataset_dict.values(), 
    dim=xr.DataArray(member_names, dims="member", name="member"))
    # Extract the numeric part from each member name and sort based on it
    sorted_member_indices = np.argsort([int(member[1:].split('i')[0]) for member in ds2['member'].values])

    # Reorder the dataset based on the sorted member indices
    ds_sorted = ds2.isel(member=sorted_member_indices)
    return ds_sorted
