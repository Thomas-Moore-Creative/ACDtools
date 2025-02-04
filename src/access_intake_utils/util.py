"""
util.py

This module contains a collection of utility functions for Australian Climate Data (ACD) tools at NCI.
Author = {"name": "Thomas Moore", "affiliation": "CSIRO", "email": "thomas.moore@csiro.au", "orcid": "0000-0003-3930-1946"}
"""

# Standard library imports
import os
import socket

import intake
import xarray as xr
import yaml

# Third-party imports
# import numpy as np
from dask.distributed import Client, LocalCluster
from tabulate import tabulate

# Local application imports (if needed)
# from .my_local_module import my_function


def test_function():
    """
    a test function.

    Parameters:
    None

    Returns:
    True
    """
    print("The ACDtools package is installed and working correctly....  ")
    return True


def detect_compute_platform():
    """
    Brief description of what the function does.

    Parameters:
    param1 (type): Description of the first parameter.
    param2 (type): Description of the second parameter.

    Returns:
    return_type: Description of the return value.
    """
    hostname = socket.gethostname()
    if (
        "gadi" in hostname
    ):  # Adjust this condition to fit your HPC's hostname or unique identifier
        platform_name = "HPC"
    else:
        platform_name = "Laptop"
    print(
        "the platform we are working on is "
        + platform_name
        + " with hostname: "
        + hostname
    )
    return platform_name, hostname


def load_config(config_file="config.yaml"):
    """
    Load a YAML configuration file and return its contents as a Python dictionary.

    Parameters
    ----------
    config_file : str, optional
        The name or relative path of the YAML configuration file to load.
        By default, it looks for 'config.yaml' one directory upstream from the script.

    Returns
    -------
    dict
        A dictionary containing the parsed contents of the YAML configuration file.

    Raises
    ------
    FileNotFoundError
        If the specified YAML file is not found.
    yaml.YAMLError
        If there is an error parsing the YAML file.

    Example
    -------
    >>> config = load_config('my_config.yaml')
    >>> print(config)
    {'n_workers': 4, 'memory_limit': '16GB', ...}
    """

    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), config_file)
    with open(config_path) as file:
        return yaml.safe_load(file)


def start_dask_cluster_from_config(work_type):
    """
    Start a Dask cluster using settings from a YAML configuration file.

    Parameters
    ----------
    work_type : str
        The work type key to extract the Dask cluster settings from the configuration file.

    Returns
    -------
    client : dask.distributed.Client
        The Dask client connected to the cluster.
    cluster : dask.distributed.LocalCluster
        The Dask cluster object.
    """
    # Load the configuration
    config = load_config()

    # Extract the Dask cluster settings for the specified work type
    dask_settings = config.get("dask_cluster", {}).get(work_type, {})

    # Remove None values (optional parameters)
    dask_settings = {k: v for k, v in dask_settings.items() if v != "None"}

    # Start the Dask cluster with the settings by unpacking the dictionary using **
    cluster = LocalCluster(**dask_settings)

    # Connect a client to the cluster
    client = Client(cluster)

    # Show some basic information about the cluster
    print(f"Cluster started with {len(cluster.workers)} workers.")
    print(f"Dashboard available at: {cluster.dashboard_link}")

    # Return both the client and the cluster
    return client, cluster


