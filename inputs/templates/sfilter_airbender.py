"Template for sfilter airbender"

from inputs.templates.airbender import AirbenderCmdTemplate, AirbenderDefaults, AirbenderResultFname

sfilterAirbenderCmd = dict(AirbenderCmdTemplate)
sfilterAirbenderCmd.update({
    "workload_size_x" : '--args="-x {workload_size_x} ',
    "workload_size_y" : '-y {workload_size_y} ',
    "optimize" : '-O {optimize} ',
    "repeat" : '-r {repeat} ',
    "kernel" : '-k {kernel}"'
})

sfilterAirbenderDefaults = dict(AirbenderDefaults)
sfilterAirbenderDefaults.update({
    "workload_size_x" : "8",
    "workload_size_y" : "8",
    "repeat" : "1",
    "optimize" : "0",
    "kernel" : "sfilter"
})

sfilterAirbenderResFname = dict(AirbenderResultFname)
sfilterAirbenderResFname.update({
    "workload_size_x" : 'xs{workload_size_x}',
    "workload_size_y" : 'ys{workload_size_y}',
    "optimize" : 'O{optimize}',
    "repeat" : 'r{repeat}',
    "kernel" : '{kernel}',
    "groups" : 'hw{groups}',
})