"""Defines for Figure 12"""

import pandas as pd

APP_NAMES = ['sgemm', 'knn', 'saxpy', 'sfilter']

AREA = pd.DataFrame({
    "dcache_ports": [1, 2, 3],
    "area": [2407695.98/1e6,
             2893271.59/1e6,
             3924759.33/1e6]
})
