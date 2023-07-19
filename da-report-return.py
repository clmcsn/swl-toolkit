import os
import pandas as pd
import yaml
import numpy as np
import math

import util.parsers.da as parsers

parser = parsers.DataAnalysisParserClass()
print("Loading dataframe...")
DF_NAME = parser.args.res_path + "dataframe.feather"
df = pd.read_feather(DF_NAME)

# ----------------- Check for faulty reports -----------------
bad_df = df[df.isnull().any(axis=1)]
if bad_df.empty: print("No faulty reports found.")
else: 
    l = len(bad_df)
    print("WARNING: Faulty reports found. (" + str(l) + ")")

# ----------------- Extracting columns name -----------------
exp_dict = yaml.load(open(parser.args.res_path + "experiments.dump.yml", "r"), Loader=yaml.FullLoader)
keys_list = list(exp_dict.keys())
if "OuterParams" in keys_list:
    oKeys = list(exp_dict["OuterParams"].keys())
    iKeys = list(exp_dict["InnerParams"].keys())
else:
    raise Exception("OuterParams not found in experiments.dump.yml")

with open(parser.args.res_path + "return_report.log", "w") as log_file:
    log_file.write("REPORTING oIDs -----------------"+"\n")
    for oID in sorted(list(df["oID"].unique())):
        ID_string = "oID: " + str(oID)
        for oK in oKeys:
            ID_string += " " + oK + ": " + str(df.loc[df["oID"]==oID][oK].unique()[0])
        log_file.write(ID_string + "\n")
        zero_ret = len(df.loc[(df["oID"]==oID) & (df["Return"]==0)])
        total    = len(df.loc[df["oID"]==oID])
        log_file.write("------> Zero return: " + str(zero_ret) + "/" + str(total) + " (" + str(np.round(zero_ret/total*100, decimals=1)) + "%)\n")
    log_file.write("--------------------------------------------------"+"\n")

    log_file.write("REPORTING HW params -----------------"+"\n")
    for oK in oKeys:
        log_file.write(oK + ": " + str(df[oK].unique()) + "\n")
        for v in sorted(list(df[oK].unique())):
            log_file.write("------> " + oK + ": " + str(v) + "\n")
            zero_ret = len(df.loc[(df[oK]==v) & (df["Return"]==0)])
            total    = len(df.loc[df[oK]==v])
            log_file.write("------> Zero return: " + str(zero_ret) + "/" + str(total) + " (" + str(np.round(zero_ret/total*100, decimals=1)) + "%)\n")
    log_file.write("--------------------------------------------------"+"\n")

    log_file.write("REPORTING SW params -----------------"+"\n")
    for iK in iKeys:
        log_file.write(iK + ": " + str(df[iK].unique()) + "\n")
        for v in sorted(list(df[iK].unique())):
            log_file.write("------> " + iK + ": " + str(v) + "\n")
            zero_ret = len(df.loc[(df[iK]==v) & (df["Return"]==0)])
            total    = len(df.loc[df[iK]==v])
            log_file.write("------> Zero return: " + str(zero_ret) + "/" + str(total) + " (" + str(np.round(zero_ret/total*100, decimals=1)) + "%)\n")
    log_file.write("--------------------------------------------------"+"\n")

