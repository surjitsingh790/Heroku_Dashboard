from DEF_MFS_MVP_Storage import df_list
import pandas as pd

class Statistical_Analysis:

    def statistical_characteristics(self):
        df = pd.concat(df_list)
        print("Shape:\n",df.shape)
        print("Statistical Characteristics:\n",df.describe())

stat_analy = Statistical_Analysis()
stat_analy.statistical_characteristics()

