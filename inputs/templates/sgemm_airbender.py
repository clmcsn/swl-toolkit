"Template for sgemm airbender"

from inputs.templates.vortex import VortexCmdTemplate, VortexDefaults, VortexResultFname

sgemmAirbenderCmd = dict(VortexCmdTemplate)
sgemmAirbenderCmd.update({
    "app"               : '--app={app} --perf',
    "optimize" : '--args="-O {optimize} ',
    "workload_size_x" : '-x {workload_size_x} ',
    "workload_size_y" : '-y {workload_size_y} ',
    "workload_size_z" : '-z {workload_size_z} ',
    "repeat" : '-r {repeat} ',
    "kernel" : '-k {kernel}"'
})

sgemmAirbenderDefaults = dict(VortexDefaults)
sgemmAirbenderDefaults.update({
    "workload_size_x" : "8",
    "workload_size_y" : "8",
    "workload_size_z" : "8",
    "repeat" : "1",
    "optimize" : "0",
    "kernel" : "sgemm"
})

sgemmAirbenderResFname = dict(VortexResultFname)
sgemmAirbenderResFname.update({
    "workload_size_x" : 'x{workload_size_x}',
    "workload_size_y" : 'y{workload_size_y}',
    "workload_size_z" : 'z{workload_size_z}',
    "optimize" : 'O{optimize}',
    "repeat" : 'r{repeat}',
    "kernel" : '{kernel}',
    "groups" : 'hw{groups}',
})