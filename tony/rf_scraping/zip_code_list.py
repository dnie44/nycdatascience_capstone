import pandas as pd
import numpy as np

df = pd.read_csv('zip_df.csv')
final_df = pd.read_csv('final_redfin.csv')

final_df['zip'] = final_df['ZIP OR POSTAL CODE'].apply(str)
df['ZipCode'] = df['ZipCode'].apply(str)

# ----------- KEEP ONLY first digits of zipcode -----
final_df['zip'] = final_df['zip'].str[:5]
# ----------------------------------------------------

final_df['zip'] = final_df['zip'].replace({'nan':'0'})
df['ZipCode'] = df['ZipCode'].astype(int)
final_df['zip'] = final_df['zip'].astype(int)
df = df.sort_values(by=['ZipCode'], ascending=True)

# ----------- KEEP ONLY VALS > 20000 -----------
final_df = final_df[final_df['zip'] > 20000]
# ----------------------------------------------

# ----------- Make lists of zip codes ----------
zip_list = list(df['ZipCode'])
ripped_zips = list(final_df['zip'].unique())
# ----------------------------------------------

# ----------- Remove Duplicates ----------------
final_df = final_df[final_df.ADDRESS.duplicated() == False]
print(final_df.ADDRESS)
