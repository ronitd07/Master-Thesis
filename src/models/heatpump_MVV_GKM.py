
"""
Mosaik interface for bhe model

"""
from tespy.components import CycleCloser, Compressor, Valve, HeatExchanger, Source, Sink, Condenser, Pump ,Splitter,DropletSeparator, Merge, Drum
from tespy.connections import Connection, Ref
from tespy.networks import Network
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
    def __init__(self, params) -> None:
        self.name = params["name"]
        self.working_fluid = params["working_fluid"]
        self.cooling_mode = params["cooling_mode #not implemented"]
        self.eta_compressor = params["eta_compressor"]
        self.eta_fan = params["eta_fan"]
        self.ttd_heat_exchanger = params["ttd_heat_exchanger"]
        self.heating_system_feed_tenp = params["heating_system_feed_temp"]
        self.heating_system_return_temp = params["heating_system_return_temp"]
        self.cooling_system_feed_temp = params["cooling_system_feed_temp"]
        self.cooling_system_return_temp = params["cooling_system_return_temp"]
        self.tamb_design = params["tamb_design"]
        self.heat_design = params["heat_design"]
        self.cooling_design = params["cooling_Q_design"] #-323e3 #323 kW Kältelast
        self.cooling_tamb_design = params["cooling_tamb_design"]

        self.setup_heat_pump()
        #self.plot()
    
    def setup_heat_pump(self):
        """This function generates a heatpump system and generates it for an design state

        Returns:
            _type_: _description_
        """
        #create network and connections
        #self.nwk = Network(fluids=[self.working_fluid, "air", "Water","INCOMP::MEG[0.2]|mass"], p_unit="bar", T_unit="C", h_unit="kJ / kg", v="m3 / h", iterinfo=False)
        self.nwk = Network(fluids=[self.working_fluid, "Water"], iterinfo=False)
        self.nwk.units.set_defaults(pressure="bar", temperature = "°C", enthalpy = "kJ/kg", volumetric_flow = "m3/h",entropy = 'kJ / kgK' )
        self.cp1 = Compressor("compressor1")
        self.cp2 = Compressor("compressor2")
        self.ev = HeatExchanger("evaporator")
        self.cd = Condenser("condenser")
        self.va1 = Valve("expansion valve1")
        self.va2 = Valve("expansion valve2")
        self.cc = CycleCloser("cycle closer")
        self.sp = DropletSeparator("Separator")
        self.mg = Merge('Merge')
        self.fan = Pump("fan")
        
        self.so1 = Source("ambient river source")
        self.si1 = Sink("ambient river sink")
        self.so2 = Source("heating source")
        self.si2 = Sink("heating sink")

        self.c0 = Connection(self.ev, "out2", self.cc, "in1", label="0")
        self.c1 = Connection(self.cc, "out1", self.cp1, "in1", label="1")
        self.c2 = Connection(self.cp1, "out1", self.mg, "in1", label="2")
        self.c2a = Connection(self.mg, "out1", self.cp2, "in1", label="2a")
        self.c3 = Connection(self.cp2, "out1", self.cd, "in1", label="3")
        self.c4 = Connection(self.cd, "out1", self.va1, "in1", label="4")
        self.c5 = Connection(self.va1, "out1", self.sp, "in1", label="5")
        self.c6 = Connection(self.sp, "out2", self.mg, "in2", label="6")
        self.c7 = Connection(self.sp, "out1", self.va2, "in1", label="7")
        self.c8 = Connection(self.va2, "out1", self.ev, "in2", label="8")



        self.nwk.add_conns(self.c0, self.c1, self.c2,self.c2a, self.c3, self.c4, self.c5, self.c6, self.c7, self.c8)
        #self.nwk.add_conns(self.c0, self.c1, self.c2,self.c4, self.c5)

        self.c10 = Connection(self.so1, "out1", self.fan, "in1", label="20")
        self.c11 = Connection(self.fan, "out1", self.ev, "in1", label="11")
        self.c12 = Connection(self.ev, "out1", self.si1, "in1", label="12")


        self.c21 = Connection(self.so2, "out1", self.cd, "in2", label="21")
        self.c22 = Connection(self.cd, "out2", self.si2, "in1", label="22")

        self.nwk.add_conns(self.c10,self.c11, self.c12, self.c21, self.c22)


        ####################################################################
        # Calculate the design case for heating
        ####################################################################
        # set the parameters before and behind the compressor
        self.c1.set_attr(T=self.tamb_design - self.ttd_heat_exchanger)
        self.c4.set_attr(T=self.heating_system_feed_tenp + self.ttd_heat_exchanger) 
        #self.c1.set_attr(p=2) 

        # set the power and the compressor efficiencies 
        Q_design = self.heat_design
        self.cd.set_attr(Q=-Q_design)
        self.cp1.set_attr(eta_s=self.eta_compressor)
        self.cp2.set_attr(eta_s=self.eta_compressor)

        #set the fan efficiency
        self.fan.set_attr(eta_s=self.eta_fan,pr=1.002)


        # set the connections around the hx
        self.c1.set_attr(fluid={self.working_fluid: 1}, x=1.0)
        #self.c1.set_attr(td_dew=10)
        self.c10.set_attr(fluid={ "Water": 1},  T=self.tamb_design,p=1)
        self.c12.set_attr(T=self.tamb_design -3)
        self.c21.set_attr(fluid={ "Water": 1}, p=3.0, T=self.heating_system_return_temp)
        self.c22.set_attr(T=self.heating_system_feed_tenp)
        #hx elements 
        self.cd.set_attr(pr1=1, pr2=1) 
        self.ev.set_attr(pr1=1, pr2=0.98)
      
        #self.sp.set_attr(split=[0.6, 0.4])  # fraction of mass to out1/out2
        #self.c7.set_attr(p=Ref(self.c4,1,-10))
        self.c7.set_attr(p=10)
        self.c5.set_attr(fluid={self.working_fluid: 1})
        #self.c4.set_attr(m=0.6)
        #self.c4.set_attr(td_bubble = 2)
        try:

            #solve the design case
            self.nwk.solve("design",print_results=True)
        except ValueError as e:
            print(e)


        #vary heat exchanger efficiency
        self.ev.set_attr(ttd_l=self.ttd_heat_exchanger)
        self.c1.set_attr(T=None)
        self.cd.set_attr(ttd_u=self.ttd_heat_exchanger)
        self.c4.set_attr(T=None)
        #save data
        self.nwk.solve("design")

        #cop = abs(self.cd.Q.val) / (self.cp1.P.val + self.cp2.P.val + self.fan.P.val)
        #print("COP :",cop)

        self.nwk.save("data/process_data/hp_design_"+self.name+".json")

        
    def calc_partload_state(self, temperature:float=None, Q:float=None):
        """This function can calculate partload states of an heat pump with a calculated design state

        Args:
            temperature (float, optional): _description_. Defaults to None.
            Q (float, optional): _description_. Defaults to None.

        Returns:
            _type_: _description_
        """
        if temperature != None:
            self.c10.set_attr(T=temperature)
        if Q != None:
            self.cd.set_attr(Q=-Q)  
        #self.nwk.reset_topology_reduction_specifications()
        # After design solves in partload_heat_pump()
        #self.ev.set_attr(ttd_u=None)
        #self.cd.set_attr(ttd_u=None)

        # Freeze the actual design areas for offdesign
        #self.ev.set_attr(kA=1.5*self.ev.kA.val)
        #self.cd.set_attr(kA=1.5*self.cd.kA.val)
        
        try:

            self.nwk.solve("offdesign", design_path="data/process_data/hp_design_"+self.name+".json")
            cop = abs(self.cd.Q.val) / (self.cp1.P.val + self.cp2.P.val + self.fan.P.val )
            #cop = abs(self.cd.Q.val) / (self.cp.P.val )
            compressor_power = self.cp1.P.val + self.cp2.P.val 
            load = abs(self.cd.Q.val)
            T_evap = self.c1.T.val
            T_cond = self.c4.T.val
            #T_delta = T_cond - T_evap
            #m_flow = self.c12.m.val
            #print(self.c8.T.val," ", self.c0.T.val, " ", self.c1.T.val, " ", self.ev.ttd_l.val, " ", self.ev.ttd_u.val, " ", self.c1.p.val)
        except Exception as e:
            # mark as infeasible — record error and continue
            print(e)
            cop=None
            compressor_power=None
            load=None
            T_delta = None
            m_flow = 0
        return cop, compressor_power,load

   
    def step(self, Q:float, ambient_temperature:float, cooling:bool=False):
        """This function takes one step in the heatpump simulation and returns the values

        Args:
            Q (float): _description_
            ambient_temperature (float): _description_
            cooling (bool, optional): _description_. Defaults to False.

        Returns:
            _type_: _description_
        """
        if cooling == False:
            cop, power,load = self.calc_partload_state(ambient_temperature, Q)
        else:
            cop, power = self.calc_partload_state_cooling(ambient_temperature, Q)
        return cop, power,load
    def evap_outlet_temperature(self):
        return self.c12.T.val 
    def plot(self):
        states = [self.c1, self.c2,self.c2a, self.c3, self.c4,self.c5,self.c6,self.c2a,self.c7,self.c8, self.c0]  # cycle order

        #Plot saturation lines of P-h and T-s diagram
        fluid = 'R1234ZE'

        # Generate temperature range for saturation (in Kelvin)
        T_sat = np.linspace(PropsSI('Tmin', fluid), PropsSI('Tcrit', fluid) - 0.1, 300)

        # Saturation lines
        s_liq = [PropsSI('S', 'T', T, 'Q', 0, fluid) / 1000 for T in T_sat]  # kJ/kg·K
        s_vap = [PropsSI('S', 'T', T, 'Q', 1, fluid) / 1000 for T in T_sat]

        h_liq = [PropsSI('H', 'T', T, 'Q', 0, fluid) / 1000 for T in T_sat]  # kJ/kg
        h_vap = [PropsSI('H', 'T', T, 'Q', 1, fluid) / 1000 for T in T_sat]

        p_liq = [PropsSI('P', 'T', T, 'Q', 0, fluid) / 100000 for T in T_sat]  # bar
        p_vap = [PropsSI('P', 'T', T, 'Q', 1, fluid) / 100000 for T in T_sat]

        #Plot P-h and T-S diagrams

        T_vals = [c.T.val for c in states]
        s_vals = [c.s.val for c in states]
        p_vals = [c.p.val for c in states]
        h_vals = [c.h.val for c in states]

        # Close the cycle by adding the first point again
        T_vals.append(T_vals[0])
        s_vals.append(s_vals[0])

        # Close the cycle
        p_vals.append(p_vals[0])
        h_vals.append(h_vals[0])

        # ----------------- T-s Diagram -----------------
        plt.figure(figsize=(8, 5))
        plt.plot(s_vals, T_vals, marker='o', linestyle='-')
        plt.title('T-s Diagram')
        plt.xlabel('Entropy [kJ/kg·K]')
        plt.ylabel('Temperature [°C]')
        plt.grid(True)

        plt.plot(s_liq, T_sat - 273.15, 'r--', label='Saturation curve')
        plt.plot(s_vap, T_sat - 273.15, 'r--')
        plt.legend()

        plt.show()   # Shows in Window 1


        # ----------------- p-h Diagram -----------------
        plt.figure(figsize=(8, 5))
        plt.plot(h_vals, p_vals, marker='o', linestyle='-')
        plt.title('p-h Diagram')
        plt.xlabel('Enthalpy [kJ/kg]')
        plt.ylabel('Pressure [bar]')
        plt.yscale('log')
        plt.grid(True, which='both', linestyle='--')

        plt.plot(h_liq, p_liq, 'r--', label='Saturation curve')
        plt.plot(h_vap, p_vap, 'r--')
        plt.legend()

        plt.show()    # Shows in Window 2

if __name__ == "__main__":
    # Define the parameters dictionary
    params = {
        "name": "MyHeatPump",
        "working_fluid": "R1234ZE",
        "cooling_mode #not implemented": False,
        "eta_compressor": 0.8,
        "eta_fan": 0.7,
        "ttd_heat_exchanger": 5.0,
        "heating_system_feed_temp": 80.0,
        "heating_system_return_temp": 30.0,
        "cooling_system_feed_temp": 10.0,
        "cooling_system_return_temp": 15.0,        
        "tamb_design": 15.0,
        "heat_design": 100e3,        # 100 kW
        "cooling_Q_design": 50e3,    # 50 kW
        "cooling_tamb_design": 25.0
    }

    # Create an instance of the heat pump
    hp = Heatpump_tespy(params)

    print("Design case solved successfully!")
