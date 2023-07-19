from inputs.templates.vortex import VortexCmdTemplate, VortexDefaults, VortexResultFname

gcn_synth_benchCmd = dict(VortexCmdTemplate)
gcn_synth_benchCmd.update({
    "benchmark"     : '--args="-b {benchmark} ',
    "dataset"       :         '-d {dataset}',
    "layer"        :         '-l {layer}',
    "hidden_size"   :         '-n {hidden_size}',
    "batch_size"    :         '-i {batch_size}',
    "local_worksize":         '-w {local_worksize}"'
})

gcn_synth_benchDefaults = dict(VortexDefaults)
gcn_synth_benchDefaults.update({ 
    "benchmark"     : "AGGR",
    "dataset"       : "cora",
    "layer"        : "INTER",
    "hidden_size"   : "16",
    "batch_size"    : "-1",
    "local_worksize": "0"
})

gcn_synth_benchResFname = dict(VortexResultFname)
gcn_synth_benchResFname.update({
    "benchmark"     : '{benchmark}',
    "dataset"       : '{dataset}',
    "layer"        : '{layer}',
    "hidden_size"   : 'hs{hidden_size}',
    "batch_size"    : 'bs{batch_size}',
    "local_worksize": 'lw{local_worksize}'
})