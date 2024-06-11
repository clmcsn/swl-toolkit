"Template for saxpy airbender"

from inputs.templates.airbender import AirbenderCmdTemplate, AirbenderDefaults, AirbenderResultFname

saxpyAirbenderCmd = dict(AirbenderCmdTemplate)
saxpyAirbenderCmd.update({
    "workload_size" : '--args="-n {workload_size} ',
    "optimize" : '-O {optimize} ',
    "repeat" : '-r {repeat} ',
    "write_back" : '-w {write_back} ',
    "kernel" : '-k {kernel}"'
})

saxpyAirbenderDefaults = dict(AirbenderDefaults)
saxpyAirbenderDefaults.update({
    "workload_size" : "256",
    "repeat" : "1",
    "optimize" : "0",
    "write_back" : "1",
    "kernel" : "saxpy"
})

saxpyAirbenderResFname = dict(AirbenderResultFname)
saxpyAirbenderResFname.update({
    "workload_size" : 'n{workload_size}',
    "optimize" : 'O{optimize}',
    "repeat" : 'r{repeat}',
    "write_back" : 'w{write_back}',
    "kernel" : '{kernel}',
    "groups" : 'hw{groups}',
})