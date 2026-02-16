'''
This code simulates the heatpump cycle for Maneheim over an year
'''
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import CoolProp.CoolProp as CP
from MVV_GKM_simulation import simulation_loop
from tespy.tools.characteristics import CharLine,CharMap
from tqdm import tqdm 


def optimization():
    n_runs = 10

    for i in tqdm(range(n_runs)):

        print(f"\n--- Optimization Run {i+1} ---")
        simulation_loop()



if __name__ == "__main__":
    optimization()