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
    "clusters"         : [1,2,4,8],
    "area"         : [  2893271.59 /1e6, 
                        2407695.98*2/1e6, 
                        2407695.98*4/1e6,
                        2407695.98*8/1e6] 
})

ws_red_list = ['conv2d', 'sfilter', 'sgemm']