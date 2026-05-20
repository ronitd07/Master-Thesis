
"""
heat pump model of MVV GKM Manheim using compressor maps

"""
from tespy.components import CycleCloser, Compressor, Valve, HeatExchanger, Source, Sink, Condenser, Pump ,Splitter,DropletSeparator, Merge, Drum,MovingBoundaryHeatExchanger,PolynomialCompressor, TurboCompressor
from tespy.tools.characteristics import CharLine
from tespy.tools.characteristics import CharMap
from tespy.tools.characteristics import load_custom_char
from tespy.tools.characteristics import load_default_char as ldc
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
        self.eta_compressor1 = params["eta_compressor1"]
        self.eta_compressor2 = params["eta_compressor2"]
        self.ttd_heat_exchanger = params["ttd_heat_exchanger"]
        self.heating_system_feed_tenp = params["heating_system_feed_temp"]
        self.heating_system_return_temp = params["heating_system_return_temp"]
        self.tamb_design = params["tamb_design"]
        self.heat_design = params["heat_design"]

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
        self.nwk.units.set_defaults(pressure="bar",pressure_difference ="bar", temperature = "°C", enthalpy = "kJ/kg", volumetric_flow = "m3/h",entropy = 'J / kgK' )
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

        #self.c10 = Connection(self.so1, "out1", self.fan, "in1", label="10")
        self.c11 = Connection(self.so1, "out1", self.ev, "in1", label="11")
        self.c12 = Connection(self.ev, "out1", self.si1, "in1", label="12")


        self.c21 = Connection(self.so2, "out1", self.cd, "in2", label="21")
        self.c22 = Connection(self.cd, "out2", self.si2, "in1", label="22")

        self.nwk.add_conns(self.c11, self.c12, self.c21, self.c22)


        ####################################################################
        # Calculate the design case for heating
        ####################################################################
        # set the parameters before and behind the compressor
        self.c1.set_attr(T=self.tamb_design - self.ttd_heat_exchanger)
        self.c3.set_attr(T=self.heating_system_feed_tenp + self.ttd_heat_exchanger) 

        # set the power and the compressor efficiencies 
        Q_design = self.heat_design
        self.cd.set_attr(Q=-100e3) # 100kW as a starting value

        #Charmap for turbocompressor performance
        map_eta1 = load_custom_char('map_eta1', CharMap)
        map_eta2 = load_custom_char('map_eta2', CharMap)
        map_pr1 = load_custom_char('map_pr1', CharMap)
        map_pr2 = load_custom_char('map_pr2', CharMap)

        # saves the char line plot
        map_pr1.plot(
                path="map_pr1.png",
                title="char Map Pr Compressor1",
                xlabel="Y",
                ylabel="Z"
        )
        map_eta1.plot(
                path="map_eta1.png",
                title="char Map eta Compressor1",
                xlabel="Y",
                ylabel="Z"
        )     
        map_eta2.plot(
                path="map_eta2.png",
                title="char Map eta Compressor2",
                xlabel="Y",
                ylabel="Z"
        )
        map_pr2.plot(
                path="map_pr2.png",
                title="char Map Pr Compressor2",
                xlabel="Y",
                ylabel="Z"
        )                     

        #Default charmaps using eta
        #self.cp1.set_attr(eta_s=self.eta_compressor1, design = ['eta_s'], offdesign = ['char_map_eta_s'], char_warnings = False)
        #self.cp2.set_attr(eta_s=self.eta_compressor2, design = ['eta_s'], offdesign = ['char_map_eta_s'], char_warnings = False)

        #Default charmaps using both eta and pr
        #self.cp1.set_attr(eta_s=self.eta_compressor1, design = ['eta_s'], offdesign = ['char_map_eta_s','char_map_pr'], char_warnings = False)
        #self.cp2.set_attr(eta_s=self.eta_compressor2, design = ['eta_s'], offdesign = ['char_map_eta_s','char_map_pr'], char_warnings = False)

        #Custom charmaps using eta
        #self.cp1.set_attr(eta_s=self.eta_compressor1, design = ['eta_s'],char_map_eta_s = {'char_func' : map_eta1},char_map_pr = {'char_func' : map_pr1}, offdesign = ['char_map_eta_s'])
        #self.cp2.set_attr(eta_s=self.eta_compressor2, design = ['eta_s'],char_map_eta_s = {'char_func' : map_eta2},char_map_pr = {'char_func' : map_pr2},offdesign = ['char_map_eta_s'])

        #Custom charmaps using pr
        #self.cp1.set_attr(eta_s=self.eta_compressor1, design = ['eta_s'],char_map_pr = {'char_func' : map_pr1}, offdesign = ['char_map_pr'])
        #self.cp2.set_attr(eta_s=self.eta_compressor2, design = ['eta_s'],char_map_pr = {'char_func' : map_pr2},offdesign = ['char_map_pr'])

        #Custom charmaps using both eta and pr
        self.cp1.set_attr(eta_s=self.eta_compressor1, design = ['eta_s'],char_map_eta_s = {'char_func' : map_eta1},char_map_pr = {'char_func' : map_pr1}, offdesign = ['char_map_eta_s','char_map_pr'])
        self.cp2.set_attr(eta_s=self.eta_compressor2, design = ['eta_s'],char_map_eta_s = {'char_func' : map_eta2},char_map_pr = {'char_func' : map_pr2},offdesign = ['char_map_eta_s','char_map_pr'])

        #Custom charmaps
        #self.cp1.set_attr(eta_s=self.eta_compressor1, design = ['eta_s'])
        #self.cp2.set_attr(eta_s=self.eta_compressor2, design = ['eta_s'])

        #set the fan efficiency
        #self.fan.set_attr(eta_s=self.eta_pump,pr=1.002)


        # set the connections around the hx
        self.c1.set_attr(fluid={self.working_fluid: 1}, x=1.0)
        self.c11.set_attr(fluid={ "Water": 1},  T=self.tamb_design,p=1)
        self.c12.set_attr(T=self.tamb_design - 3)
        self.c21.set_attr(fluid={ "Water": 1}, p=3.0, T=self.heating_system_return_temp)
        self.c22.set_attr(T=self.heating_system_feed_tenp)
        #hx elements 
        self.cd.set_attr(pr1=1, pr2=1) 
        self.c4.set_attr(td_bubble=15) # How to define this with real lab data 
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

        self.m1_design = self.c1.m.val
        self.m1_vals.append(self.m1_design)
        self.m2_design = self.c2a.m.val
        self.m2_vals.append(self.m2_design)

        self.t1_design = self.c1.T.val
        self.t2a_design = self.c2a.T.val

        # Get the design heat transfer coefficient to be used in offdesign case
        self.cond_UA_design = self.cd.UA.val # W/ K
        self.ev_kA_design = self.ev.kA.val


        self.nwk.save("data/process_data/hp_design_"+self.name+".json")

        
    def calc_partload_state(self, sink_temp_in:float=None,sink_temp_out:float=None, source_temp_in:float=None, source_temp_out:float=None, Q:float=None,
                            p_inter:float=None, p_evap:float=None, t_cond:float=None,sp_comp1:float=None,p_cond:float=None,t_subcooler:float=None,*,
                            igva1:float=None,igva2:float=None,eta1:float=None,eta2:float=None,cp1_real:float=None,cp2_real:float=None,k1:float=None,k2:float=None):
        """This function can calculate partload states of an heat pump with a calculated design state

        Args:
            temperature (float, optional): _description_. Defaults to None.
            Q (float, optional): _description_. Defaults to None.

        Returns:
            _type_: _description_
        """
        if source_temp_in != None:
            self.c11.set_attr(T=source_temp_in)
            self.c12.set_attr(T=source_temp_out)
        if Q != None:
            self.cd.set_attr(Q=-Q)  
        self.c7.set_attr(p=p_inter)    
        self.c21.set_attr(T=sink_temp_in)
        self.c22.set_attr(T=sink_temp_out)
        self.c1.set_attr(td_dew = sp_comp1,x=None)
        #self.c8.set_attr(p=p_evap)
        #self.c1.set_attr(T=self.t1_design,x=None)
        #self.cd.set_attr(ttd_u=None, UA = self.cond_UA_design)
        self.cd.set_attr(ttd_u=None,  UA = None)
        self.ev.set_attr(ttd_l=None)
        self.c3.set_attr(p=p_cond)
        self.t_cond_out = PropsSI("T", "P", self.c3.p.val*1e5, "Q", 0, self.working_fluid) - 273.15
        t_subcooling = self.t_cond_out-t_subcooler
        self.c4.set_attr(td_bubble=t_subcooling)

        #self.cp1.set_attr(igva=0)
        #self.cp2.set_attr(igva=0)

        #igva values from real compressor power simulation run
        #self.cp1.set_attr(igva=igva1)
        #self.cp2.set_attr(igva=igva2)

        self.cp1.set_attr(igva='var')
        self.cp2.set_attr(igva='var')

        #eta values from real compressor power simulation run
        #self.cp1.set_attr(eta_s=eta1)
        #self.cp2.set_attr(eta_s=eta2)

        #scaling factor
        #self.cp1.set_attr(eta_scale = k1)
        #self.cp2.set_attr(eta_scale = k2)

        #compressor power from real compressor power simulation run
        #self.cp1.set_attr(P=cp1_real*1e3)
        #self.cp2.set_attr(P=cp2_real*1e3)

        kA_char1 = ldc('HeatExchanger', 'kA_char1', 'DEFAULT', CharLine)
        kA_char2 = ldc('HeatExchanger', 'kA_char2', 'EVAPORATING FLUID', CharLine)
        
        line_ev = CharLine(
        x = [0.2521175208169838, 0.33220667111492613, 0.41229582141286847, 0.4923849717108108, 0.5724741220087531, 0.6525632723066954, 0.7326524226046378, 0.8127415729025801, 0.8928307232005225, 0.9729198734984649],
        y = [0.43643606753034203, 0.5039238958656511, 0.57141172420096, 0.6388995525362691, 0.706387380871578, 0.773875209206887, 0.8413630375421961, 0.908850865877505, 0.976338694212814, 1.0438265225481231]
        )
        #self.ev.set_attr(offdesign = ['kA_char'],kA_char1 = kA_char1, kA_char2=kA_char2) # Using default for hot fluid, evaporating fluid for cold fluid
        self.ev.set_attr(kA_char2 = {'char_func': line_ev},offdesign = ['kA_char']) # Using default for hot fluid, custom char line for cold fluid

        
        try:

            self.nwk.solve("offdesign",  design_path="data/process_data/hp_design_"+self.name+".json")
            self.nwk.assert_convergence()
            #self.nwk.print_results()
            cop = abs(self.cd.Q.val) / (self.cp1.P.val + self.cp2.P.val)
            cp1 = self.cp1.P.val 
            cp2 = self.cp2.P.val
            load = abs(self.cd.Q.val)
            T_evap = self.c1.T.val
            T_cond = self.c4.T.val
            T_delta = T_cond - T_evap
            eta1 = self.cp1.eta_s.val
            eta2 = self.cp2.eta_s.val
            ft_x = self.c5.x.val

            self.eta1_vals.append(self.cp1.eta_s.val)
            self.eta2_vals.append(self.cp2.eta_s.val)

            self.m1_vals.append(self.c1.m.val)
            self.m2_vals.append(self.c2a.m.val)

            m1=self.c1.m.val
            m2=self.c2a.m.val

            igva1 = self.cp1.igva.val
            igva2 = self.cp2.igva.val

            p1 = self.c1.p.val
            X= np.sqrt((self.t1_design + 273.15)/(self.c1.T.val+273.15))
            #print(f'speedline X Comp1 = {X}')
            x= np.sqrt((self.t2a_design + 273.15)/(self.c2a.T.val+273.15))
            #print(f'speedline X Comp2 = {x}')

            #print((self.c1.m.val * 1.9738605431888492)/(self.m1_design * self.c1.p.val * X))

            #Collect data for regression calibration
            self.x1.append({
                'Delta T' : self.c2.T.val - self.c1.T.val,
                'pr' : self.cp1.pr.val,
                'mdot' : self.c1.m.val
            })
            self.x2.append({
                'Delta T' : self.c3.T.val - self.c2a.T.val,
                'pr' : self.cp2.pr.val,
                'mdot' : self.c2a.m.val
            })

            #print("p_cond :",p_cond,"t_cond_out: ",t_cond_out,"t_subcooler :",t_subcooler, "t_subcooling :",t_subcooling,"c4_t :",self.c4.T.val )
            #print("Refrigerant input temp : ",self.c8.T.val, "Refrigerant output temp : ", self.c1.T.val,"Water in temp : ",self.c11.T.val,"Water out temp : ",self.c12.T.val)
            #print("Refrigerant coondensor input temp : ",self.c3.T.val, "Refrigerant condensor output temp : ", self.c4.T.val,"Sink Water in temp : ",self.c21.T.val,"Sink Water out temp : ",self.c22.T.val)
        except Exception as e:
            # mark as infeasible — record error and continue
            print(e)
            cop=None
            compressor_power=None
            load=None
            T_delta = None
            m_flow = 0
        return eta1,eta2,m1,m2,X,x,cop,cp1,cp2,igva1,igva2,p1


    def plot(self):
        diagram = FluidPropertyDiagram("R1234ZE")
        diagram.set_unit_system(T="°C", p="bar")
        diagram.set_isolines()
        diagram.calc_isolines()
        states = [self.c1, self.c2,self.c2a, self.c3, self.c4,self.c5,self.c6,self.c7,self.c8, self.c0]  # cycle order

        #Plot saturation lines of P-h and T-s diagram
        fluid = 'R1234ZE'

        # Generate temperature range for saturation (in Kelvin)
        T_sat = np.linspace(PropsSI('Tmin', fluid), PropsSI('Tcrit', fluid) , 300)

        # Saturation lines
        s_liq = [PropsSI('S', 'T', T, 'Q', 0, fluid) / 1000 for T in T_sat]  # kJ/kg·K
        s_vap = [PropsSI('S', 'T', T, 'Q', 1, fluid) / 1000 for T in T_sat]

        h_liq = [PropsSI('H', 'T', T, 'Q', 0, fluid) / 1000 for T in T_sat]  # kJ/kg
        h_vap = [PropsSI('H', 'T', T, 'Q', 1, fluid) / 1000 for T in T_sat]

        p_liq = [PropsSI('P', 'T', T, 'Q', 0, fluid) / 100000 for T in T_sat]  # bar
        p_vap = [PropsSI('P', 'T', T, 'Q', 1, fluid) / 100000 for T in T_sat]

        #Plot P-h and T-S diagrams

        T_vals = [c.T.val  for c in states] # degC
        s_vals = [c.s.val/1e3  for c in states] # J/kgK
        p_vals = [c.p.val  for c in states] # bar
        h_vals = [c.h.val  for c in states] #kJ/kg

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

        plt.plot(s_liq, T_sat - 273.15, 'r-', label='Saturation curve')
        plt.plot(s_vap, T_sat - 273.15, 'r-')
        plt.legend()

        plt.show()   # Shows in Window 1


        # ----------------- p-h Diagram -----------------
        plt.figure(figsize=(8, 5))
        plt.plot(h_vals, p_vals, marker='o', linestyle='-')
        plt.title('log p-h Diagram')
        plt.xlabel('Enthalpy [kJ/kg]')
        plt.ylabel('Pressure [bar]')
        plt.yscale('log')
        plt.grid(True, which='both', linestyle='--')

        plt.plot(h_liq, p_liq, 'r-', label='Saturation curve')
        plt.plot(h_vap, p_vap, 'r-')
        plt.legend()

        plt.show()    # Shows in Window 2

    def plot_eta_s(self):
        '''
        To plot the isentropic efficiency curve for the compressors in offdesign
        
        :param self: self
        '''
        fig,ax = plt.subplots(1, 2, figsize=(10, 4))
                              
        self.x1_vals = [m / self.m1_design for m in self.m1_vals]
        self.eta_ref1 = [e / self.eta_compressor for e in self.eta1_vals]

        #Adding the design case eta_s and x
        #self.x1_vals.append(1)
        #self.eta1_vals.append(self.eta_compressor)

        ax[0].plot(self.x1_vals,self.eta_ref1 ,'x')
        ax[0].set_xlabel('Mass flow / Design mass flow (x)')
        ax[0].set_ylabel('Relative isentropic efficiency (eta_s/ eta_s_design)')
        ax[0].grid(True)
        ax[0].set_title("Compressor 1")

        self.x2_vals = [m / self.m2_design for m in self.m2_vals]
        self.eta_ref2 = [e / self.eta_compressor for e in self.eta2_vals]

        #Adding the design case eta_s and x
        #self.x2_vals.append(1)
        #self.eta2_vals.append(self.eta_compressor)

        ax[1].plot(self.x2_vals,self.eta_ref2,'x')
        ax[1].set_xlabel('Mass flow / Design mass flow (x)')
        ax[1].set_ylabel('Relative isentropic efficiency (eta_s/ eta_s_design)')
        ax[1].grid(True)
        ax[1].set_title("Compressor 2")


        plt.tight_layout()
        plt.show()
    
    def plot2(self):
        diagram = FluidPropertyDiagram("R1234ZE")
        diagram.set_unit_system(T="°C", p="bar")
        diagram.set_isolines()
        diagram.calc_isolines()

        from tespy.tools import get_plotting_data
        processes, points = get_plotting_data(self.nwk, "5")
        processes = {
        key: diagram.calc_individual_isoline(**value)
        for key, value in processes.items()
        if value is not None
        }

        fig, ax = plt.subplots(1)
        diagram.draw_isolines(fig, ax, "Ts", 1000, 1800, 0, 120)
        for label, values in processes.items():
            _ = ax.plot(values["s"], values["T"], label=label, color="tab:red")
        for label, point in points.items():
            _ = ax.scatter(point["s"], point["T"], label=label, color="tab:red")
        plt.show()
    def get_plotting_states(self, **kwargs):
        """Generate data of states to plot in state diagram."""
        data = {}
        data.update(
            {self.cp1.label:
             self.cp1.get_plotting_data()[1]}
        )
        data.update(
            {self.cp2.label:
             self.cp2.get_plotting_data()[1]}
        )
        data.update(
            {self.cd.label:
             self.cd.get_plotting_data()[1]}
        )
        data.update(
            {self.va1.label:
             self.va1.get_plotting_data()[1]}
        )
        data.update(
            {self.sp.label + ' (hot)':
                self.sp.get_plotting_data()[2]}
        )
        data.update(
            {self.sp.label + ' (cold)':
                self.sp.get_plotting_data()[1]}
        )
        data.update(
            {'Injection steam': self.mg.get_plotting_data()[2]}
            )
        data.update(
            {'Compressed gas': self.mg.get_plotting_data()[1]}
            )
        data.update(
            {self.va2.label:
             self.va2.get_plotting_data()[1]}
        )
        data.update(
            {self.ev.label:
             self.ev.get_plotting_data()[2]}
        )

        
        for comp in data:
            if 'Compressor1' in comp:
                data[comp]['starting_point_value'] *= 0.999999
        
        return data
    def generate_state_diagram(self, refrig='', diagram_type='logph',
                               style='light', figsize=(16, 10), fontsize=10,
                               legend=True, legend_loc='upper left',
                               return_diagram=False, savefig=False,
                               open_file=False, filepath=None, **kwargs):
        """
        Generate log(p)-h-diagram of heat pump process.

        Parameters
        ----------

        refrig : str
            Name of refrigerant to use for plot. Can be left as an empty string
            in single cycle heat pumps.

        diagram_type : str
            Fluid property diagram type. Either 'logph' or 'Ts'. Default is
            'logph'.

        style : str
            Diagram style to chose. Either 'light' or 'dark'. Default is
            'light'.

        figsize : tuple/list of numbers
            Size of matplotlib figure in inches. Default is (16, 10), so the
            figure is 16 inches wide and 10 inches tall.

        fontsize : int/float
            Size of main fonts in points. Title is 20% larger and tick labels
            as well as state annotations are 10% smaller. Default is 10pts.

        legend : bool
            Flag to set if legend should be shown. Default is `True`.

        legend_loc : str
            Location to place legend to. Accepts options as matplotlib allows.
            Default is 'upper left'. Is only used if 'legend' parameter is set
            to `True`.

        return_diagram : bool
            Flag to set if diagram object should be returned by method. Default
            is False.

        savefig : bool
            Flag to set if diagram should be saved to disk. Default is `False`.

        filepath : str
            Path to save the file to. If `None` and `savefig` is `True`, a
            default name is given and saved to the current working directory.
            Default is `None`.

        open_file : bool
            Flag to set if saved file should be opend by the os. Default is
            `False`.

        **kwargs
            Additional keyword arguments to pass through to the
            `get_plotting_states` method of the heat pump class.
        """
        if not refrig:
            #refrig = self.params['setup']['refrig']
            refrig = "R1234ZE"
        # Define axis and isoline state variables
        if diagram_type == 'logph':
            var = {'x': 'h', 'y': 'p', 'isolines': ['T', 's']}
        elif diagram_type == 'Ts':
            var = {'x': 's', 'y': 'T', 'isolines': ['h', 'p']}
        else:
            print(
                'Parameter "diagram_type" has to be set correctly. Valid '
                + 'diagram types are "logph" and "Ts".'
                )
            return

        # Get plotting state data
        result_dict = self.get_plotting_states(**kwargs)
        if len(result_dict) == 0:
            print(
                "'get_plotting_states'-method of heat pump "
                + f"'{self.params['setup']['type']}' seems to not be implemented."
                )
            return

        if style == 'light':
            plt.style.use('default')
            isoline_data = None
        elif style == 'dark':
            plt.style.use('dark_background')
            isoline_data = {
                'T': {'style': {'color': 'dimgrey'}},
                'v': {'style': {'color': 'dimgrey'}},
                'Q': {'style': {'color': '#FFFFFF'}},
                'h': {'style': {'color': 'dimgrey'}},
                'p': {'style': {'color': 'dimgrey'}},
                's': {'style': {'color': 'dimgrey'}}
            }

        # Initialize fluid property diagram
        fig, ax = plt.subplots(figsize=figsize)

        diagram_data_path = os.path.abspath(os.path.join(
            os.path.dirname(__file__), 'input', 'diagrams', f"{refrig}.json"
        ))

        # Generate isolines
        path = os.path.abspath(os.path.join(
            os.path.dirname(__file__), 'input', 'state_diagram_config.json'
            ))
        with open(path, 'r', encoding='utf-8') as file:
            config = json.load(file)

        if refrig in config:
            state_props = config[refrig]
        else:
            state_props = config['MISC']

        if os.path.isfile(diagram_data_path):
            diagram = FluidPropertyDiagram.from_json(diagram_data_path)
        else:
            diagram = FluidPropertyDiagram(refrig)
            diagram.set_unit_system(T='°C', p='bar', h='kJ/kg')

            iso1 = np.arange(
                state_props[var['isolines'][0]]['isorange_low'],
                state_props[var['isolines'][0]]['isorange_high'],
                state_props[var['isolines'][0]]['isorange_step']
                )
            iso2 = np.arange(
                state_props[var['isolines'][1]]['isorange_low'],
                state_props[var['isolines'][1]]['isorange_high'],
                state_props[var['isolines'][1]]['isorange_step']
                )

            diagram.set_isolines(**{
                var['isolines'][0]: iso1,
                var['isolines'][1]: iso2
                })
            diagram.calc_isolines()
            diagram.to_json(diagram_data_path)


        # Calculate components process data
        for compdata in result_dict.values():
            compdata['datapoints'] = (
                diagram.calc_individual_isoline(**compdata)
            )
        diagram.fig = fig
        diagram.ax = ax

        # Set axes limits
        if 'xlims' in kwargs:
            xlims = kwargs['xlims']
        else:
            xlims = (
                state_props[var['x']]['min'], state_props[var['x']]['max']
                )
        if 'ylims' in kwargs:
            ylims = kwargs['ylims']
        else:
            ylims = (
                state_props[var['y']]['min'], state_props[var['y']]['max']
                )

        diagram.draw_isolines(
            diagram_type=diagram_type, fig=fig, ax=ax,
            x_min=xlims[0], x_max=xlims[1], y_min=ylims[0], y_max=ylims[1],
            isoline_data=isoline_data
            )

        # Draw heat pump process over fluid property diagram
        for i, key in enumerate(result_dict.keys()):
            datapoints = result_dict[key]['datapoints']
            has_xvals = len(datapoints[var['x']]) > 0
            has_yvals = len(datapoints[var['y']]) > 0
            if has_xvals and has_yvals:
                ax.plot(
                    datapoints[var['x']][:], datapoints[var['y']][:],
                    color='#EC6707'
                    )
                ax.scatter(
                    datapoints[var['x']][0], datapoints[var['y']][0],
                    color='#B54036',
                    label=f'$\\bf{i+1:.0f}$: {key}',
                    s=14*int(fontsize*0.9), alpha=0.5
                    )
                ax.annotate(
                    f'{i+1:.0f}',
                    (datapoints[var['x']][0], datapoints[var['y']][0]),
                    ha='center', va='center', color='w',
                    fontsize=int(fontsize*0.9)
                    )
            else:
                ax.scatter(
                    0, 0,
                    color='#FFFFFF', s=0, alpha=1.0,
                    label=f'$\\bf{i+1:.0f}$: {key}'
                    )
                ax.annotate(
                    'Error\nMissing Plotting Data', (0.5, 0.5),
                    xycoords='axes fraction', ha='center', va='center',
                    fontsize=60, color='#B54036'
                    )

        # Additional plotting parameters
        ax.set_title(refrig, fontsize=int(fontsize*1.2))
        if diagram_type == 'logph':
            ax.set_xlabel('Specific Enthalpy in $kJ/kg$', fontsize=fontsize)
            ax.set_ylabel('Pressure in $bar$', fontsize=fontsize)
        elif diagram_type == 'Ts':
            ax.set_xlabel('Specific Entropy in $J/(kg \\cdot K)$', fontsize=fontsize)
            ax.set_ylabel('Temperature in $°C$', fontsize=fontsize)

        ax.tick_params(axis='both', labelsize=int(fontsize*0.9))

        if legend:
            ax.legend(
                loc=legend_loc,
                prop={'size': fontsize * (1 - 0.02 * len(result_dict))},
                markerscale=(1 - 0.02 * len(result_dict))
                )

        if savefig:
            if filepath is None:
                filename = (
                    f'{diagram_type}_{refrig}.png'
                    )
                filepath = os.path.abspath(os.path.join(
                    os.getcwd(), filename
                    ))

            plt.tight_layout()
            plt.savefig(filepath, dpi=300)

            if open_file:
                os.startfile(filepath)

        if return_diagram:
            return diagram
        plt.close()
    def generate_temp_plot(self):

        N = 10
        T_ref_in  = self.c3.T.val
        T_ref_out = self.c4.T.val

        T_w_in  = self.c21.T.val
        T_w_out = self.c22.T.val
        T_w = np.linspace(T_w_out, T_w_in, 20)

        Q_total = abs(self.cd.Q.val)/1e6

        # Desuperheating, condensation, subcooling
        T_sat = self.t_cond_out
        T_ref_desup = np.linspace(T_ref_in, T_sat, 5)
        T_ref_cond = np.ones(10) * T_sat
        T_ref_sub = np.linspace(T_sat, T_ref_out, 5)
        T_ref = np.concatenate([T_ref_desup, T_ref_cond, T_ref_sub])

        x = np.linspace(0, Q_total, len(T_ref))
        
        # Create main figure
        fig, ax1 = plt.subplots(figsize=(8,5))
        
        # Left y-axis: refrigerant
        ax1.plot(x, T_ref, 'r-', label='Refrigerant')
        ax1.set_xlabel('Heat Transfer at Condensor [MW]')
        ax1.set_ylabel('Refrigerant Temperature at Condensor [°C]', color='r')
        ax1.tick_params(axis='y', labelcolor='r')
        ax1.grid(True)
        
        # Right y-axis: water
        ax2 = ax1.twinx()  # create a twin y-axis
        ax2.plot(x, T_w, 'b--', label='District water at sink')
        ax2.set_ylabel('Water Temperature [°C]', color='b')
        ax2.tick_params(axis='y', labelcolor='b')

        # Make both y-axes share the same scale
        y_min = min(T_ref.min(), T_w.min())
        y_max = max(T_ref.max(), T_w.max())
        ax1.set_ylim(y_min-10, y_max+10)
        ax2.set_ylim(y_min-10, y_max+10)
        
        # Optional: combine legends
        lines_1, labels_1 = ax1.get_legend_handles_labels()
        lines_2, labels_2 = ax2.get_legend_handles_labels()
        ax1.legend(lines_1 + lines_2, labels_1 + labels_2, loc='best')

        t_ref_in  = self.c8.T.val
        t_ref_out = self.c1.T.val
        t_ref_ev = np.ones(15) * t_ref_in
        t_ref_she = np.linspace(t_ref_out,t_ref_in ,5)
        t_ref = np.concatenate([t_ref_she,t_ref_ev])

        t_w_in  = self.c11.T.val
        t_w_out = self.c12.T.val

        t_w = np.linspace(t_w_in, t_w_out, 20)

        Q_ev = self.c8.m.val * (self.c1.h.val - self.c8.h.val) / 1e3 # in MW

        x1 = np.linspace(0, Q_ev, 20)

        # Create main figure
        fig, ax3 = plt.subplots(figsize=(8,5))
        
        # Left y-axis: refrigerant
        ax3.plot(x1, t_ref, 'r-', label='Refrigerant')
        ax3.set_xlabel('Heat Input at evaporator [MW]')
        ax3.set_ylabel('Refrigerant Temperature at evaporator [°C]', color='r')
        ax3.tick_params(axis='y', labelcolor='r')
        ax3.grid(True)
        
        # Right y-axis: water
        ax4 = ax3.twinx()  # create a twin y-axis
        ax4.plot(x1, t_w, 'b--', label='River water at source')
        ax4.set_ylabel('Water Temperature [°C]', color='b')
        ax4.tick_params(axis='y', labelcolor='b')

        # Make both y-axes share the same scale
        Y_min = min(t_ref.min(), t_w.min())
        Y_max = max(t_ref.max(), t_w.max())
        ax3.set_ylim(Y_min-10, Y_max+10)
        ax4.set_ylim(Y_min-10, Y_max+10)

        # Optional: combine legends
        lines_3, labels_3 = ax3.get_legend_handles_labels()
        lines_4, labels_4 = ax4.get_legend_handles_labels()
        ax3.legend(lines_3 + lines_4, labels_3 + labels_4, loc='best')
        
        heat, T_hot, T_cold, heat_section, td_log = self.cd.calc_sections()
        print(T_cold-273.15)
        plt.savefig("evaporator_temperature_profile.png", dpi=300, bbox_inches="tight")
        plt.show()
    def generate_temp_plot2(self):
        heat, T_hot, T_cold, heat_section, td_log = self.cd.calc_sections()

        fig, ax = plt.subplots(figsize=(8,5))
        ax.plot(heat/1e6, T_hot-273.15, label = 'Refrigerant')
        ax.plot(heat/1e6, T_cold-273.15, label = 'District Water')
        ax.set_xlabel('Heat Transfer at Condensor [MW]')
        ax.set_ylabel('Temperature at Condensor [°C]')
        ax.legend()
        plt.grid()
        plt.savefig("condenser_temperature_profile.png", dpi=300, bbox_inches="tight")
        plt.show()


if __name__ == "__main__":
    # Define the parameters dictionary
    params_hp = {
        "name": "HeatPump",
        "working_fluid": "R1234ZE",
        "cooling_mode #not implemented": False,
        "eta_compressor": 0.92,
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
