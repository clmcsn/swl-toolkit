"Template for sgemv airbender"

from inputs.templates.airbender import AirbenderCmdTemplate, AirbenderDefaults, AirbenderResultFname

sgemvAirbenderCmd = dict(AirbenderCmdTemplate)
sgemvAirbenderCmd.update({
    "app"               : '--app={app} --perf',
    "optimize" : '--args="-O {optimize} ',
    "workload_size_x" : '-x {workload_size_x} ',
    "workload_size_y" : '-y {workload_size_y} ',
    "repeat" : '-r {repeat} ',
    "write_back" : '-w {write_back} ',
    "kernel" : '-k {kernel}"'
})

sgemvAirbenderDefaults = dict(AirbenderDefaults)
sgemvAirbenderDefaults.update({
    "workload_size_x" : "8",
    "workload_size_y" : "8",
    "repeat" : "1",
    "optimize" : "0",
    "write_back" : "1",
    "kernel" : "sgemv"
})

sgemvAirbenderResFname = dict(AirbenderResultFname)
sgemvAirbenderResFname.update({
    "workload_size_x" : 'x{workload_size_x}',
    "workload_size_y" : 'y{workload_size_y}',
    "optimize" : 'O{optimize}',
    "repeat" : 'r{repeat}',
    "write_back" : 'w{write_back}',
    "kernel" : '{kernel}',
    "groups" : 'hw{groups}',
})