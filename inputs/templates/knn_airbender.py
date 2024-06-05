"Template for knn airbender"

from inputs.templates.airbender import AirbenderCmdTemplate, AirbenderDefaults, AirbenderResultFname

knnAirbenderCmd = dict(AirbenderCmdTemplate)
knnAirbenderCmd.update({
    "workload_size" : '--args="-n {workload_size} ',
    "optimize" : '-O {optimize} ',
    "repeat" : '-r {repeat} ',
    "kernel" : '-k {kernel}"'
})

knnAirbenderDefaults = dict(AirbenderDefaults)
knnAirbenderDefaults.update({
    "workload_size" : "256",
    "repeat" : "1",
    "optimize" : "0",
    "kernel" : "knn"
})

knnAirbenderResFname = dict(AirbenderResultFname)
knnAirbenderResFname.update({
    "workload_size" : 'n{workload_size}',
    "optimize" : 'O{optimize}',
    "repeat" : 'r{repeat}',
    "kernel" : '{kernel}',
    "groups" : 'hw{groups}',
})