def report_esm_unique(
    esm_datastore_object,
    drop_list=["path", "time_range", "member_id", "version", "derived_variable_id"],
    keep_list=None,
    header=["Category", "Unique values"],
    return_results=False,
):
    """
    Generate a table of unique values for each category in the esm_datastore_object, optionally returning the data.

    Parameters
    ----------
    esm_datastore_object : object
        An object that has a `.unique()` method to generate unique entries for each category.
    drop_list : list, optional
        A list of keys to exclude from the final dictionary (default is ['path','time_range','member_id','version','derived_variable_id']).
    keep_list : list, optional
        A list of keys to keep in the final dictionary, dropping all others (default is None).
    header : list, optional
        The header for the output table (default is ["Category", "Unique values"]).
    return_results : bool, optional
        Whether to return the unique_dict and table_data (default is False).

    Returns
    -------
    unique_dict : dict or None
        A dictionary of unique values for each category (returned only if `return_results=True`).
    table_data : list or None
        A list of lists formatted for tabulation (returned only if `return_results=True`).
    """
    # Get the unique values from the esm_datastore_object
    unique = esm_datastore_object.unique()

    # Convert to dictionary
    unique_dict = unique.to_dict()

    # Keep only specified keys if keep_list is provided
    if keep_list is not None:
        unique_dict = {
            key: value for key, value in unique_dict.items() if key in keep_list
        }
    # Drop specified keys if drop_list is provided
    elif drop_list is not None:
        unique_dict = {
            key: value for key, value in unique_dict.items() if key not in drop_list
        }

    # Sort each list of values in the dictionary and sort the keys alphabetically
    sorted_unique_dict = {
        key: sorted(value) if isinstance(value, list) else value
        for key, value in sorted(unique_dict.items())
    }

    # Prepare data for tabulation
    table_data = []
    for key, value in sorted_unique_dict.items():
        # If value is a list, join elements by newline; otherwise, use the value as is
        table_data.append([key, "\n".join(value) if isinstance(value, list) else value])

    # Print the table
    print(tabulate(table_data, headers=header, tablefmt="fancy_grid"))

    # Conditionally return results based on the flag
    if return_results:
        return sorted_unique_dict, table_data


def var_name_info(catalog_object, var_name, return_results=False):
    """
    Extracts information about a variable from an intake-esm catalog object.

    Parameters
    ----------
    catalog_object : intake_esm.core.esm_datastore object
        An intake-esm catalog object, likely containing many variables.
    var_name : str
        The name of the variable to extract information for.
    return_results : bool, optional
        Whether to return the variable information (default is False).

    Returns
    -------
    var_info : dict or None
        A dictionary containing the variable information (returned only if `return_results=True`).
    """
    var_ds = xr.open_mfdataset(
        (catalog_object.search(variable_id=var_name).unique().path)[0], chunks={}
    )
    var_info = var_ds[var_name].attrs
    # turn the dictionary into a table for easy reading - adding a header that reports the variable name and name of the catalog object
    print(f"*** Variable: \033[1m{var_name}\033[0m from catalog: {catalog_object} ***")
    table_data = []
    for key, value in var_info.items():
        table_data.append([key, value])
    # Print the table
    max_chars_per_line = 100  # Maximum number of characters per line
    max_words_per_line = 30  # Maximum number of words per line
    table_data_formatted = []
    for key, value in table_data:
        if isinstance(value, str):
            # Split the value into words
            words = value.split()
            # Create a new list to store the formatted lines
            lines = []
            current_line = ""
            for word in words:
                # Check if adding the current word exceeds the maximum characters or words per line
                if (
                    len(current_line) + len(word) + 1 <= max_chars_per_line
                    and len(lines) < max_words_per_line
                ):
                    current_line += word + " "
                else:
                    # Add the current line to the lines list and start a new line with the current word
                    lines.append(current_line.strip())
                    current_line = word + " "
            # Add the last line to the lines list
            lines.append(current_line.strip())
            # Join the lines with newline characters
            formatted_value = "\n".join(lines)
            table_data_formatted.append([key, formatted_value])
        else:
            table_data_formatted.append([key, value])
    print(
        tabulate(
            table_data_formatted, headers=["Attribute", "Value"], tablefmt="fancy_grid"
        )
    )
    # Conditionally return results
    if return_results:
        return var_info


