""" Constants used across all scripts in this directory. """

DF_FNAME = 'dataframe.feather'
RES_DIR = 'output/'
PLOT_DIR = 'output/plots/'
FIG_NAME = 'figure'

# #####################################################################
# Merge is needed for obtaining results 2xrepetitions vs 1xrepetition
COMMON_MERGE_ON = [
    'app',
    'driver',
    'clusters',
    'threads',
    'warps',
    'cores',
    'dcache_ports',
    'ssr_credits',
    'dcache_banks',
    'dcache_size',
    'l2cache',
    'optimize',
    'kernel'
]

MERGE_ON = {
    "vecadd":  COMMON_MERGE_ON + ['workload_size'],
    "sgemm":   COMMON_MERGE_ON + ['workload_size_x',
                                  'workload_size_y',
                                  'workload_size_z'],
    "sfilter": COMMON_MERGE_ON + ['workload_size_x',
                                  'workload_size_y'],
    "saxpy":   COMMON_MERGE_ON + ['workload_size'],
    "knn":     COMMON_MERGE_ON + ['workload_size'],
    "conv2d":  COMMON_MERGE_ON + ['workload_size_x',
                                  'workload_size_y',
                                  'out_channels',
                                  'in_channels'],
    "sgemv":   COMMON_MERGE_ON + ['workload_size_x',
                                  'workload_size_y']
}

# #####################################################################

BASE_KERNELS = {
    "vecadd": "vecadd-base",
    "sgemm":  "sgemm",
    "sfilter": "sfilter",
    "saxpy": "saxpy",
    "knn": "knn-asm",
    "conv2d": "conv2d-asm",
    "sgemv": "sgemv"
}
