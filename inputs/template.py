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
# ----------------------------------------------------------------------------
# sfilter ---------------------------------------------------------------------
from inputs.templates.sfilter import sfilterCmd, sfilterDefaults, sfilterResFname
# ----------------------------------------------------------------------------
# nearn ---------------------------------------------------------------------
from inputs.templates.nearn import nearnCmd, nearnDefaults, nearnResFname
# ----------------------------------------------------------------------------
# badd ---------------------------------------------------------------------
from inputs.templates.badd import baddCmd, baddDefaults, baddResFname
# ----------------------------------------------------------------------------
# vecadd-swift ---------------------------------------------------------------------
from inputs.templates.vecadd_airbender import vecaddAirbenderCmd, vecaddAirbenderDefaults, vecaddAirbenderResFname
# ----------------------------------------------------------------------------
# sgemm-swift ---------------------------------------------------------------------
from inputs.templates.sgemm_airbender import sgemmAirbenderCmd, sgemmAirbenderDefaults, sgemmAirbenderResFname
# ----------------------------------------------------------------------------
# aggr-swift ---------------------------------------------------------------------
from inputs.templates.aggr_airbender import aggrAirbenderCmd, aggrAirbenderDefaults, aggrAirbenderResFname
# ----------------------------------------------------------------------------
# saxpy-swift ---------------------------------------------------------------------
from inputs.templates.saxpy_airbender import saxpyAirbenderCmd, saxpyAirbenderDefaults, saxpyAirbenderResFname
# ----------------------------------------------------------------------------
# knn-swift ---------------------------------------------------------------------
from inputs.templates.knn_airbender import knnAirbenderCmd, knnAirbenderDefaults, knnAirbenderResFname
# ----------------------------------------------------------------------------

Map = namedtuple('Map', ['CMD', 'DICT', 'STR'])
templateDict = {
    "vecadd" : Map(CMD=[CondorVortexCmdTemplate, vecaddCmd], DICT=vecaddDefaults, STR=vecaddResFname),
    "saxpy"  : Map(CMD=[CondorVortexCmdTemplate, vecaddCmd], DICT=vecaddDefaults, STR=vecaddResFname),
    "relu"   : Map(CMD=[CondorVortexCmdTemplate, vecaddCmd], DICT=vecaddDefaults, STR=vecaddResFname),
    "gcnSynth" : Map(CMD=[CondorVortexCmdTemplate, gcn_synth_benchCmd], DICT=gcn_synth_benchDefaults, STR=gcn_synth_benchResFname),
    "sgemm" : Map(CMD=[CondorVortexCmdTemplate, sgemmCmd], DICT=sgemmDefaults, STR=sgemmResFname),
    "igemm" : Map(CMD=[CondorVortexCmdTemplate, sgemmCmd], DICT=sgemmDefaults, STR=sgemmResFname),
    "sfilter" : Map(CMD=[CondorVortexCmdTemplate, sfilterCmd], DICT=sfilterDefaults, STR=sfilterResFname),
    "badd" : Map(CMD=[CondorVortexCmdTemplate, baddCmd], DICT=baddDefaults, STR=baddResFname),
    "nearn" : Map(CMD=[CondorVortexCmdTemplate, nearnCmd], DICT=nearnDefaults, STR=nearnResFname),
    "vecadd-airbender" : Map(CMD=[CondorVortexCmdTemplate, vecaddAirbenderCmd], DICT=vecaddAirbenderDefaults, STR=vecaddAirbenderResFname),
    "sgemm-airbender" : Map(CMD=[CondorVortexCmdTemplate, sgemmAirbenderCmd], DICT=sgemmAirbenderDefaults, STR=sgemmAirbenderResFname),
    "saxpy-airbender" : Map(CMD=[CondorVortexCmdTemplate, vecaddAirbenderCmd], DICT=vecaddAirbenderDefaults, STR=vecaddAirbenderResFname),
    "knn-airbender" : Map(CMD=[CondorVortexCmdTemplate, knnAirbenderCmd], DICT=knnAirbenderDefaults, STR=knnAirbenderResFname),
    "aggr-airbender" : Map(CMD=[CondorVortexCmdTemplate, aggrAirbenderCmd], DICT=aggrAirbenderDefaults, STR=aggrAirbenderResFname)}