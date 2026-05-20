'''
Create characteristic line for compressor stage 1 and 2
'''
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import numpy as np
import json
from pathlib import Path
#import fhgcd_plots.main as fhgCD

df = pd.read_csv(r'results\compressor_results1.csv',sep=',') # Real compressor power simulation results

m1_design = 116.8445877958067
pr1_design = 5.096810782032815
e1_design = 0.8
m2_design = 177.7294186674552
pr2_design = 2.8615636254804384
e2_design = 0.75

def eta1_charline():

        #fhgCD.set_matplotlib_style("darkgrid", "official")
        fig, ax = plt.subplots(figsize=(10, 4))

        x = df['Comp1 m']/m1_design
        y = df['Comp1 eff']/e1_design
        ax.scatter(x, y,
                label='eta_s_char compressor 1',color='tab:blue')


        coeffs2 = np.polyfit(x, y,2)
        print("2nd-degree coefficients:", coeffs2)

        x_fit = np.linspace(min(x), max(x), 10)

        y_fit = np.polyval(coeffs2,x_fit)

        ax.plot(x_fit,y_fit,color='tab:red',label = 'Fitted 2nd degree polynomial',linewidth=3)
        #ax.set_xlim(0,1.2)

        ax.set_xlabel('Normalized mass flow x')
        ax.set_ylabel('Normalized efficiecny y')
        ax.legend()
        ax.grid(True)
        plt.savefig("eta_charline comp1.png", dpi=300, bbox_inches="tight")

        return x_fit.tolist(), y_fit.tolist()

def eta2_charline():
        fig1, ax = plt.subplots(figsize=(10, 4))

        X = df['Comp2 m']/m2_design
        Y = df['Comp2 eff']/e2_design

        ax.scatter(X, Y,
                label='eta_s_char compressor 2',color='tab:blue')

        Coeffs2 = np.polyfit(X, Y,2)
        print("2nd-degree coefficients:", Coeffs2)

        X_fit = np.linspace(min(X), max(X), 10)

        Y_fit = np.polyval(Coeffs2,X_fit)

        ax.plot(X_fit,Y_fit,color='tab:red',label = 'Fitted 2nd degree polynomial',linewidth=3)
        #ax.set_xlim(0,1.2)


        ax.set_xlabel('Normalized mass flow x')
        ax.set_ylabel('Normalized efficiecny y')
        ax.legend()
        ax.grid(True)
        plt.savefig("eta_charline comp2.png", dpi=300, bbox_inches="tight")

        plt.tight_layout()
        plt.show()

        return X_fit.tolist(), Y_fit.tolist()

def create_compressor_line():
        x1,y1 = eta1_charline()
        x2,y2 = eta2_charline()

        # Update charline data
        charline_data = {
                "line_eta1": {"x": x1, "y": y1},
                "line_eta2": {"x": x2, "y": y2},
        }
        path = Path.home() / ".tespy" / "data" / "char_lines.json"

        with open(path, "w") as f:
                json.dump(charline_data,f,indent=1, cls=SmartEncoder)     

class SmartEncoder(json.JSONEncoder):
    def iterencode(self, obj, _one_shot=False):
        for chunk in super().iterencode(obj, _one_shot=_one_shot):
            yield chunk

    def encode(self, obj):
        if isinstance(obj, list):
            # Keep small lists in one line
            if len(obj) <= 5 and all(isinstance(i, (int, float)) for i in obj):
                return '[' + ', '.join(map(str, obj)) + ']'
        return super().encode(obj)   
    
if __name__ == "__main__":
    create_compressor_line()