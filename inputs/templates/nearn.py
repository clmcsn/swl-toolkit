from inputs.templates.vortex import VortexCmdTemplate, VortexDefaults, VortexResultFname

nearnCmd = dict(VortexCmdTemplate)
nearnCmd.update( {
    "local_worksize"    : '--args="-b {local_worksize}"'
})

nearnDefaults = dict(VortexDefaults)
nearnDefaults.update( {
    "local_worksize"    : "16"
})

nearnResFname = dict(VortexResultFname)
nearnResFname.update({
    "local_worksize"    : 'lw{local_worksize}',
    "groups"            : 'hw{groups}'
})