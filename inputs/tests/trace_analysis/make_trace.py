import pandas as pd

df = pd.read_csv("./test_trace.csv")
df.to_feather("./test_trace.feather")