def list_catalog_query_kwargs(esmds):
    """
    List all possible keyword arguments for the **query argument
    in the search method of an intake_esm.core.esm_datastore object.

    Parameters:
        esmds (intake_esm.core.esm_datastore): The ESM datastore object.

    Returns:
        list: A list of column names that can be used as keyword arguments for **query.

    Example usage:
    Assuming `esmds` is your intake_esm.core.esm_datastore object
    query_kwargs = list_query_kwargs(cmip6_fs38_datastore)
    print("Possible query kwargs for search method:", query_kwargs)
    """
    # Get the columns of the dataframe inside the esm_datastore
    query_kwargs = esmds.df.columns.tolist()
    print(
        tabulate(
            [[kw] for kw in query_kwargs],
            headers=["Possible query kwargs"],
            tablefmt="fancy_grid",
        )
    )
    return query_kwargs


def load_cmip6_fs38_datastore():
    """
    Load the CMIP6 FS38 data catalog as an intake-esm datastore object.

    Returns:
    intake_esm.core.esm_datastore: The CMIP6 FS3.8 data catalog as an intake-esm datastore object.
    """

    # Load the CMIP6 FS38 data catalog
    nri_catalog = intake.cat.access_nri
    cmip6_fs38_datastore = nri_catalog.search(name="cmip6_fs38").to_source()
    return cmip6_fs38_datastore


def load_cmip6_CLEX_datastore():
    """
    Load the CMIP6 FS38 data catalog as an intake-esm datastore object using the frozen CLEX NCI catalog.
    Using the 'cmip6' entry of the 'esgf' sub-catalog of the CLEX "nci" catalog provides access to only the latest CMIP6 data.
    See: https://github.com/Thomas-Moore-Creative/ACDtools/issues/2#issuecomment-2510304106

    Returns:
    intake_esm.core.esm_datastore: The CMIP6 FS3.8 CLEX data catalog as an intake-esm datastore object.
    """

    # Load the CMIP6 CLEX FS38 data catalog
    clex_esgf_cat = intake.cat.nci["esgf"]
    clex_cmip6_cat = clex_esgf_cat["cmip6"]
    return clex_cmip6_cat


def show_methods(your_object):
    # Get all attributes of the object
    all_methods = dir(your_object)

    # Filter the list to only show callable methods
    methods_only = []
    for method in all_methods:
        try:
            if callable(getattr(your_object, method)):
                methods_only.append(method)
        except AttributeError:
            pass

    # Print all the methods
    for method in methods_only:
        print(method)


def remove_encoding(DS):
    for var in DS:
        DS[var].encoding = {}

    for coord in DS.coords:
        DS[coord].encoding = {}
    return DS


def align_lon(ds, lon_name_list):
    """
    align_lon
    Returns: ds
    Defaults:
    Author: Thomas Moore (based on Dougie Squire code)
    Date created: 28/01/2020

    Assumptions:
    Dataset = ds
    Use: ds_aligned = align_lon(ds,lon_name_list)
    Limitations:
    """
    for lon_name in lon_name_list:
        ds_attrs = ds[lon_name].attrs
        ds = ds.assign_coords({lon_name: (ds[lon_name] + 360) % 360}).sortby(lon_name)
        ds[lon_name].attrs = ds_attrs
    return ds


def replace_zero_w_nan(data_w_zero):
    data_w_nan = data_w_zero.where(data_w_zero != 0)
    data_w_nan.attrs["post_processing_note"] = "zero values replaced with NaNs"
    return data_w_nan


def convert_longitude_360_2_180(da, lon_name="longitude"):
    """
    Convert longitude values from 0-360 to -180 to 180.

    Parameters:
    - da: xarray.DataArray or xarray.Dataset
        Input data with longitude values in the range 0-360.
    - lon_name: str
        Name of the longitude coordinate.

    Returns:
    - xarray.DataArray or xarray.Dataset
        Data with longitude values converted to -180 to 180.
    """
    da = da.assign_coords(**{lon_name: ((da[lon_name] + 180) % 360) - 180})
    return da.sortby(lon_name)
