import pandas as pd
import numpy as np


df = pd.read_excel('data/process_data/fits for maps.xlsx', sheet_name="eta1_fit (7)", header=0) 
#df = pd.read_excel('data/process_data/fits for maps.xlsx', sheet_name="pr1_fit", header=0) 

# --- Step 1: Filter unreliable points ---
df_filtered = df[df['COUNT'] >= 20].copy()

# --- Step 2: Normalize metrics ---
df_filtered['R2_n'] = (df_filtered['R2'] - df_filtered['R2'].min()) / (df_filtered['R2'].max() - df_filtered['R2'].min())

df_filtered['RMSE_n'] = 1 - (df_filtered['RMSE'] - df_filtered['RMSE'].min()) / (df_filtered['RMSE'].max() - df_filtered['RMSE'].min())

df_filtered['MAPE_n'] = 1 - (df_filtered['MAPE'] - df_filtered['MAPE'].min()) / (df_filtered['MAPE'].max() - df_filtered['MAPE'].min())

df_filtered['COUNT_n'] = (df_filtered['COUNT'] - df_filtered['COUNT'].min()) / (df_filtered['COUNT'].max() - df_filtered['COUNT'].min())

# --- Step 3: Define weights ---
w_R2 = 0.5
w_RMSE = 0.4
w_MAPE = 0
w_COUNT = 0.1

# --- Step 4: Compute score ---
df_filtered['score'] = (
    w_R2 * df_filtered['R2_n'] +
    w_RMSE * df_filtered['RMSE_n'] +
    w_MAPE * df_filtered['MAPE_n'] +
    w_COUNT * df_filtered['COUNT_n']
)

# --- Step 5: Select best speedline ---
best = df_filtered.loc[df_filtered['score'].idxmax()]

print("Best speedlines:")
top10 = df_filtered.sort_values(by='score', ascending=False).head(10)
print(top10.sort_values(by='X', ascending=True)['X'].tolist())