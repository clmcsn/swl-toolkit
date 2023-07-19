from collections import namedtuple

CondorVortexCmdTemplate = "condor_send  --type command \
                                        --jobname {app}.{oID} \
                                        --nice 1 \
                                        --cpus {cpus} \
                                        --distribution fedora rocky \
                                        --logdirs {output_dir} \
                                        --stream 0 \
                                        --command '{launcher_path}/tools/singularity/vortex-run.sh  -f={conf_file} \
                                                                                                    -c={cpus} \
                                                                                                    -o={output_dir} \
                                                                                                    -i={oID}' \
                                        --avoid grape,aristoteles"

# vecadd ---------------------------------------------------------------------
from inputs.templates.vecadd import vecaddCmd, vecaddDefaults, vecaddResFname
# ----------------------------------------------------------------------------
# gcn_synth_bench ------------------------------------------------------------
from inputs.templates.gcn_synth_bench import gcn_synth_benchCmd, gcn_synth_benchDefaults, gcn_synth_benchResFname
# ----------------------------------------------------------------------------
# sgemm ---------------------------------------------------------------------
from inputs.templates.sgemm import sgemmCmd, sgemmDefaults, sgemmResFname

Map = namedtuple('Map', ['CMD', 'DICT', 'STR'])
templateDict = {
    "vecadd" : Map(CMD=[CondorVortexCmdTemplate, vecaddCmd], DICT=vecaddDefaults, STR=vecaddResFname),
    "gcnSynth" : Map(CMD=[CondorVortexCmdTemplate, gcn_synth_benchCmd], DICT=gcn_synth_benchDefaults, STR=gcn_synth_benchResFname),
    "sgemm" : Map(CMD=[CondorVortexCmdTemplate, sgemmCmd], DICT=sgemmDefaults, STR=sgemmResFname)}