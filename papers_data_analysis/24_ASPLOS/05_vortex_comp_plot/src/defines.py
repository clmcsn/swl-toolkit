"""Defines for Figure 12"""

import pandas as pd

APP_NAMES = ['sgemm', 'knn', 'saxpy', 'sfilter', 'vecadd', 'conv2d']

AREA = pd.DataFrame({
    "clusters": [1, 2, 4, 8],
    "area": [2893271.59/1e6,
             2407695.98*2/1e6,
             2407695.98*4/1e6,
             2407695.98*8/1e6] 
})
