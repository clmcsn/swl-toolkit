VortexCmdTemplate = {
    "launcher"          : '{launcher}',
    "driver"            : '--driver={driver}',
    "app"               : '--app={app} --perf',
    "debug"             : "--debug",
    "clusters"          : '--clusters={clusters}',
    "cores"             : '--cores={cores}',
    "warps"             : '--warps={warps}',
    "threads"           : '--threads={threads}',
    "l2cache"           : '--l2cache',
    "l3cache"           : '--l3cache'
}

VortexDefaults = {
    "launcher"          : "./ci/blackbox.sh",
    "driver"            : "simx",
    "app"               : "vecadd",
    "clusters"          : "1",
    "cores"             : "1",
    "warps"             : "16",
    "threads"           : "32"
}

VortexResultFname = {
    "ID"                : '{ID}',  
    "app"               : '{app}',
    "driver"            : '{driver}',
    "clusters"          : 'C{clusters}', 
    "cores"             : 'c{cores}',
    "warps"             : 'w{warps}',
    "threads"           : 't{threads}',
    "l2cache"           : "l2",
    "l3cache"           : "l3",
}