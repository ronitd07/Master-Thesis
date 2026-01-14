'''
Plot characteristic lines
'''
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import numpy as np
import fhgcd_plots.main as fhgCD


x = [0.49, 0.55782, 0.62612, 0.69418, 0.76132, 0.82682,
		      0.89, 0.95016, 1, 1.04326, 1.07753, 1.10916,
		      1.13795, 1.16365, 1.18604, 1.2049, 1.22]
y = [0.68, 0.72066, 0.76025, 0.79742, 0.83083, 0.85914,
		      0.881, 0.89507, 1.0, 0.89733, 0.88913, 0.87496,
		      0.85435, 0.82687, 0.79205, 0.64944, 0.69859]
'''

x=np.array([0.70, 0.85, 1.00, 1.10, 1.25])
y=np.array([0.88, 0.96, 1.00, 0.97, 0.90])
'''
plt.plot(x,y,'x',linestyle='-',)
plt.xlabel('x')
plt.ylabel('y')
plt.grid(True)

plt.tight_layout()
plt.show()
