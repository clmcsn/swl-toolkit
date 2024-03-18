"Template for vortex airbender"

from inputs.templates.vortex import VortexCmdTemplate, VortexDefaults, VortexResultFname
from collections import OrderedDict

AirbenderCmdTemplate = OrderedDict({
    "ssr_credits"       : 'CONFIGS="-DNUM_SSR_CREDITS={ssr_credits}',
    "dcache_size"       : '-DDCACHE_SIZE={dcache_size}',
    "dcache_banks"      : '-DDCACHE_NUM_BANKS={dcache_banks}"'
})
AirbenderCmdTemplate.update(VortexCmdTemplate)
AirbenderCmdTemplate.update({
    "dcache_ports"      : '--dcache_ports={dcache_ports}',
})

AirbenderDefaults = dict(VortexDefaults)
AirbenderDefaults.update({
    "ssr_credits"       : "4",
    "dcache_banks"      : "16",
    "dcache_size"       : "16384",
    "dcache_ports"      : "1"
})

AirbenderResultFname = dict(VortexResultFname)
AirbenderResultFname.update({
    "ssr_credits"       : 'sc{ssr_credits}',
    "dcache_banks"      : 'b{dcache_banks}',
    "dcache_ports"      : 'p{dcache_ports}',
    "dcache_size"       : 'ds{dcache_size}',
})

