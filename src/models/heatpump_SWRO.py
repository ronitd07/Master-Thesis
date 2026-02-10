
"""
heat pump model of MVV GKM Manheim with subcooling

"""
from tespy.components import CycleCloser, Compressor, Valve, HeatExchanger, Source, Sink, Condenser, Pump ,Splitter,DropletSeparator, Merge, Drum,MovingBoundaryHeatExchanger,TurboCompressor,Splitter
from tespy.tools.characteristics import CharLine,CharMap
from tespy.tools.characteristics import load_custom_char
from tespy.connections import Connection, Ref
from tespy.networks import Network
from fluprodia import FluidPropertyDiagram
import pandas as pd
#import plotly.express as px 
#import fhgcd_plots.main as fhgCD
import CoolProp.CoolProp as CP
#import mosaik_api_v3
import multiprocessing as mp
from scipy import interpolate
import json
import os
import numpy as np
from CoolProp.CoolProp import PropsSI
import matplotlib.pyplot as plt


# import time as time

META = {
    'type': 'time-based',
    'models': {
        'HeatpumpDummy': {
            'public': True,
            'params': ['params'],
            'attrs': ['dotm_in_pri', 'T_in_pri', 'T_out_pri', 'dotQ_heating', 'dotQ_cooling', 'cooling_mode'],
        },
    },
}

