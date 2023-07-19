from inputs.templates.vortex import VortexCmdTemplate, VortexDefaults, VortexResultFname

vecaddCmd = dict(VortexCmdTemplate)
vecaddCmd.update( {
    "workload_size"     : '--args="-n {workload_size} ',
    "local_worksize"    : '-b {local_worksize}"'
})

vecaddDefaults = dict(VortexDefaults)
vecaddDefaults.update( {
    "workload_size"     : "256",
    "local_worksize"    : "16"
})

vecaddResFname = dict(VortexResultFname)
vecaddResFname.update({
    "workload_size"     : 'ws{workload_size}',
    "local_worksize"    : 'lw{local_worksize}',
    "groups"            : 'hw{groups}'
})