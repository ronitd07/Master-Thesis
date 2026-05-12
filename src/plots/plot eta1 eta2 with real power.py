import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv(r'h:\Master Thesis\gitlab\ma_ronit\compressor_results1.csv')
df['datetime'] = pd.to_datetime(df['datetime'])
#df = df.sort_values('datetime').reset_index(drop=True)

fig, ax = plt.subplots(figsize=(12, 5))


ax.scatter(df['datetime'], df['Comp1 eff'],label='Compressor 1')
ax.scatter(df['datetime'], df['Comp2 eff'],label='Compressor 2')
ax.scatter(df['datetime'], df['Comp2 eff'],label='Compressor 2')



ax.set_ylabel('Efficiency')
ax.set_xlabel('Date time')
ax.set_title('Isentropic efficiency using real power as input')
ax.legend()
ax.grid(True, axis='y')

plt.tight_layout()
plt.show()