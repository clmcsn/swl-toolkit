"Template for vecadd airbender"

from inputs.templates.vortex import VortexCmdTemplate, VortexDefaults, VortexResultFname

vecaddAirbenderCmd = dict(VortexCmdTemplate)
vecaddAirbenderCmd.update({
    "app"               : '--app={app} --perf',
    "workload_size" : '--args="-n {workload_size} ',
    "optimize" : '-O {optimize} ',
    "repeat" : '-r {repeat} ',
    "kernel" : '-k {kernel}"'
})

vecaddAirbenderDefaults = dict(VortexDefaults)
vecaddAirbenderDefaults.update({
    "workload_size" : "256",
    "repeat" : "1",
    "optimize" : "0",
    "kernel" : "vecadd"
})

vecaddAirbenderResFname = dict(VortexResultFname)
vecaddAirbenderResFname.update({
    "workload_size" : 'n{workload_size}',
    "optimize" : 'O{optimize}',
    "repeat" : 'r{repeat}',
    "kernel" : '{kernel}',
    "groups" : 'hw{groups}',
})
