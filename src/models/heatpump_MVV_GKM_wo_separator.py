
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

    
    def setup_heat_pump(self):
        """This function generates a heatpump system and generates it for an design state

        Returns:
            _type_: _description_
        """
        #create network and connections
        #self.nwk = Network(fluids=[self.working_fluid, "air", "Water","INCOMP::MEG[0.2]|mass"], p_unit="bar", T_unit="C", h_unit="kJ / kg", v="m3 / h", iterinfo=False)
        self.nwk = Network(fluids=[self.working_fluid, "Water"], iterinfo=True)
        self.nwk.units.set_defaults(pressure="bar", temperature = "°C", enthalpy = "kJ/kg", volumetric_flow = "m3/h" )
        self.cp1 = Compressor("compressor1")
        self.cp2 = Compressor("compressor2")
        self.ev = HeatExchanger("evaporator")
        self.cd = Condenser("condenser")
        self.va1 = Valve("expansion valve1")
        self.va2 = Valve("expansion valve2")
        self.cc = CycleCloser("cycle closer")
        self.sp = Drum("Separator")
        self.mg = Merge('Merge')
        self.fan = Pump("fan")
        
        self.so1 = Source("ambient river source")
        self.si1 = Sink("ambient river sink")
        self.so2 = Source("heating source")
        self.si2 = Sink("heating sink")

        self.c0 = Connection(self.ev, "out1", self.cc, "in1", label="0")
        self.c1 = Connection(self.cc, "out1", self.cp1, "in1", label="1")
        self.c2 = Connection(self.cp1, "out1", self.cp2, "in1", label="2")
        self.c3 = Connection(self.cp2, "out1", self.cd, "in1", label="3")
        self.c4 = Connection(self.cd, "out1", self.va1, "in1", label="4")
        self.c5 = Connection(self.va1, "out1", self.va2, "in1", label="5")
        self.c6 = Connection(self.va2, "out1", self.ev, "in1", label="6")



        self.nwk.add_conns(self.c0, self.c1, self.c2, self.c3, self.c4, self.c5, self.c6)
        #self.nwk.add_conns(self.c0, self.c1, self.c2,self.c4, self.c5)

        self.c10 = Connection(self.so1, "out1", self.fan, "in1", label="20")
        self.c11 = Connection(self.fan, "out1", self.ev, "in2", label="11")
        self.c12 = Connection(self.ev, "out2", self.si1, "in1", label="12")


        self.c21 = Connection(self.so2, "out1", self.cd, "in2", label="21")
        self.c22 = Connection(self.cd, "out2", self.si2, "in1", label="22")

        self.nwk.add_conns(self.c10,self.c11, self.c12, self.c21, self.c22)


        ####################################################################
        # Calculate the design case for heating
        ####################################################################
        # set the parameters before and behind the compressor
        self.c1.set_attr(T=self.tamb_design - self.ttd_heat_exchanger)
        self.c4.set_attr(T=self.heating_system_feed_tenp + self.ttd_heat_exchanger) 

        # set the power and the compressor efficiencies 
        Q_design = self.heat_design
        self.cd.set_attr(Q=Q_design)
        self.cp1.set_attr(eta_s=0.75)
        self.cp2.set_attr(eta_s=0.75)

        #set the fan efficiency
        self.fan.set_attr(eta_s=self.eta_fan,pr=1.002)


        # set the connections around the hx
        self.c1.set_attr(fluid={self.working_fluid: 1}, x=1.0)
        self.c10.set_attr(fluid={ "Water": 1},  T=self.tamb_design,p=1)
        self.c12.set_attr(p=None)
        self.c12.set_attr(T=self.tamb_design -2)
        self.c21.set_attr(fluid={ "Water": 1}, p=3.0, T=self.heating_system_return_temp)
        self.c22.set_attr(T=self.heating_system_feed_tenp)
        #hx elements 
        self.cd.set_attr(pr1=1, pr2=1) 
        self.ev.set_attr(pr1=1, pr2=0.98)
      
        #self.sp.set_attr(split=[0.6, 0.4])  # fraction of mass to out1/out2
        self.va1.set_attr(pr=0.3)
        self.c4.set_attr(m=0.5)


        #solve the design case
        self.nwk.solve("design",print_results=True)
        print("Pressure of 1st compressor ", self.cp1.P.val)
        print("Pressure of 2nd compressor ", self.cp2.P.val)

        #vary heat exchanger efficiency
        self.ev.set_attr(ttd_u=self.ttd_heat_exchanger)
        self.c1.set_attr(T=None)
        self.cd.set_attr(ttd_u=self.ttd_heat_exchanger)
        self.c4.set_attr(T=None)

        #save data
        #self.nwk.solve("design")


        self.nwk.save("data/process_data/hp_design_"+self.name+".json")

        ################################################################
        #Setup the cooling case
        ################################################################
        if self.cooling_mode == True:
            #create network and connections
            #self.nwk_cooling = Network(fluids=[self.working_fluid, "air", "Water"], p_unit="bar", T_unit="C",  h_unit="kJ / kg", v_unit="m3 / h", iterinfo=False)
            self.nwk_cooling = Network(fluids=[self.working_fluid, "air", "Water"],  iterinfo=False)
            self.nwk_cooling.units.set_defaults(pressure="bar", temperature = "°C", enthalpy = "kJ/kg", volumetric_flow = "m3/h" )
            self.cp_cooling = Compressor("compressor")
            self.ev_cooling = HeatExchanger("evaporator")
            self.cd_cooling = Condenser("condenser")
            self.va_cooling = Valve("expansion valve")
            self.cc_cooling = CycleCloser("cycle closer")
            self.fan_cooling = Pump("fan") #fan is only needed with air source heatpumps
            
            self.so1_cooling = Source("ambient air source")
            self.si1_cooling = Sink("ambient air sink")
            self.so2_cooling = Source("heating source")
            self.si2_cooling = Sink("heating sink")

            self.c0_cooling = Connection(self.va_cooling, "out1", self.cc_cooling, "in1", label="0")
            self.c1_cooling = Connection(self.cc_cooling, "out1", self.ev_cooling, "in2", label="1")
            self.c2_cooling = Connection(self.ev_cooling, "out2", self.cp_cooling, "in1", label="2")
            self.c3_cooling = Connection(self.cp_cooling, "out1", self.cd_cooling, "in1", label="3")
            self.c4_cooling = Connection(self.cd_cooling, "out1", self.va_cooling, "in1", label="4")

            self.nwk_cooling.add_conns(self.c0_cooling, self.c1_cooling, self.c2_cooling, self.c3_cooling, self.c4_cooling)

            self.c11_cooling = Connection(self.so1_cooling, "out1", self.ev_cooling, "in1", label="11")
            self.c12_cooling = Connection(self.ev_cooling, "out1", self.si1_cooling, "in1", label="12")

            self.c20_cooling = Connection(self.so2_cooling, "out1", self.fan_cooling, "in1", label="20")
            self.c21_cooling = Connection(self.fan_cooling, "out1", self.cd_cooling, "in2", label="21")
            self.c22_cooling = Connection(self.cd_cooling, "out2", self.si2_cooling, "in1", label="22")

            self.nwk_cooling.add_conns(self.c11_cooling, self.c12_cooling, self.c21_cooling, self.c22_cooling, self.c20_cooling)

            ####################################################################
            # Calculate the design case for cooling
            ####################################################################
            # set the parameters before and behind the compressor
            # evaporation point
            p_eva = CP.PropsSI("P", "Q", 1, "T", 2 + 273.15, self.working_fluid) * 1e-5
            self.c2_cooling.set_attr(p=p_eva)

            # condensation point
            p_cond = CP.PropsSI("P", "Q", 0, "T", 60 + 273.15, self.working_fluid) * 1e-5
            self.c4_cooling.set_attr(p=p_cond)
            # condenser.set_attr(ttd_u=None)
            h_evap = CP.PropsSI("H", "Q", 1, "T", 2 + 273.15, self.working_fluid) * 1e-3
            self.c2_cooling.set_attr(Td_bp=None, h=h_evap * 1.01)

            # set the values of some components
            self.cp_cooling.set_attr(eta_s=self.eta_compressor)
            self.ev_cooling.set_attr(Q=self.cooling_design)
            self.fan_cooling.set_attr(eta_s=self.eta_fan) #TODO check if a fan curve is necessary
 
            #set connections around the hx
            self.c2_cooling.set_attr(fluid={self.working_fluid: 1, "Water": 0, "air": 0})
            self.c11_cooling.set_attr(fluid={self.working_fluid: 0, "Water": 1, "air": 0}, p=3, T=self.cooling_system_feed_temp)
            self.c12_cooling.set_attr(T=self.cooling_system_return_temp)
            self.c20_cooling.set_attr(fluid={self.working_fluid: 0, "Water": 0, "INCOMP::MEG[0.2]": 1}, T=self.cooling_tamb_design, p=1) #TODO test if this glykol works
            self.c22_cooling.set_attr(T=self.heating_system_feed_tenp, p =1)
            self.cd_cooling.set_attr(pr1=1, pr2=0.99)
            self.ev_cooling.set_attr(pr1=1, pr2=1)
             
            # calculate and save design case
            self.nwk_cooling.solve("design")
            self.nwk_cooling.save("data/process_data/hp_design_cooling_"+self.name+".json")

            #TODO manipulate JSON, so that there is the same design parameters

        
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
            # calculate parameters of the pump
            cop = abs(self.cd.Q.val) / (self.cp.P.val + self.fan.P.val)
            #cop = abs(self.cd.Q.val) / (self.cp.P.val )
            compressor_power = self.cp.P.val + self.fan.P.val
            #compressor_power = self.cp.P.val
            load = abs(self.cd.Q.val)
            T_evap = self.c2.T.val
            T_cond = self.c4.T.val
            T_delta = T_cond - T_evap
            m_flow = self.c12.m.val
        except Exception as e:
            # mark as infeasible — record error and continue
            print(e)
            cop=None
            compressor_power=None
            load=None
            T_delta = None
            m_flow = 0
        return cop, compressor_power, load, T_delta, m_flow


    def calc_partload_state_cooling(self, temperature:float=None, Q:float=None):
        """This function can calculates cooling partload states of an heat pump with a calculated design state

        Args:
            temperature (float, optional): _description_. Defaults to None.
            Q (float, optional): _description_. Defaults to None.

        Returns:
            _type_: _description_
        """
        if self.cooling_mode == True:
            if temperature != None:
                self.c20_cooling.set_attr(T=temperature)
            if Q != None:
                self.ev_cooling.set_attr(Q=Q)
                
            # self.nwk.reset_topology_reduction_specifications()
            
            self.nwk_cooling.solve("offdesign", design_path="data/process_data/hp_design_cooling_"+self.name+".json")

            # calculate parameters of the pump
            #? is it coorect to use the ev cooling as cop?
            cop = abs(self.cd_cooling.Q.val) / (self.cp_cooling.P.val + self.fan_cooling.P.val)
            compressor_power = self.cp_cooling.P.val + self.fan_cooling.P.val
            
            return cop, compressor_power
        else:
            raise ValueError("Please switch to cooling mode first with the function switch_to_cooling_mode")

    
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
            cop, power, load, T_delta,m_flow = self.calc_partload_state(ambient_temperature, Q)
        else:
            cop, power = self.calc_partload_state_cooling(ambient_temperature, Q)
        return cop, power, load, T_delta, m_flow
    def evap_outlet_temperature(self):
        return self.c12.T.val 
    

if __name__ == "__main__":
    # Define the parameters dictionary
    params = {
        "name": "MyHeatPump",
        "working_fluid": "R1234ZE",
        "cooling_mode #not implemented": False,
        "eta_compressor": 0.85,
        "eta_fan": 0.7,
        "ttd_heat_exchanger": 5.0,
        "heating_system_feed_temp": 55.0,
        "heating_system_return_temp": 30.0,
        "cooling_system_feed_temp": 10.0,
        "cooling_system_return_temp": 15.0,        
        "tamb_design": 5.0,
        "heat_design": 100e3,        # 100 kW
        "cooling_Q_design": 50e3,    # 50 kW
        "cooling_tamb_design": 25.0
    }

    # Create an instance of the heat pump
    hp = Heatpump_tespy(params)

    print("Design case solved successfully!")
