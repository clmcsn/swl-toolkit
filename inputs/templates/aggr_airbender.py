"Template for aggr airbender"

from inputs.templates.vortex import VortexCmdTemplate, VortexDefaults, VortexResultFname

aggrAirbenderCmd = dict(VortexCmdTemplate)
aggrAirbenderCmd.update({
    "app"               : '--app={app} --perf',
    "nodes" : '--args="-n {nodes} ',
    "vlen" : '-v {vlen} ',
    "dataset" : '-d {dataset} ',
    "optimize" : '-O {optimize} ',
    "repeat" : '-r {repeat} ',
    "kernel" : '-k {kernel}"'
})

aggrAirbenderDefaults = dict(VortexDefaults)
aggrAirbenderDefaults.update({
    "nodes" : "64",
    "vlen" : "4",
    "dataset" : "cora",
    "repeat" : "1",
    "optimize" : "0",
    "kernel" : "aggr"
})

aggrAirbenderResFname = dict(VortexResultFname)
aggrAirbenderResFname.update({
    "nodes" : 'n{nodes}',
    "vlen" : 'v{vlen}',
    "dataset" : '{dataset}',
    "optimize" : 'O{optimize}',
    "repeat" : 'r{repeat}',
    "kernel" : '{kernel}',
    "groups" : 'hw{groups}',
})
