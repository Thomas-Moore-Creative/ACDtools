"""
util.py

This module contains a collection of utility functions for Australian Climate Data (ACD) tools at NCI.
Author = {"name": "Thomas Moore", "affiliation": "CSIRO", "email": "thomas.moore@csiro.au", "orcid": "0000-0003-3930-1946"}
"""
# Standard library imports
import os
import socket
import yaml

# Third-party imports
#import numpy as np
from dask.distributed import Client, LocalCluster
from tabulate import tabulate


# Local application imports (if needed)
#from .my_local_module import my_function


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
    if "gadi" in hostname:  # Adjust this condition to fit your HPC's hostname or unique identifier
        platform_name = 'HPC'
    else:
        platform_name = 'Laptop'
    print('the platform we are working on is '+platform_name+' with hostname: '+hostname)    
    return platform_name, hostname

def load_config(config_file='config.yaml'):
    """
    Load a YAML configuration file and return its contents as a Python dictionary.

    Parameters
    ----------
    config_file : str, optional
        The name or relative path of the YAML configuration file to load. 
        By default, it looks for 'config.yaml' in the same directory as the script.

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
    with open(config_path, 'r') as file:
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
    dask_settings = config.get('dask_cluster', {}).get(work_type, {})
    
    # Remove None values (optional parameters)
    dask_settings = {k: v for k, v in dask_settings.items() if v != 'None'}
    
    # Start the Dask cluster with the settings by unpacking the dictionary using **
    cluster = LocalCluster(**dask_settings)
    
    # Connect a client to the cluster
    client = Client(cluster)

    # Show some basic information about the cluster
    print(f"Cluster started with {len(cluster.workers)} workers.")
    print(f"Dashboard available at: {cluster.dashboard_link}")
    
    # Return both the client and the cluster
    return client, cluster

def report_esm_unique(esm_datastore_object, drop_list=['path','time_range','member_id','version','derived_variable_id'], keep_list=None, header=["Category", "Unique values"], return_results=False):
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
        unique_dict = {key: value for key, value in unique_dict.items() if key in keep_list}
    # Drop specified keys if drop_list is provided
    elif drop_list is not None:
        unique_dict = {key: value for key, value in unique_dict.items() if key not in drop_list}

    # Sort each list of values in the dictionary and sort the keys alphabetically
    sorted_unique_dict = {key: sorted(value) if isinstance(value, list) else value for key, value in sorted(unique_dict.items())}

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

    

