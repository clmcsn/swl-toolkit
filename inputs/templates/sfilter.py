from inputs.templates.vortex import VortexCmdTemplate, VortexDefaults, VortexResultFname

#TODO filter is applied to a square matrix (picture), maybe add x, y dimension

sfilterCmd = dict(VortexCmdTemplate)
sfilterCmd.update( {
    "workload_size"     : '--args="-n {workload_size} ',
    "local_worksize"    : '-b {local_worksize}"'
})

sfilterDefaults = dict(VortexDefaults)
sfilterDefaults.update( {
    "workload_size"     : "256",
    "local_worksize"    : "16"
})

sfilterResFname = dict(VortexResultFname)
sfilterResFname.update({
    "workload_size"     : 'ws{workload_size}',
    "local_worksize"    : 'lw{local_worksize}',
    "groups"            : 'hw{groups}'
})