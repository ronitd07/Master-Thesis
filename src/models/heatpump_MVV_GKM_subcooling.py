
"""
heat pump model of MVV GKM Manheim with subcooling

"""
from tespy.components import CycleCloser, Compressor, Valve, HeatExchanger, Source, Sink, Condenser, Pump ,Splitter,DropletSeparator, Merge, Drum,MovingBoundaryHeatExchanger
from tespy.tools.characteristics import CharLine
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
        self.c4.set_attr(T=self.heating_system_feed_tenp + self.ttd_heat_exchanger) 

        # set the power and the compressor efficiencies 
        Q_design = self.heat_design
        self.cd.set_attr(Q=-100e3) # 100kW as a starting value

        #Charline for compressor performance
        self.eta_char = CharLine(
        x=[1.0, 1.5, 2.0, 3.0],     # pressure ratio
        y=[0.78, 0.75, 0.70, 0.62] # isentropic efficiency
        )
        gen_char = load_custom_char('eta_s_test', CharLine)
        self.cp1.set_attr(eta_s=self.eta_compressor, design=['eta_s'], offdesign = ['eta_s_test'])
        self.cp2.set_attr(eta_s=self.eta_compressor, design=['eta_s'], offdesign = ['eta_s_test'])

        #self.cp1.set_attr(eta_s=self.eta_compressor,design=['eta_s'], offdesign=['char_map_pr','char_map_eta_s'] )
        self.eta1_vals.append(self.eta_compressor)

        #self.cp2.set_attr(eta_s=self.eta_compressor,design=['eta_s'], offdesign=['char_map_pr','char_map_eta_s'])
        self.eta2_vals.append(self.eta_compressor)

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
        self.c4.set_attr(td_bubble=15) # How to define this with real lab data 
        self.ev.set_attr(pr1=1, pr2=0.995)
      
        #self.sp.set_attr(split=[0.6, 0.4])  # fraction of mass to out1/out2
        #self.c7.set_attr(p=Ref(self.c4,1,-10))
        self.c7.set_attr(p=10)
        self.c5.set_attr(fluid={self.working_fluid: 1})
        #self.c1.set_attr(m=170)
        try:

            #solve the design case
            self.nwk.solve("design",print_results=True)
            #print("Refrigerant temp : ",self.c0.T.val, "Water in temp : ", self.c11.T.val, "Water out temp : " ,self.c12.T.val)
        except ValueError as e:
            print(e)


        #vary heat exchanger efficiency
        self.ev.set_attr(ttd_l=self.ttd_heat_exchanger)
        self.c1.set_attr(T=None)
        self.cd.set_attr(ttd_u=self.ttd_heat_exchanger)
        self.c4.set_attr(T=None)
        self.cd.set_attr(Q=-Q_design) #
        #save data
        self.nwk.solve("design")
        self.nwk.print_results()

        self.m1_design = self.c1.m.val
        self.m1_vals.append(self.m1_design)
        self.m2_design = self.c2a.m.val
        self.m2_vals.append(self.m2_design)


        # Get the design heat transfer coefficient to be used in offdesign case
        self.cond_UA_design = self.cd.UA.val # W/ K
        self.ev_kA_design = self.ev.kA.val


        self.nwk.save("data/process_data/hp_design_"+self.name+".json")

        
    def calc_partload_state(self, sink_temp_in:float=None,sink_temp_out:float=None, source_temp_in:float=None, source_temp_out:float=None, Q:float=None,p_inter:float=None, t_evap:float=None, t_cond:float=None,sp_comp1:float=None,p_cond:float=None,t_subcooler:float=None):
        """This function can calculate partload states of an heat pump with a calculated design state

        Args:
            temperature (float, optional): _description_. Defaults to None.
            Q (float, optional): _description_. Defaults to None.

        Returns:
            _type_: _description_
        """
        if source_temp_in != None:
            self.c10.set_attr(T=source_temp_in)
            self.c12.set_attr(T=source_temp_out)
        if Q != None:
            self.cd.set_attr(Q=-Q)  
        self.c7.set_attr(p=p_inter)    
        self.c21.set_attr(T=sink_temp_in)
        self.c22.set_attr(T=sink_temp_out)
        self.c1.set_attr(td_dew = sp_comp1,x=None)
        #self.cd.set_attr(ttd_u=None, UA = self.cond_UA_design)
        self.cd.set_attr(ttd_u=None)
        self.ev.set_attr(ttd_l=None, kA = self.ev_kA_design)
        self.c3.set_attr(T=t_cond)
        t_cond_out = PropsSI("T", "P", p_cond*1e5, "Q", 0, self.working_fluid) - 273.15
        t_subcooling = t_cond_out-t_subcooler
        self.c4.set_attr(td_bubble=t_subcooling-10)
        #self.cp1.set_attr(eta_s=None, offdesign=['eta_s_char'])
        #self.cp2.set_attr(eta_s=None,offdesign=['eta_s_char'])
        # After design solves in partload_heat_pump()

        # Freeze the actual design areas for offdesign
        #self.ev.set_attr(kA=1.5*self.ev.kA.val)
        #self.cd.set_attr(kA=1.5*self.cd.kA.val)
        
        try:

            self.nwk.solve("offdesign", design_path="data/process_data/hp_design_"+self.name+".json")
            self.nwk.print_results()
            self.nwk.save('results.csv')
            cop = abs(self.cd.Q.val) / (self.cp1.P.val + self.cp2.P.val + self.fan.P.val )
            compressor_power = self.cp1.P.val + self.cp2.P.val 
            load = abs(self.cd.Q.val)
            T_evap = self.c1.T.val
            T_cond = self.c4.T.val
            T_delta = T_cond - T_evap
            ft_x = self.c5.x.val

            self.eta1_vals.append(self.cp1.eta_s.val)
            self.eta2_vals.append(self.cp2.eta_s.val)

            self.m1_vals.append(self.c1.m.val)
            self.m2_vals.append(self.c2a.m.val)

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
        return cop, compressor_power,load,T_delta,ft_x

   
    def step(self, sink_temp_in:float,sink_temp_out:float, source_temp_in:float,source_temp_out:float, Q:float, p_inter:float,t_evap:float,t_cond:float,sp_comp1:float,p_cond:float,t_subcooler:float,cooling:bool=False):
        """This function takes one step in the heatpump simulation and returns the values

        Args:
            Q (float): _description_
            ambient_temperature (float): _description_
            cooling (bool, optional): _description_. Defaults to False.

        Returns:
            _type_: _description_
        """
        if cooling == False:
            cop, power,load,T_delta,ft_x = self.calc_partload_state(sink_temp_in,sink_temp_out, source_temp_in,source_temp_out, Q, p_inter, t_evap,t_cond,sp_comp1,p_cond,t_subcooler)
        else:
            cop, power = self.calc_partload_state_cooling(source_temp_in, sink_temp_out,Q)
        return cop, power,load,T_delta,ft_x
    def evap_outlet_temperature(self):
        return self.c12.T.val 
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
                    f'{diagram_type}_{refrig}.pdf'
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
