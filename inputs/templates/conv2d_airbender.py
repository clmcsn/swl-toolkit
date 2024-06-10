"Template for conv2d airbender"

from inputs.templates.airbender import AirbenderCmdTemplate, AirbenderDefaults, AirbenderResultFname

conv2dAirbenderCmd = dict(AirbenderCmdTemplate)
conv2dAirbenderCmd.update({
    "app"               : '--app={app} --perf',
    "optimize" : '--args="-O {optimize} ',
    "workload_size_x" : '-x {workload_size_x} ',
    "workload_size_y" : '-y {workload_size_y} ',
    "out_channels" : '-K {out_channels} ',
    "in_channels" : '-C {in_channels} ',
    "filter_size" : '-f {filter_size} ',
    "repeat" : '-r {repeat} ',
    "kernel" : '-k {kernel}"'
})

conv2dAirbenderDefaults = dict(AirbenderDefaults)
conv2dAirbenderDefaults.update({
    "workload_size_x" : "8",
    "workload_size_y" : "8",
    "out_channels" : "4",
    "in_channels" : "4",
    "filter_size" : "3",
    "repeat" : "1",
    "optimize" : "0",
    "kernel" : "conv2d"
})

conv2dAirbenderResFname = dict(AirbenderResultFname)
conv2dAirbenderResFname.update({
    "workload_size_x" : 'x{workload_size_x}',
    "workload_size_y" : 'y{workload_size_y}',
    "out_channels" : 'K{out_channels}',
    "in_channels" : 'Ch{in_channels}',
    "filter_size" : 'f{filter_size}',
    "optimize" : 'O{optimize}',
    "repeat" : 'r{repeat}',
    "kernel" : '{kernel}',
    "groups" : 'hw{groups}',
})
