"Template for vecadd airbender"

from inputs.templates.airbender import AirbenderCmdTemplate, AirbenderDefaults, AirbenderResultFname

vecaddAirbenderCmd = dict(AirbenderCmdTemplate)
vecaddAirbenderCmd.update({
    "workload_size" : '--args="-n {workload_size} ',
    "optimize" : '-O {optimize} ',
    "repeat" : '-r {repeat} ',
    "write_back" : '-w {write_back} ',
    "kernel" : '-k {kernel}"'
})

vecaddAirbenderDefaults = dict(AirbenderDefaults)
vecaddAirbenderDefaults.update({
    "workload_size" : "256",
    "repeat" : "1",
    "write_back" : "1",
    "optimize" : "0",
    "kernel" : "vecadd"
})

vecaddAirbenderResFname = dict(AirbenderResultFname)
vecaddAirbenderResFname.update({
    "workload_size" : 'n{workload_size}',
    "optimize" : 'O{optimize}',
    "repeat" : 'r{repeat}',
    "write_back" : 'w{write_back}',
    "kernel" : '{kernel}',
    "groups" : 'hw{groups}',
})
