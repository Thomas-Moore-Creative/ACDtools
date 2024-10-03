"""
util.py

This module contains a collection of utility functions for Australian Climate Data (ACD) tools at NCI.
"""
# Standard library imports
import os
import socket

# Third-party imports
#import numpy as np
from dask.distributed import Client, LocalCluster


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



def start_dask_cluster(n_workers=None, threads_per_worker=None, memory_limit=None):
    """
    Starts a local Dask cluster. If no parameters are provided, LocalCluster defaults are used.

    Parameters:
    n_workers (int or None): Number of workers (None uses LocalCluster's default).
    threads_per_worker (int or None): Number of threads per worker (None uses LocalCluster's default).
    memory_limit (str or None): Memory limit per worker (None uses LocalCluster's default).

    Returns:
    client (Client): Dask distributed client connected to the cluster.
    """
    # Create a LocalCluster, passing parameters only if they are not None
    cluster_kwargs = {}
    if n_workers is not None:
        cluster_kwargs['n_workers'] = n_workers
    if threads_per_worker is not None:
        cluster_kwargs['threads_per_worker'] = threads_per_worker
    if memory_limit is not None:
        cluster_kwargs['memory_limit'] = memory_limit

    # Create the cluster with the provided or default parameters
    cluster = LocalCluster(**cluster_kwargs)

    # Connect a client to the cluster
    client = Client(cluster)
    
    # Optionally print out cluster information
    print("Dask cluster started:")
    print(cluster)
    
    return client





