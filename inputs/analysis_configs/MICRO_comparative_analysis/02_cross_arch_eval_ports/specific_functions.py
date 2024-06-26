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
    "dcache_ports"         : [1,2,3],
    "area"         : [  2407695.98/1e6, 
                        2893271.59/1e6, 
                        3924759.33/1e6] 
})

ws_red_list = ['conv2d', 'sfilter', 'sgemm']