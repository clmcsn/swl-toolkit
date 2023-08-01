from inputs.templates.vortex import VortexCmdTemplate, VortexDefaults, VortexResultFname

baddCmd = dict(VortexCmdTemplate)
baddCmd.update( {
    "workload_size_x"     : '--args="-x {workload_size_x} ',
    "workload_size_y"     : '-y {workload_size_y} ',
    "local_worksize"    : '-l {local_worksize}"'
})

baddDefaults = dict(VortexDefaults)
baddDefaults.update( {
    "workload_size_x"     : "4",
    "workload_size_y"     : "4",
    "local_worksize"      : "0"
})

baddResFname = dict(VortexResultFname)
baddResFname.update({
    "workload_size_x"     : 'xs{workload_size_x}',
    "workload_size_y"     : 'ys{workload_size_y}',
    "local_worksize"    : 'lw{local_worksize}',
    "groups"            : 'hw{groups}'
})