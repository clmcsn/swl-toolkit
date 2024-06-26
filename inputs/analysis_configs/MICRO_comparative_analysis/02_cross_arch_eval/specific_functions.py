import pandas as pd

s_merge_list = {
    "conv2d"    : ['workload_size_x', 'workload_size_y', 'out_channels', 'in_channels'],
    "knn"       : ['workload_size'],
    "saxpy"     : ['workload_size'],
    "vecadd"    : ['workload_size'],
    "sfilter"   : ['workload_size_x', 'workload_size_y'],
    "sgemm"     : ['workload_size_x', 'workload_size_y', 'workload_size_z']
}

area = pd.DataFrame({
    "threads"      : [4, 8, 16, 32],
    "area"         : [  1094920.92/1e6 ,   1656579.87 /1e6,   2893271.59 /1e6 ,   5562554.52 /1e6]
})

ws_red_list = ['conv2d', 'sfilter', 'sgemm']