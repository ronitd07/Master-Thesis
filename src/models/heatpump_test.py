from tespy.components import (
    Compressor, Condenser, HeatExchanger, Valve, Separator, Source, Sink
)
from tespy.connections import Connection, Ref
from tespy.networks import Network

# ------------------------------
# 1. Network setup
# ------------------------------
nw = Network(fluids=['R134a'], p_unit='bar', T_unit='C', h_unit='kJ / kg')

# ------------------------------
# 2. Components
# ------------------------------
# Heat pump components
c1 = Compressor('Low-stage compressor')
c2 = Compressor('High-stage compressor')
cd = Condenser('Condenser')
v1 = Valve('High-pressure valve')   # condenser → flash tank
sp = Separator('Flash tank')
v2 = Valve('Low-pressure valve')    # flash tank → evaporator
ev = HeatExchanger('Evaporator')

# Source & sink for boundary conditions
hso_in = Source('Heat source in')
hso_out = Sink('Heat source out')
hs_in = Source('Heat sink in')
hs_out = Sink('Heat sink out')

# ------------------------------
# 3. Connections
# ------------------------------
# Evaporator → Low-stage compressor
c01 = Connection(hso_in, 'out1', ev, 'in1')
c02 = Connection(ev, 'out1', c1, 'in1')

# Low-stage compressor → flash tank vapor line
c03 = Connection(c1, 'out1', sp, 'in1')

# Vapor outlet from flash tank → High-stage compressor
c04 = Connection(sp, 'out2', c2, 'in1')

# High-stage compressor → condenser
c05 = Connection(c2, 'out1', cd, 'in1')

# Condenser → HP valve → flash tank (liquid line)
c06 = Connection(cd, 'out1', v1, 'in1')
c07 = Connection(v1, 'out1', sp, 'in1')

# Flash tank liquid outlet → LP valve → evaporator
c08 = Connection(sp, 'out1', v2, 'in1')
c09 = Connection(v2, 'out1', ev, 'in2')

# Condenser outlet to sink
c10 = Connection(cd, 'out2', hs_out, 'in1')
c11 = Connection(hs_in, 'out1', cd, 'in2')

# Add all connections
nw.add_conns(c01, c02, c03, c04, c05, c06, c07, c08, c09, c10, c11)

# Connections
c_hs_in = Connection(hs_in, 'out1', cd, 'in2')
c_hs_out = Connection(cd, 'out2', hs_out, 'in1')

# Connections
c_hso_in = Connection(hso_in, 'out1', ev, 'in1')
c_hso_out = Connection(ev, 'out2', hso_out, 'in1')

# ------------------------------
# 4. Boundary conditions
# ------------------------------

# Define pressures
c02.set_attr(p=5)    # Low pressure (evaporator outlet)
c05.set_attr(p=25)   # High pressure (discharge of 2nd compressor)

# Set phase conditions at separator
c04.set_attr(x=1.0)  # vapor to high stage compressor
c08.set_attr(x=0.0)  # liquid to low pressure valve

# Compressor efficiencies
c1.set_attr(eta_s=0.75)
c2.set_attr(eta_s=0.75)

# Heat sink and source temperatures
c_hs_in.set_attr(T=30)
c_hs_out.set_attr(T=40)
c_hso_in.set_attr(T=0)
c_hso_out.set_attr(T=-5)

# Evaporator and condenser energy flows
ev.set_attr(pr=0.99)
cd.set_attr(pr=0.99)

# Valves – let TESPy calculate pressure drop & mass flow
v1.set_attr()  # HP valve (auto-determined)
v2.set_attr()  # LP valve (auto-determined)

# Flash tank (separator)
sp.set_attr(pr=1.0)  # negligible pressure drop

# ------------------------------
# 5. Solve network
# ------------------------------
nw.solve('design')
nw.print_results()
