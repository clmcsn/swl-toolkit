from inputs.templates.vortex import VortexCmdTemplate, VortexDefaults, VortexResultFname

sgemmCmd = dict(VortexCmdTemplate)
sgemmCmd.update( {
    "workload_size_x"     : '--args="-x {workload_size_x} ',
    "workload_size_y"     : '-y {workload_size_y} ',
    "workload_size_z"     : '-z {workload_size_z} ',
    "local_worksize"    : '-l {local_worksize}"'
})

sgemmDefaults = dict(VortexDefaults)
sgemmDefaults.update( {
    "workload_size_x"     : "4",
    "workload_size_y"     : "4",
    "workload_size_z"     : "4",
    "local_worksize"      : "0"
})

sgemmResFname = dict(VortexResultFname)
sgemmResFname.update({
    "workload_size_x"     : 'xs{workload_size_x}',
    "workload_size_y"     : 'ys{workload_size_y}',
    "workload_size_z"     : 'zs{workload_size_z}',
    "local_worksize"    : 'lw{local_worksize}',
    "groups"            : 'hw{groups}'
})