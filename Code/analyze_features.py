from pandas import Timestamp
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
#plt.set_style()

from itertools import zip_longest
def grouper(iterable, n, fillvalue=None):
    "Collect data into fixed-length chunks or blocks"
    # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * n
    return zip_longest(*args, fillvalue=fillvalue)


stream1 = pd.read_csv("feature_importances_stream_no_leverage.csv")
stream2 = pd.read_csv("feature_importances_stream_yes_leverage.csv")

lake1 = pd.read_csv("feature_importances_lake_no_leverage.csv")
lake2 = pd.read_csv("feature_importances_lake_yes_leverage.csv")


df1 = pd.concat([lake1, stream1])
df2 = pd.concat([stream2, lake2])

df1 = df1.drop([df1.columns[0]], axis=1)
df2 = df2.drop([df2.columns[0]], axis=1)

df1["data_type"] = [x.replace("_normal","") for x in df1["data_type"]]
df1["leverage"] = ["non_leverage"] * len(df1["data_type"])
df2["leverage"] = ["leverage"] * len(df2["data_type"])

df2["nutrient"] = [x.replace("lev_","") for x in df2["nutrient"]]
df2["data_type"] = [x.replace("_leverage","") for x in df2["data_type"]]

print(df1)
print(df2)

df = pd.concat([df1, df2])
df.to_csv("all_data_wide.csv")
df = df.melt(id_vars=["data_type","model_type","r^2","times_better_than_random", "nutrient", "leverage"], var_name="feature", value_name="importance")
df.to_csv("all_data_long.csv")
