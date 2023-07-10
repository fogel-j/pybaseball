import warnings
from typing import Optional

import pandas as pd

from .datasources.fangraphs import fg_starting_pitching_data, fg_relief_pitching_data


# This is just a pass through for the new, more configurable function
starting_pitching_stats = fg_starting_pitching_data
relief_pitching_stats = fg_relief_pitching_data