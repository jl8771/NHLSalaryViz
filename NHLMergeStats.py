import os
import pandas as pd

os.chdir('stagedcsv/')
filenames = [_ for _ in os.listdir() if _.endswith('.csv')]
dfs = []
for file in filenames:
    temp_df = pd.read_csv(file)
    dfs.append(temp_df)
    
output = pd.concat(dfs)

#Filter invalid results that remain
output = output[output['salary'] != -111]
output = output.dropna()

output.to_csv('combinedstats.csv', index=False)