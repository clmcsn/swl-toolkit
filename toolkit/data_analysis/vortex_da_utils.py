import os
import pandas as pd

from typing import OrderedDict

fname_info = {
    'clusters'          : 'C',
    'cores'             : 'c',
    'warps'             : 'w',
    'threads'           : 't',
    'l2cache'           : 'l2',
    'l3cache'           : 'l3',
    'driver'            : 2,
    'app'               : 1,
    'ID'                : 0,
    'workload_size'     : 'ws',
    'local_worksize'    : 'lw',
    'workload'          : 'W'
}

#TODO merge this with templates.py
fname_info_gcnSynth = dict(fname_info)
fname_info_gcnSynth.update({
    'workload'      : 8,
    'dataset'       : 9,
    'layer'         : 10,
    'hidden_size'   : 'hs',
    'batch_size'    : 'bs',
})

fname_info_dict = {'gcnSynth' : fname_info_gcnSynth}

def get_key_from_value(d,v):
    try:
        return list(d.keys())[list(d.values()).index(v)]
    except:
        print("Error: value {} not found in dictionary".format(v))
        return None

def get_key(string):
    r = ""
    for c in string:
        if c.isalpha(): r+=c
        else:   return r

def gen_dict_from_fname(string, ref_dict):
    l = string.split("_")
    d = {}
    for i,v in enumerate(l):
        if i in ref_dict.values(): #if index I get my value right away
            k = get_key_from_value(ref_dict,i)
            d[k]=v
        elif v in ref_dict.values():
            k = get_key_from_value(ref_dict,v)
            d[k] = True
        else:
            r = get_key(v)
            k = get_key_from_value(ref_dict,r)
            d[k] = int(v.replace(r,''))
    return d

log_info = ['instrs',
            'cycles', 
            'IPC', 
            'ibuffer_stalls',
            'ssr_stalls',
            'ssr_prefetch_stalls',
            'scoreboard_stalls', 
            'alu_unit_stalls', 
            'lsu_unit_stalls', 
            'csr_unit_stalls', 
            'fpu_unit_stalls', 
            'gpu_unit_stalls', 
            'loads', 
            'stores', 
            'branches', 
            'icache_reads', 
            'icache_read_misses', 
            'icache_read_hit_ratio', 
            'dcache_reads', 
            'dcache_writes', 
            'dcache_read_misses', 
            'dcache_read_hit_ratio', 
            'dcache_write_misses', 
            'dcache_write_hit_ratio', 
            'dcache_bank_stalls', 
            'dcache_bank_utilization', 
            'dcache_mshr_stalls', 
            'smem_reads', 
            'smem_writes', 
            'smem_bank_stalls', 
            'smem_bank_utilization', 
            'memory_requests', 
            'reads', 
            'writes', 
            'memory_average_latency']

space_log_info = [" ".join(x.split("_")) for x in log_info]

def digit(string):
    if "." in string:   return float(string)
    else:               return int(string)

def remove_c_from_s(c,string):
    s = string
    for d in c:
        s = s.replace(d,'')
    return s

def gen_dict_from_logfile(path):
    d = dict((k,None) for k in log_info)
    with open(path, "r") as log:
        for l in log:
            l = l.strip()
            if "PERF:" in l:
                if " core" in l: continue #Not implemented yet
                else:
                    split_l = l.split(" ")[1:] #I remove the PERF [1:]
                    k = []
                    k_prec = []
                    #TODO percenteages don't work here
                    for sl in (remove_c_from_s("(),",ssl) for ssl in split_l): #I clean the string from (),
                        k.append(sl.split('=')[0])
                        if "=" in sl:
                            k = '_'.join(k)
                            if sl.split('=')[1][-1] == '%': #percentage cases
                                k = "_".join(k_prec.split("_")[:-1]) + "_" + k
                                if k in log_info: d[k] = digit(sl.split("=")[1][:-1]) #I remove the % from the string
                                else: print("Unknown key found:{}".format(k))
                            else:
                                if k in log_info: d[k] = digit(sl.split("=")[1])
                                else: print("Unknown key found:{}".format(k))
                            k_prec = k
                            k=[]
    return d

def gen_dict_from_log(path):
    fname = path.split("/")[-1]
    dl = gen_dict_from_logfile(path)
    dl["ID"] = int(fname.split("_")[fname_info["ID"]])
    return dl

def gen_df_from_log(path):
    return pd.DataFrame(gen_dict_from_log(path),index=[0])

def vortex_fault_handler(path):
    with open("fauty.txt","a") as f:
        f.write(path+"\n")
    os.remove(path)

aggregated_cols_dict = OrderedDict({   'instrs':                   'sum',      
                                        'cycles':                   'sum', 
                                        'ibuffer_stalls':           'sum', 
                                        'scoreboard_stalls':        'sum', 
                                        'alu_unit_stalls':          'sum', 
                                        'lsu_unit_stalls':          'sum', 
                                        'csr_unit_stalls':          'sum', 
                                        'fpu_unit_stalls':          'sum', 
                                        'gpu_unit_stalls':          'sum',
                                        'loads':                    'sum', 
                                        'stores':                   'sum', 
                                        'branches':                 'sum',
                                        'icache_reads':             'sum', 
                                        'icache_read_misses':       'sum', 
                                        'dcache_reads':             'sum',
                                        'dcache_writes':            'sum', 
                                        'dcache_read_misses':       'sum', 
                                        'dcache_write_misses':      'sum',
                                        'dcache_bank_stalls':       'sum', 
                                        'dcache_mshr_stalls':       'sum', 
                                        'smem_reads':               'sum', 
                                        'smem_writes':              'sum', 
                                        'smem_bank_stalls':         'sum', 
                                        'memory_requests':          'sum', 
                                        'reads':                    'sum', 
                                        'writes':                   'sum'})

derived_cols_dict = OrderedDict({   'IPC':                      lambda x: x['instrs']/x['cycles'],
                                    'icache_read_hit_ratio':    lambda x: 1 - x['icache_read_misses']/x['icache_reads'],
                                    'dcache_read_hit_ratio':    lambda x: 1 - x['dcache_read_misses']/x['dcache_reads'],
                                    'dcache_write_hit_ratio':   lambda x: 1 - x['dcache_write_misses']/x['dcache_writes'],
                                    'dcache_bank_utilization':  lambda x: 1 - x['dcache_bank_stalls']/x['dcache_reads'], #Not sure about this
                                    'smem_bank_utilization':    lambda x: 1 - x['smem_bank_stalls']/x['smem_reads']}) #Not sure about this})