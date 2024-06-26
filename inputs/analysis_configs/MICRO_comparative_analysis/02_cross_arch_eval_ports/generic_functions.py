import pandas as pd

import specific_functions as sf

merge_list = ['threads', 'warps', 'dcache_ports','clusters', 'cores', 'app']

def gen_df(path, benchmark):
    df = pd.read_feather(path+"/dataframe.feather")
    df_r1 = df[df['repeat'] == 1].reset_index(drop=True)
    df_r2 = df[df['repeat'] == 2].reset_index(drop=True)

    df = pd.merge(df_r1, df_r2, on=merge_list+sf.s_merge_list[benchmark], suffixes=('_r1', '_r2'))
    df['cycles'] = df['cycles_r1'] + df['cycles_r2']
    df['instrs'] = df['instrs_r1'] + df['instrs_r2']
    df['ssr_stalls'] = df['ssr_stalls_r1'] + df['ssr_stalls_r2']
    df['dcache_bank_stalls'] = df['dcache_bank_stalls_r1'] + df['dcache_bank_stalls_r2']
    df['dcache_bank_utilization'] = (df['dcache_bank_utilization_r1'] + df['dcache_bank_utilization_r2'])/2

    if(benchmark in sf.ws_red_list):
        df['workload_size'] = df['workload_size_x'] * df['workload_size_y']

    df = df.sort_values(by=['dcache_ports', 'workload_size']).reset_index(drop=True)

    df['cycles'] = df['cycles'].mask(df['cycles'] <= 0).ffill()
    df['ssr_stalls'] = df['ssr_stalls'].mask(df['ssr_stalls'] <= 0).ffill()

    #remove _airbender form app name
    df['app'] = df['app'].str.replace('-airbender', '')

    return df

def make_summary_df(df):
    sum_df = pd.DataFrame()
    for t in df['dcache_ports'].unique():
        area = sf.area[sf.area['dcache_ports'] == t]['area'].values[0]
        sum_df = pd.concat([pd.DataFrame({
                "app" :                     [df['app'].unique()[0]],
                "dcache_ports" :                 [t],
                "cycles" :                  [df[df['dcache_ports'] == t]['cycles'].mean()],
                "cycle_area" :              [df[df['dcache_ports'] == t]['cycles'].mean()*area],
                "ssr_stalls" :              [df[df['dcache_ports'] == t]['ssr_stalls'].mean()],
                "dcache_bank_stalls" :      [df[df['dcache_ports'] == t]['dcache_bank_stalls'].mean()],
                "dcache_bank_utilization" : [df[df['dcache_ports'] == t]['dcache_bank_utilization'].mean()]
        }), sum_df])
    #normalize over maximum
    sum_df['cycles'] = sum_df['cycles']/sum_df['cycles'].max()
    sum_df['ssr_stalls'] = sum_df['ssr_stalls']/sum_df['ssr_stalls'].max()
    sum_df['dcache_bank_stalls'] = sum_df['dcache_bank_stalls']/sum_df['dcache_bank_stalls'].max()
    sum_df['dcache_bank_utilization'] = 100 - sum_df['dcache_bank_utilization']
    sum_df['cycle_area'] = sum_df['cycle_area']/sum_df['cycle_area'].max()
    return sum_df