
from tespy.components import CycleCloser, Compressor, Valve, HeatExchanger, Source, Sink, Condenser, Pump ,Splitter,DropletSeparator, Merge, Drum,MovingBoundaryHeatExchanger,PolynomialCompressor, TurboCompressor
from tespy.tools.characteristics import CharLine
from tespy.tools.characteristics import CharMap
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

class Heatpump_tespy():
    """
    This is the model of the heatpump simulation
    """

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
        
        self.setup_heat_pump()
        self.calc_partload_state()
    
    def setup_heat_pump(self):
        """This function generates a heatpump system and generates it for an design state

        Returns:
            _type_: _description_
        """
        #create network and connections
        #self.nwk = Network(fluids=[self.working_fluid, "air", "Water","INCOMP::MEG[0.2]|mass"], p_unit="bar", T_unit="C", h_unit="kJ / kg", v="m3 / h", iterinfo=False)
        self.nwk = Network(fluids=[self.working_fluid, "Water"], iterinfo=False)
        self.nwk.units.set_defaults(pressure="bar", temperature = "°C", enthalpy = "kJ/kg", volumetric_flow = "m3/h",entropy = 'J / kgK' )
        self.cp1 = TurboCompressor("compressor1")
        self.cp2 = TurboCompressor("compressor2")
        self.ev = HeatExchanger("evaporator")
        #self.cd = Condenser("condenser")
        self.cd = MovingBoundaryHeatExchanger("condenser")
        self.va1 = Valve("expansion valve1")
        self.va2 = Valve("expansion valve2")
        self.cc = CycleCloser("cycle closer")
        self.sp = DropletSeparator("Separator")
        self.mg = Merge('Merge')
        self.fan = Pump("Pump")
        
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

        self.c10 = Connection(self.so1, "out1", self.fan, "in1", label="10")
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
        self.c3.set_attr(T=self.heating_system_feed_tenp + self.ttd_heat_exchanger) 

        # set the power and the compressor efficiencies 
        Q_design = self.heat_design
        self.cd.set_attr(Q=-100e3) # 100kW as a starting value

                                
        #gen_char = load_custom_char('eta_s_test', CharLine)
        #Default charmaps
        self.cp1.set_attr(eta_s=self.eta_compressor, design = ['eta_s'], offdesign = ['char_map_eta_s'])
        self.cp2.set_attr(eta_s=self.eta_compressor, design = ['eta_s'],  offdesign = ['char_map_eta_s'])

        #Custom charmaps
        #self.cp1.set_attr(eta_s=self.eta_compressor, design = ['eta_s'],char_map_eta_s = {'char_func' : map_eta1},char_map_pr = {'char_func' : map_pr1}, offdesign = ['char_map_eta_s','char_map_pr'])
        #self.cp2.set_attr(eta_s=self.eta_compressor, design = ['eta_s'],char_map_eta_s = {'char_func' : map_eta2},char_map_pr = {'char_func' : map_pr2}, offdesign = ['char_map_eta_s','char_map_pr'])

        #set the fan efficiency
        self.fan.set_attr(eta_s=self.eta_pump,pr=1.002)


        # set the connections around the hx
        self.c1.set_attr(fluid={self.working_fluid: 1}, x=1.0)
        self.c10.set_attr(fluid={ "Water": 1},  T=self.tamb_design,p=1)
        self.c12.set_attr(T=self.tamb_design - 3)
        self.c21.set_attr(fluid={ "Water": 1}, p=3.0, T=self.heating_system_return_temp)
        self.c22.set_attr(T=self.heating_system_feed_tenp)
        #hx elements 
        self.cd.set_attr(pr1=1, pr2=1) 
        self.c4.set_attr(td_bubble=15) 
        self.ev.set_attr(pr1=1, pr2=1)

        self.c7.set_attr(p=10)
        self.c5.set_attr(fluid={self.working_fluid: 1})

        try:

            #solve the design case
            self.nwk.solve("design",print_results=False)
        except ValueError as e:
            print(e)


        #vary heat exchanger efficiency
        self.ev.set_attr(ttd_l=self.ttd_heat_exchanger)
        self.c1.set_attr(T=None)
        self.cd.set_attr(ttd_u=self.ttd_heat_exchanger)
        self.c3.set_attr(T=None)
        self.cd.set_attr(Q=-Q_design) #
        #save data
        self.nwk.solve("design")
        #self.nwk.print_results()

        # Get the design heat transfer coefficient to be used in offdesign case
        self.cond_UA_design = self.cd.UA.val # W/ K
        self.ev_kA_design = self.ev.kA.val


        self.nwk.save("data/process_data/hp_design_"+self.name+".json")
        print("Heatpump design mode successful")

        
    def calc_partload_state(self):
        """This function can calculate partload states of an heat pump with a calculated design state

        Args:
            temperature (float, optional): _description_. Defaults to None.
            Q (float, optional): _description_. Defaults to None.

        Returns:
            _type_: _description_
        """
        
        self.c10.set_attr(T=7.01)
        self.c12.set_attr(T=3.70)
        
        self.cd.set_attr(Q=-15.74e6)  
        self.c7.set_attr(p=8.62)    
        self.c21.set_attr(T=60.38)
        self.c22.set_attr(T=97.12)
        self.c1.set_attr(td_dew = 1.57,x=None)
        self.cd.set_attr(ttd_u=None,  UA = self.cd.UA.val)
        self.ev.set_attr(ttd_l=None, kA = self.ev_kA_design)
        self.c3.set_attr(p=28.62)
        self.t_cond_out = PropsSI("T", "P", self.c3.p.val*1e5, "Q", 0, self.working_fluid) - 273.15
        t_subcooling = self.t_cond_out-64.5
        self.c4.set_attr(td_bubble=t_subcooling)


        self.cp1.set_attr(igva='var')
        self.cp2.set_attr(igva='var')
        
        try:
            self.nwk.solve("offdesign",  design_path="data/process_data/hp_design_"+self.name+".json")
            self.nwk.assert_convergence()
            self.nwk.print_results()
            self.nwk.save('results.csv')
        except Exception as e:
            # mark as infeasible — record error and continue
            print(e)

if __name__ == "__main__":
    # Define the parameters dictionary
    params_hp = {
        "name": "HeatPump",
        "working_fluid": "R1234ZE",
        "cooling_mode #not implemented": False,
        "eta_compressor": 0.92,
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
    hp = Heatpump_tespy(params_hp)