class Heatpump_tespy():
    """
    This is the model of the heatpump simulation
    """
    eta1_vals = []
    eta2_vals = []
    m1_vals = []
    m2_vals = []

    def __init__(self, params) -> None:
        self.name = params["name"]
        self.working_fluid = params["working_fluid"]
        self.cooling_mode = params["cooling_mode #not implemented"]
        self.eta_compressor = params["eta_compressor"]
        self.eta_pump = params["eta_pump"]
        self.ttd_heat_exchanger = params["ttd_heat_exchanger"]
        self.heating_system_feed_tenp = params["heating_system_feed_temp"]
        self.heating_system_return_temp = params["heating_system_return_temp"]
        self.cooling_system_feed_temp = params["cooling_system_feed_temp"]
        self.cooling_system_return_temp = params["cooling_system_return_temp"]
        self.tamb_design = params["tamb_design"]
        self.heat_design = params["heat_design"]
        self.cooling_design = params["cooling_Q_design"] #-323e3 #323 kW Kältelast
        self.cooling_tamb_design = params["cooling_tamb_design"]

        self.eta1_vals = []
        self.eta2_vals = []
        self.m1_vals = []
        self.m2_vals = []
        
        self.setup_heat_pump()



    
    def setup_heat_pump(self):
        """This function generates a heatpump system and generates it for an design state

        Returns:
            _type_: _description_
        """
        #create network and connections
        #self.nwk = Network(fluids=[self.working_fluid, "air", "Water","INCOMP::MEG[0.2]|mass"], p_unit="bar", T_unit="C", h_unit="kJ / kg", v="m3 / h", iterinfo=False)
        self.nwk = Network(fluids=[self.working_fluid, "Water"], iterinfo=False)
        self.nwk.units.set_defaults(pressure="bar", temperature = "°C", enthalpy = "kJ/kg", volumetric_flow = "m3/h",entropy = 'J / kgK' )
        self.cp1 = Compressor("compressor1")
        self.cp2 = Compressor("compressor2")
        self.ev = HeatExchanger("evaporator")
        #self.cd = Condenser("condenser")
        self.cd = MovingBoundaryHeatExchanger("condenser")
        self.va1 = Valve("expansion valve1")
        self.va2 = Valve("expansion valve2")
        self.va3 = Valve("expansion valve3")
        self.va4 = Valve("expansion valve4")
        self.cc = CycleCloser("cycle closer")
        self.sp1 = DropletSeparator("Separator 1")
        self.sp2 = DropletSeparator("Separator 2")
        self.sp3 = DropletSeparator("Separator 3")
        self.spl = Splitter("Splitter")
        self.mg1 = Merge('Merge 1')
        self.mg2 = Merge('Merge 2')
        self.mg3 = Merge('Merge 3')
        self.mg4 = Merge('Merge 4')
        self.fan = Pump("Pump")
        self.ihx = HeatExchanger("Internal heat exchanger")
        
        self.so1 = Source("ambient river source")
        self.si1 = Sink("ambient river sink")
        self.so2 = Source("heating source")
        self.si2 = Sink("heating sink")

        self.c0 = Connection(self.cc, "out1", self.mg1, "in1", label="0")
        self.c1 = Connection(self.mg1, "out1", self.cp1, "in1", label="1")
        self.c2 = Connection(self.cp1, "out1", self.mg2, "in1", label="2")
        self.c3 = Connection(self.mg2, "out1", self.cp2, "in1", label="3")
        self.c4 = Connection(self.cp2, "out1", self.cd, "in1", label="4")
        self.c5 = Connection(self.cd, "out1", self.va1, "in1", label="5")
        self.c6 = Connection(self.va1, "out1", self.sp1, "in1", label="6")
        self.c7 = Connection(self.sp1, "out2", self.mg2, "in2", label="7")
        self.c8 = Connection(self.sp1, "out1", self.spl, "in1", label="8")
        self.c9 = Connection(self.spl, "out2", self.ihx, "in1", label="9")
        self.c10 = Connection(self.ihx, "out1", self.va3, "in1", label="10")
        self.c11 = Connection(self.spl, "out1", self.va2, "in1", label="11")
        self.c12 = Connection(self.va2, "out1", self.mg3, "in1", label="12")
        self.c13 = Connection(self.va3, "out1", self.mg3, "in2", label="13")
        self.c14 = Connection(self.mg3, "out1", self.sp2, "in1", label="14")
        self.c15 = Connection(self.sp2, "out2", self.mg1, "in2", label="15")
        self.c16 = Connection(self.sp2, "out1", self.va4, "in1", label="16")
        self.c17 = Connection(self.va4, "out1", self.mg4, "in1", label="17")
        self.c18 = Connection(self.mg4, "out1", self.sp3, "in1", label="18")
        self.c19 = Connection(self.sp3, "out1", self.ev, "in1", label="19")
        self.c20 = Connection(self.ev, "out1", self.mg4, "in2", label="20")
        self.c21 = Connection(self.sp3, "out2", self.ihx, "in2", label="21")
        self.c22 = Connection(self.ihx, "out2", self.cc, "in1", label="22")


        self.nwk.add_conns(self.c0, self.c1, self.c2, self.c3, self.c4, self.c5, self.c6, self.c7, self.c8,self.c9,self.c10,self.c11,self.c12,self.c13,self.c14,
                           self.c15,self.c16,self.c17,self.c18,self.c19,self.c20,self.c21,self.c22)

        self.c23 = Connection(self.so1, "out1", self.ev, "in2", label="23")
        self.c24 = Connection(self.ev, "out2", self.si1, "in1", label="24")


        self.c25 = Connection(self.so2, "out1", self.cd, "in2", label="25")
        self.c26 = Connection(self.cd, "out2", self.si2, "in1", label="26")

        self.nwk.add_conns(self.c23, self.c24, self.c25, self.c26)


if __name__ == "__main__":
    # Define the parameters dictionary
    params_hp = {
        "name": "MyHeatPump",
        "working_fluid": "R1234ZE",
        "cooling_mode #not implemented": False,
        "eta_compressor": 0.85,
        "eta_pump": 0.7,
        "ttd_heat_exchanger": 5.0,
        "heating_system_feed_temp": 101.32,
        "heating_system_return_temp": 74.38,
        "cooling_system_feed_temp": 10.0,
        "cooling_system_return_temp": 15.0,        
        "tamb_design": 5.35,
        "heat_design": 22e6,        # 22 MW as nominal load
        "cooling_Q_design": 50e3,    # 50 kW
        "cooling_tamb_design": 25.0
    }

    # Create an instance of the heat pump
    hp = Heatpump_tespy(params_hp)

    print("Design case solved successfully!")
