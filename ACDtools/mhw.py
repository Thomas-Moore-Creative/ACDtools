"""
mhw.py

This module attempts to build xarray-ready dask-enabled functions to:
- implement the Marine Heatwave (MHW) definition of Hobday et al. (2016, Prog Ocean)
- expand functionality and purposes
- including severity filter from Richaud, B., Hu, X., Darmaraki, S., Fennel, K., Lu, Y., & Oliver, E. C. J. (2024). Drivers of marine heatwaves in the Arctic Ocean. Journal of Geophysical Research: Oceans, 129, e2023JC020324. https://doi.org/10.1029/2023JC020324
- better enable parallel processing of large datasets across the board

CREDITS:
- Eric Oliver, https://ecjoliver.weebly.com & original python code https://github.com/ecjoliver/marineHeatWaves
- Richaud, B., Hu, X., Darmaraki, S., Fennel, K., Lu, Y., & Oliver, E. C. J. (2024). Drivers of marine heatwaves in the Arctic Ocean. Journal of Geophysical Research: Oceans, 129, e2023JC020324. https://doi.org/10.1029/2023JC020324

Author = {"name": "Thomas Moore", "affiliation": "CSIRO", "email": "thomas.moore@csiro.au", "orcid": "0000-0003-3930-1946"}

"""
# Standard library imports
import os
import datetime


# Third-party imports
import numpy as np
import xarray as xr

# Local application imports (if needed)
#from .my_local_module import my_function
