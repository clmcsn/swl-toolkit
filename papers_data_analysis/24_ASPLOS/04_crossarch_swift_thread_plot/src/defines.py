"""Defines for Figure 12"""

import pandas as pd

APP_NAMES = ['sgemm', 'knn', 'saxpy', 'sfilter', 'vecadd', 'conv2d']

AREA = pd.DataFrame({
    "threads": [4, 8, 16, 32],
    "area": [1094920.92/1e6,
             1656579.87/1e6,
             2893271.59/1e6,
             5562554.52/1e6]
})
